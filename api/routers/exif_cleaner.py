import os
import io
import uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

router = APIRouter(prefix="/exif", tags=["EXIF Cleaner"])

# Папка для временного хранения «чистых» изображений
CLEAN_DIR = os.path.join(os.path.dirname(__file__), "..", "cleaned_images")
os.makedirs(CLEAN_DIR, exist_ok=True)


def _decode_gps_info(gps_data) -> dict:
    """Расшифровывает GPS-данные из EXIF в читаемые координаты."""
    def _convert_to_degrees(value):
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    gps = {}
    for key, val in gps_data.items():
        tag_name = GPSTAGS.get(key, key)
        try:
            if tag_name == "GPSLatitude":
                gps["latitude"] = _convert_to_degrees(val)
                if gps_data.get(1) == "S":
                    gps["latitude"] = -gps["latitude"]
            elif tag_name == "GPSLongitude":
                gps["longitude"] = _convert_to_degrees(val)
                if gps_data.get(3) == "W":
                    gps["longitude"] = -gps["longitude"]
            elif tag_name == "GPSAltitude":
                gps["altitude"] = float(val[0]) / float(val[1]) if val[1] != 0 else None
            else:
                gps[tag_name] = str(val)
        except Exception:
            gps[tag_name] = str(val)

    return gps


def _extract_exif(image: Image.Image) -> dict:
    """Извлекает все доступные EXIF-данные из изображения."""
    exif_data = {}
    try:
        info = image.getexif()
        if not info:
            return exif_data

        for tag_id, value in info.items():
            tag_name = TAGS.get(tag_id, str(tag_id))

            # GPS — расшифровать
            if tag_id == 34853 and isinstance(value, dict):
                exif_data["GPS"] = _decode_gps_info(value)
            elif isinstance(value, bytes):
                try:
                    exif_data[tag_name] = value.decode("utf-8", errors="replace")
                except Exception:
                    exif_data[tag_name] = "<binary data>"
            else:
                exif_data[tag_name] = str(value)

    except Exception:
        pass

    return exif_data


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Загружает изображение, извлекает EXIF-метаданные и показывает их.
    Позволяет увидеть, сколько информации «утекает» с фотографией.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось открыть изображение: {e}")

    exif_data = _extract_exif(image)

    # Оценка «утечки»
    privacy_risks = []
    if "GPS" in exif_data:
        privacy_risks.append("📍 Обнаружены GPS-координаты — можно определить местоположение")
    if "DateTime" in exif_data or "DateTimeOriginal" in exif_data:
        privacy_risks.append("📅 Есть дата и время съёмки")
    if "Model" in exif_data:
        privacy_risks.append(f"📷 Указана модель камеры: {exif_data['Model']}")
    if "Software" in exif_data:
        privacy_risks.append(f"💻 Указано ПО для обработки: {exif_data['Software']}")
    if "Make" in exif_data:
        privacy_risks.append(f"🏭 Указан производитель: {exif_data['Make']}")

    return {
        "filename": file.filename,
        "format": image.format,
        "size": image.size,
        "has_exif": len(exif_data) > 0,
        "exif_count": len(exif_data),
        "exif_data": exif_data,
        "privacy_risks": privacy_risks,
        "risk_level": "высокий" if "GPS" in exif_data else "средний" if privacy_risks else "низкий",
    }


@router.post("/clean")
async def clean_exif(file: UploadFile = File(...)):
    """
    Загружает изображение, удаляет все EXIF-метаданные и возвращает «чистый» файл.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    try:
        content = await file.read()
        image = Image.open(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось открыть изображение: {e}")

    # Создаём «чистое» изображение без EXIF
    output = io.BytesIO()

    # Определяем формат
    fmt = image.format or "JPEG"
    # PNG не поддерживает exif в PIL, для JPEG сохраняем
    if fmt == "PNG":
        # Для PNG просто сохраняем как есть (обычно EXIF нет)
        image.save(output, format="PNG")
        content_type = "image/png"
        ext = "png"
    else:
        # Для JPEG — пересохраняем без exif
        image.save(output, format="JPEG", exif=b"")
        content_type = "image/jpeg"
        ext = "jpg"

    output.seek(0)

    # Сохраняем на сервере
    clean_filename = f"cleaned_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    clean_path = os.path.join(CLEAN_DIR, clean_filename)
    with open(clean_path, "wb") as f:
        f.write(output.getvalue())

    return StreamingResponse(
        io.BytesIO(output.getvalue()),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="cleaned_{clean_filename}"'
        },
    )
