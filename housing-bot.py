import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ====== CONFIG ======
TELEGRAM_TOKEN = os.getenv("8443772760:AAG-Is4O6sl6e9lT-lqQkIs_OGh4uocIBPM")
CHAT_ID = os.getenv("8713710491")

URL = "https://www.pararius.nl/huurwoningen/rotterdam"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

def test_scrape():
    print("Test scrape gestart...")

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    listing = soup.find("section", class_="listing-search-item")

    if not listing:
        print("Geen listing gevonden")
        return

    title = listing.find("a").text.strip()
    link = "https://www.pararius.nl" + listing.find("a")["href"]

    message = f"TEST 🧪\n🏠 {title}\n{link}"

    send_telegram(message)

    print("✅ Test bericht verstuurd!")

# run test
test_scrape()
