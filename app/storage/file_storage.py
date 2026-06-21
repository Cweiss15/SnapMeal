import uuid
from pathlib import Path

from fastapi import UploadFile

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_upload(file: UploadFile) -> Path:
    extension = Path(file.filename).suffix or ".jpg"
    filename = f"{uuid.uuid4()}{extension}"
    filepath = UPLOAD_DIR / filename

    content = await file.read()
    filepath.write_bytes(content)

    return filepath


async def save_uploads(files: list[UploadFile]) -> list[Path]:
    paths = []
    for file in files:
        path = await save_upload(file)
        paths.append(path)
    return paths