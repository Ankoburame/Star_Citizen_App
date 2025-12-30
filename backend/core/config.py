import os
from dotenv import load_dotenv

load_dotenv()

UEX_API_TOKEN = os.getenv("UEX_API_TOKEN")

if not UEX_API_TOKEN:
    raise RuntimeError("UEX_API_TOKEN manquant (variable d’environnement)")
