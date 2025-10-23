"""
csv_service.py
---------------
Handles CSV upload, summary generation, and Gemini-based data analysis.
"""

from http.client import HTTPException
import pandas as pd
import os
from io import StringIO
from services.gemini_service import get_model
from fastapi import UploadFile
import requests
import numpy as np

# Supported file extensions and content types
ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
ALLOWED_CONTENT_TYPES = {"text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}

MAX_CSV_SIZE = 50 * 1024 * 1024

def save_uploaded_csv(file: UploadFile, content_bytes: bytes) -> str:
    """
    Save uploaded CSV to processed folder.

    Args:
        file (UploadFile): Uploaded CSV file.
        content_bytes (bytes): Pre-read content of the file.

    Returns:
        str: Path to saved CSV.
    """
    if len(content_bytes) > MAX_CSV_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {MAX_CSV_SIZE / (1024 * 1024)} MB.")
    try:
        os.makedirs("data/processed", exist_ok=True)
        file_path = f"data/processed/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(content_bytes)
        return file_path
    except Exception as e:
        raise Exception(f"Failed to save CSV: {e}")

def download_csv_from_url(url: str) -> str:
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.Timeout:
        raise HTTPException(status_code=400, detail="Request to download CSV timed out.")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to download CSV: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download CSV: {e}")

def summarize_csv(file_content: str) -> str:
    """
    Create a simple textual summary of a CSV file using pandas.

    Args:
        file_content (str): Raw CSV content as a string.

    Returns:
        str: Summary including shape, columns, and missing values.
    """
    try:
        df = pd.read_csv(StringIO(file_content), encoding='utf-8-sig')
        if df.empty:
            return "❌ CSV file trống hoặc không có dữ liệu hợp lệ."
        
        summary = f"Dataset shape: {df.shape}\n"
        summary += f"Columns: {', '.join(df.columns)}\n"
        summary += "\nColumn types:\n" + str(df.dtypes) + "\n"
        summary += "\nMissing values per column:\n" + str(df.isna().sum()) + "\n"

        numeric_cols = df.select_dtypes(include='number')
        if not numeric_cols.empty:
            summary += "\nStatistics for numeric columns:\n" + str(numeric_cols.describe()) + "\n"

        object_cols = df.select_dtypes(include='object')
        for col in object_cols.columns:
            summary += f"\nTop values for {col}:\n{df[col].value_counts().head(3)}\n"
        
        return summary
    except pd.errors.EmptyDataError:
        return "❌ Failed to summarize CSV: No columns to parse from file"
    except Exception as e:
        return f"❌ Failed to summarize CSV: {str(e)}"

def generate_histogram_data(file_content: str, column: str) -> dict:
    """
    Generate histogram data for a specified numeric column in the CSV.

    Args:
        file_content (str): Raw CSV content as a string.
        column (str): Name of the column to generate histogram for.

    Returns:
        dict: Histogram data with bins and counts, or error message.
    """
    try:
        df = pd.read_csv(StringIO(file_content), encoding='utf-8-sig')
        if df.empty:
            return {"error": "CSV file is empty or contains no valid data."}
        
        # Find column case-insensitively
        column_lower = column.lower()
        matching_column = next((col for col in df.columns if col.lower() == column_lower), None)
        if matching_column is None:
            return {"error": f"Column '{column}' not found in CSV."}
        
        if not pd.api.types.is_numeric_dtype(df[matching_column]):
            return {"error": f"Column '{matching_column}' is not numeric."}
        
        # Calculate histogram
        hist, bins = np.histogram(df[matching_column].dropna(), bins=10)
        return {
            "column": matching_column,
            "bins": bins.tolist(),
            "counts": hist.tolist()
        }
    except pd.errors.EmptyDataError:
        return {"error": "No columns to parse from file."}
    except Exception as e:
        return {"error": f"Failed to generate histogram: {str(e)}"}

def ask_gemini_about_data(prompt: str, csv_summary: str, file_name: str = None) -> str:
    """
    Ask Gemini to analyze or summarize a dataset based on user input.

    Args:
        prompt (str): User's question about the dataset.
        csv_summary (str): Pre-processed summary of the CSV data.

    Returns:
        str: Gemini's analytical response about the dataset.
    """
    try:
        model = get_model()
        
        # ✅ PROMPT MỚI - BẮT BUỘC THAM CHIẾU FILE!
        file_reference = f"File: **{file_name}**" if file_name else "Uploaded CSV file"
        full_prompt = f"""
                        **ANALYZE THE FOLLOWING CSV FILE: {file_reference}**

                        User Question: {prompt}

                        Dataset Summary from {file_name or 'CSV file'}:
                        {csv_summary or 'No data summary provided.'}

                        **IMPORTANT: In your answer, ALWAYS reference the file "{file_name or 'CSV file'}" specifically. 
                        Mention the file name when explaining results, trends, or insights.**

                        Provide detailed analysis based on the data.
                        """
        
        response = model.generate_content(full_prompt)
        return response.text.strip() if response and response.text else f"(No response from Gemini about {file_name})"
        
    except Exception as e:
        print(f"[CSVService] Data query failed: {e}")
        return f"❌ Error analyzing **{file_name}**: {e}"


async def ask_gemini_about_data_streaming(prompt: str, csv_summary: str, file_name: str = None):
    """
    Streaming version - TƯƠNG TỰ!
    """
    try:
        model = get_model()
        
        file_reference = f"File: **{file_name}**" if file_name else "Uploaded CSV file"
        full_prompt = f"""
                        **ANALYZE THE FOLLOWING CSV FILE: {file_reference}**

                        User Question: {prompt}

                        Dataset Summary from {file_name or 'CSV file'}:
                        {csv_summary or 'No data summary provided.'}

                        **IMPORTANT: In your answer, ALWAYS reference the file "{file_name or 'CSV file'}" specifically. 
                        Mention the file name when explaining results, trends, or insights.**

                        Provide detailed analysis based on the data.
                        """
        
        response = model.generate_content(full_prompt, stream=True)
        full_text = ""
        
        for chunk in response:
            if chunk.text:
                text = chunk.text
                full_text += text
                yield text 
                
        if full_text.strip():
            yield full_text.strip()
            
    except Exception as e:
        print(f"[CSVService] Streaming failed: {e}")
        yield f"❌ Error analyzing **{file_name}**: {e}"
        
    except Exception as e:
        print(f"[CSVService] Streaming failed: {e}")
        yield f"❌ Error analyzing **{file_name}**: {e}"