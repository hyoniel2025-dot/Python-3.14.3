import subprocess
from pathlib import Path

def compress_file_max(file_path: str, output_folder: str):
    output_path = Path(output_folder)
    output_path.mkdir(exist_ok=True)

    base_name = Path(file_path).stem
    archive_path = output_path / f"{base_name}.7z"

    # Compresión máxima con 7zip real
    result = subprocess.run(
        ["7z", "a", "-t7z", "-mx=9", str(archive_path), str(file_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(f"Error 7z: {result.stderr}")

    return archive_path
