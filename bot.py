import os
import asyncio
from threading import Thread
from dotenv import load_dotenv
from pathlib import Path
import time

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from fastapi import FastAPI
import uvicorn

from file_handler import save_file_from_telegram, save_file_from_url, compress_file_max
from archive_uploader import upload_to_archive

# ------------------------------
# Configuración
# ------------------------------
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 8000))
DOWNLOADS_FOLDER = os.getenv("DOWNLOADS_FOLDER", "downloads")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ------------------------------
# Comando /start
# ------------------------------
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 ¡Hola! Envía un archivo o enlace directo.\n"
        "Lo descargaré, lo comprimiré en un 7z (máxima compresión), "
        "lo subiré a archive.org y te enviaré un TXT con el enlace."
    )

# ------------------------------
# Manejar archivos/enlaces
# ------------------------------
@dp.message()
async def handle_files(message: Message):
    file_path = None

    # Archivos de Telegram
    if message.document or message.photo or message.video or message.audio or message.voice:
        file = None
        if message.document:
            file = await message.document.get_file()
        elif message.photo:
            file = await message.photo[-1].get_file()
        elif message.video:
            file = await message.video.get_file()
        elif message.audio:
            file = await message.audio.get_file()
        elif message.voice:
            file = await message.voice.get_file()

        if file:
            file_path = await save_file_from_telegram(file, DOWNLOADS_FOLDER)

    # Enlaces directos
    elif message.text and message.text.startswith(("http://", "https://")):
        try:
            file_path = await save_file_from_url(message.text, DOWNLOADS_FOLDER)
        except Exception as e:
            await message.reply(f"❌ Error al descargar: {e}")
            return

    if not file_path:
        return

    await message.reply(f"📥 Archivo descargado: {file_path.name}\n⏳ Comenzando compresión máxima...")

    try:
        archive_path = compress_file_max(file_path, DOWNLOADS_FOLDER)
        await message.reply(f"✅ Archivo comprimido en 7z: {archive_path.name}")
    except Exception as e:
        await message.reply(f"❌ Error al comprimir: {e}")
        return

    try:
        item_id = f"{Path(file_path).stem}_{int(time.time())}"
        urls = upload_to_archive(item_id, archive_path)
        await message.reply(f"🌐 Subida completa a archive.org!")

        # Crear TXT con enlace
        txt_name = Path(file_path).stem + ".txt"
        txt_path = Path(DOWNLOADS_FOLDER) / txt_name
        with open(txt_path, "w") as f:
            for url in urls:
                f.write(url + "\n")

        # Enviar TXT al usuario
        await message.reply_document(document=txt_path, caption="📄 Aquí tienes el enlace de descarga.")

    except Exception as e:
        await message.reply(f"❌ Error al subir a archive.org o generar TXT: {e}")
        return

# ------------------------------
# Servidor FastAPI
# ------------------------------
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "Bot activo ✅"}

def run_server():
    uvicorn.run(app, host="0.0.0.0", port=PORT)

# ------------------------------
# Función principal
# ------------------------------
async def main():
    print("🚀 Iniciando bot y servidor...")
    Thread(target=run_server, daemon=True).start()
    await dp.start_polling(bot)

# ------------------------------
# Ejecutar
# ------------------------------
if __name__ == "__main__":
    asyncio.run(main())