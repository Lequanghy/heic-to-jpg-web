# main.py
from fastapi import FastAPI, File, HTTPException, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path
import pillow_heif
import pillow_avif
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
async def convert_heic(file: UploadFile = File(...),format: str = Form("jpg"), fromFormat: list[str] = []):
    fromFormat = fromFormat[0].split(',')
    fromFormatTuple = tuple(fromFormat)
    fromFormatStr = ', '.join(fromFormat)
    if not file.filename.lower().endswith(fromFormatTuple): # type: ignore
        raise HTTPException(
            status_code=400,  # Bad Request
            detail="Only "+ fromFormatStr +" files are allowed"
        )
    else:
        print(fromFormatStr)
    
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    if image.mode in ("RGBA", "LA", "PA"):
        if format == "jpg":  # ONLY JPG cannot have transparency
            # Force white background
            bg = Image.new("RGB", image.size, (255, 255, 255))
            bg.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else image.split()[3])
            image = bg
        else:
            # PNG, WebP, AVIF → keep transparency!
            image = image.convert("RGBA")  # ensure alpha channel is preserved
    else:
        # No alpha → safe to convert to RGB
        if format != "png":  # PNG can stay RGBA even if no transparency
            image = image.convert("RGB")

    # Save to bytes
    img_io = io.BytesIO()
    save_params = {}
    pil_format = "JPEG"

    if format == "jpg":
        pil_format = "JPEG"
        save_params = {"quality": 94, "optimize": True, "progressive": True}

    elif format == "png":
        pil_format = "PNG"
        save_params = {"compress_level": 6, "optimize": True}

    elif format == "avif":
        pil_format = "AVIF"
        save_params = {"quality": 90, 'speed': 6} 

    elif format == "webp":
        pil_format = "WEBP"
        save_params = {"quality": 90, "method": 6, "lossless": False}

    image.save(img_io, format=pil_format, **save_params)
    img_io.seek(0)

    # filename
    stem = Path(file.filename).stem # type: ignore
    ext = "jpg" if format == "jpg" else format
    new_filename = f"{stem}.{ext}"
    print('completed /convert')
    return StreamingResponse(
        img_io,
        media_type=f"image/{'jpeg' if format=='jpg' else format}",
        headers={"Content-Disposition": f'attachment; filename="{new_filename}"'}
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)