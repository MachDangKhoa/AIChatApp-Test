🤖 AI Chat Application - Gemini AI Powered

![AI Chat Assistant](https://img.shields.io/badge/AI-Chat%2520Assistant-blue)
![Multi-Modal](https://img.shields.io/badge/Multi--Modal-Text%252C%2520Image%252C%2520CSV-green)
![Real-Time Streaming](https://img.shields.io/badge/Real--Time-Streaming-orange)
![Node.js](https://img.shields.io/badge/Node.js-v22.14.0-green)
![Python](https://img.shields.io/badge/Python-3.10%252B-blue)

Ứng dụng chat AI đa phương thức hỗ trợ tương tác với văn bản, hình ảnh và file CSV. Được xây dựng với FastAPI backend và React frontend, tích hợp Google Gemini AI.


🎥 Demo Video
https://drive.google.com/file/d/1_M6h39QJVYQMdH4mORqtaPOpO0GTWKVo/view?usp=drive_link

Video demo các tính năng chính của ứng dụng


✨ Tính Năng Nổi Bật
💬 Chat đa phương thức: Text, Image, CSV

🚀 Streaming real-time: Phản hồi nhanh với hiệu ứng typing

📊 Phân tích CSV: Thống kê, biểu đồ, histogram

🖼️ Xử lý ảnh thông minh: Phân tích và mô tả hình ảnh

🎨 Giao diện hiện đại: Thiết kế responsive, gradient đẹp mắt

⚡ Performance tốt: FastAPI + Vite cho tốc độ tối ưu


🏗️ Cấu Trúc Dự Án
text
Test_Chatbot/
├── 🐍 backend/                 # FastAPI Backend
│   ├── main.py                 # Điểm vào chính
│   ├── routers/                # API Routes
│   │   ├── chat_router.py      # Chat văn bản
│   │   ├── image_router.py     # Chat với ảnh
│   │   └── csv_router.py       # Chat với CSV
│   ├── services/               # Business Logic
│   │   ├── gemini_service.py   # Gemini AI integration
│   │   ├── image_service.py    # Xử lý ảnh
│   │   └── csv_service.py      # Phân tích CSV
│   ├── models/                 # Data schemas
│   │   └── schemas.py          # Pydantic models
│   ├── utils/                  # Utilities
│   │   └── config.py           # Configuration
│   ├── data/                   # Data storage
│   │   ├── temp_uploads/       # File uploads
│   │   └── processed/          # Processed files
│   └── requirements.txt        # Python dependencies
│
├── ⚛️ frontend/                # React Frontend
│   ├── src/
│   │   ├── components/         # React Components
│   │   │   ├── ChatBox.jsx     # Main chat interface
│   │   │   ├── MessageBubble.jsx # Message display
│   │   │   └── LoadingIndicator.jsx # Loading states
│   │   ├── pages/              # App Pages
│   │   │   └── ChatPage.jsx    # Main chat page
│   │   ├── services/           # API Services
│   │   │   └── chatAPI.js      # Backend communication
│   │   ├── App.jsx             # Root component
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Styling
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
│
└── 📚 README.md               # Project documentation


🚀 Hướng Dẫn Chạy Ứng Dụng
📋 Điều Kiện Tiên Quyết
Python 3.10+ (Đã xác nhận tương thích)

Node.js v22.14.0 (Đã xác nhận tương thích)

Google Gemini API Key (Lấy tại đây)

🔧 Cài Đặt Backend (Python 3.10+)
Clone repository

bash
git clone <repository-url>
cd Test_Chatbot/backend
Tạo virtual environment (Python 3.10+)

bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
Kiểm tra Python version

bash
python --version
# Python 3.10.x hoặc cao hơn
Cài đặt dependencies

bash
pip install --upgrade pip
pip install -r requirements.txt
Cấu hình environment

bash
cp .env.example .env
# Chỉnh sửa .env và thêm API key
GEMINI_API_KEY=your_actual_gemini_api_key_here
Chạy backend server

bash
python main.py
Backend sẽ chạy tại: http://localhost:8000

⚛️ Cài Đặt Frontend (Node.js v22.14.0)
Mở terminal mới và vào thư mục frontend

bash
cd Test_Chatbot/frontend
Kiểm tra Node.js version

bash
node --version
# v22.14.0
npm --version
# 10.x.x
Cài đặt dependencies với Node.js v22.14.0

bash
npm install
# Hoặc nếu gặp lỗi permission
npm install --legacy-peer-deps
Cấu hình environment (tuỳ chọn)

bash
cp .env.example .env
# Chỉnh sửa nếu backend chạy port khác
VITE_BACKEND_URL=http://localhost:8000
Chạy development server

bash
npm run dev
Frontend sẽ chạy tại: http://localhost:5173

🌐 Truy Cập Ứng Dụng
Mở browser và truy cập: http://localhost:5173


🎯 Hướng Dẫn Sử Dụng
💬 Chat Văn Bản
 •	Nhập câu hỏi vào ô text và nhấn Send

 •	Hỗ trợ markdown trong câu trả lời

 •	Lịch sử chat được lưu tự động

 •	Xử lý trạng thái tải/streaming mượt mà

🖼️ Chat Với Ảnh
 •	Click nút "📷 Image"

 •	Chọn file ảnh (PNG, JPEG)

 •	Nhập câu hỏi về ảnh

 •	Nhấn Send

 •	Câu trả lời của trợ lý phải tham chiếu rõ ràng đến hình ảnh đã tải lên.

📊 Chat Với CSV
Cách 1: Upload file

 •	Click nút "📄 CSV"

 •	Chọn file CSV

 •	Đặt câu hỏi về dữ liệu

Cách 2: URL

 •	Dán URL CSV vào ô "Or paste CSV URL"

 •	Đặt câu hỏi phân tích

Tính năng CSV:

 •	Thống kê mô tả

 •	Biểu đồ histogram

 •	Phân tích xu hướng

 •	Preview dữ liệu

🔧 API Endpoints
Method	Endpoint	Mô Tả
POST	/api/chat/text	Chat văn bản thông thường
POST	/api/chat/image	Chat với ảnh upload
POST	/api/chat/csv	Chat với file CSV
GET	/docs	API Documentation (Swagger)

🛠️ Công Nghệ Sử Dụng
Backend (Python 3.10+)
FastAPI - Modern Python web framework

Google Gemini AI - Multi-modal AI model

Pydantic - Data validation

PIL/OpenCV - Image processing

Pandas - CSV data analysis

Python-multipart - File uploads

Frontend (Node.js v22.14.0)
React 18 - UI library

Vite 5.x - Build tool (tối ưu cho Node.js 22)

Chart.js - Data visualization

React-Markdown - Markdown rendering

Axios - HTTP client


🚀 Deployment
Development
bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev

👥 Tác Giả
Nguyen Mach Dang Khoa - GitHub Profile

🙏 Ghi Nhận
Google Gemini AI - Multi-modal AI model

FastAPI - Modern web framework

React - UI library
