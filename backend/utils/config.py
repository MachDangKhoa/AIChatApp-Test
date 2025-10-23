"""
config.py
----------
Utility for loading environment variables and configuring global settings.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Retrieve Gemini API key from environment
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "")

if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in environment variables.")
if not GEMINI_MODEL:
    raise ValueError("❌ GEMINI_MODEL not found in environment variables.")
