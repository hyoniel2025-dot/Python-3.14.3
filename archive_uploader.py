import internetarchive as ia
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()
IA_ACCESS_KEY = os.getenv("IA_ACCESS_KEY")
IA_SECRET_KEY = os.getenv("IA_SECRET_KEY")

def upload_to_archive(item_id: str, file_path: str, metadata: dict = None):
    """
    Sube un archivo 7z a archive.org y devuelve el enlace directo.
    """
    metadata = metadata or {"title": item_id, "mediatype": "software"}
    urls = []

    with ia.get_session(IA_ACCESS_KEY, IA_SECRET_KEY):
        item = ia.get_item(item_id)
        if not item.exists():
            item = ia.create_item(item_id, metadata=metadata)
        item.upload([str(file_path)], retries=5)

        filename = Path(file_path).name
        urls.append(f"https://archive.org/download/{item_id}/{filename}")

    return urls