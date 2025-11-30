# main.py
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path
import pillow_heif
from PIL import Image
import io

app = FastAPI(title="HEIC to JPG Converter")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create output folder
Path("converted").mkdir(exist_ok=True)

pillow_heif.register_heif_opener()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/convert")
async def convert_heic(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(('.heic', '.heif')): # type: ignore
        return {"error": "Only HEIC/HEIF files allowed"}

    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # Convert to RGB if needed
    if image.mode in ("RGBA", "LA", "PA"):
        image = image.convert("RGB")

    # Save to bytes
    img_io = io.BytesIO()
    image.save(img_io, format='JPEG', quality=95, optimize=True)
    img_io.seek(0)

    new_filename = Path(file.filename).stem + ".jpg" # type: ignore

    return StreamingResponse(img_io, media_type="image/jpeg",
                           headers={"Content-Disposition": f"attachment; filename={new_filename}"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)