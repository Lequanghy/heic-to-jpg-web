# HEIC to JPG Converter – Instant Web App
A beautiful, blazing-fast web tool that converts .HEIC / .HEIF photos (iPhone, iPad) to .JPG instantly in your browser.\
Live demo → just run it locally in 10 seconds!
### Features

- Drag & drop or click to upload (multiple files supported)
- Instant conversion using Pillow + pillow-heif
- Zero server storage – files are processed in memory and never saved
- Responsive, mobile-friendly UI with Tailwind CSS
- Progress bar + individual download buttons
- Single-file FastAPI app (super easy to deploy)
- 95 % JPEG quality by default (customizable)

## 1. Clone or download this repo
git clone https://github.com/Lequanghy/heic-to-jpg-web.git
cd heic-to-jpg-web

## 2. Install dependencies
pip install fastapi uvicorn pillow pillow-heif python-multipart

## 3. Run the app
python main.py
Open http://localhost:8000 in your browser — done!
