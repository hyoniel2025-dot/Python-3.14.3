import os
from pathlib import Path
import aiohttp
import py7zr

async def save_file_from_telegram(file, downloads_folder: str):
    downloads_path = Path(downloads_folder)
    downloads_path.mkdir(exist_ok=True)
    file_path = downloads_path / file.file_name
    await file.download(destination=file_path)
    return file_path

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
                raise Exception(f"No se pudo descargar el archivo, status: {response.status}")

def compress_file_max(file_path: str, output_folder: str):
    """
    Comprime en 7z con máxima compresión LZMA2.
    """
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)
    base_name = Path(file_path).stem
    archive_name = output_path / f"{base_name}.7z"

    with py7zr.SevenZipFile(
        archive_name,
        'w',
        filters=[{'id': 'LZMA2', 'preset': 9}]  # máxima compresión
    ) as archive:
        archive.write(file_path, arcname=Path(file_path).name)

    return archive_name