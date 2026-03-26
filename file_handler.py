import aiohttp
from pathlib import Path
import subprocess

# ------------------------------
# Descargar archivo de Telegram
# ------------------------------
async def save_file_from_telegram(file, downloads_folder: str):
    downloads_path = Path(downloads_folder)
    downloads_path.mkdir(exist_ok=True)

    file_path = downloads_path / file.file_name
    await file.download(destination=file_path)
    return file_path

# ------------------------------
# Descargar archivo desde URL
# ------------------------------
async def save_file_from_url(url: str, downloads_folder: str):
    downloads_path = Path(downloads_folder)
    downloads_path.mkdir(exist_ok=True)

    filename = url.split("/")[-1] or "downloaded_file"
    file_path = downloads_path / filename

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(file_path, "wb") as f:
                    f.write(await response.read())
                return file_path
            else:
                raise Exception(f"Error al descargar: {response.status}")

# ------------------------------
# Compresión con 7z (real)
# ------------------------------
def compress_file_max(file_path: str, output_folder: str):
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)

    base_name = Path(file_path).stem
    archive_path = output_path / f"{base_name}.7z"

    result = subprocess.run(
        ["7z", "a", "-t7z", "-mx=9", str(archive_path), str(file_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Error 7z: {result.stderr}")

    return archive_path
