import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ====== CONFIG ======
TELEGRAM_TOKEN = os.getenv("8443772760:AAG-Is4O6sl6e9lT-lqQkIs_OGh4uocIBPM")
CHAT_ID = os.getenv("8713710491")

URL = "https://www.pararius.nl/huurwoningen/rotterdam"

def test_scrape():
    print("Test scrape gestart...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # DEBUG: print stuk van HTML
    print("Pagina geladen, lengte:", len(response.text))

    listings = soup.find_all("a", href=True)

    print("Aantal links gevonden:", len(listings))

    for link in listings:
        href = link.get("href")

        if "/huurwoning/" in href:
            full_link = "https://www.pararius.nl" + href
            title = link.text.strip()

            message = f"TEST 🧪\n🏠 {title}\n{full_link}"
            send_telegram(message)

            print("✅ Werkt! Listing gevonden")
            return

    print("❌ Nog steeds geen listing gevonden")

test_scrape()
