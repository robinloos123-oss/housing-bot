import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ====== CONFIG ======
TELEGRAM_TOKEN = os.getenv("8443772760:AAG-Is4O6sl6e9lT-lqQkIs_OGh4uocIBPM")
CHAT_ID = os.getenv("8713710491")

URL = ["https://www.pararius.nl/huurwoningen/rotterdam", 
      "https://www.rentalrotterdam.nl",
      "https://rivarentals.nl/aanbod"]

MAX_PRICE = 3000

ROOM_OPTIONS = [
    "3 kamers", "4 kamers",
    "3 room", "4 room",
    "3-room", "4-room"
]

AREAS = [
    "blijdorp",
    "centrum",
    "coolhaven",
    "delfshaven",
    "noord",
    "west"
]

BLOCK_WORDS = [
    "garantsteller",
    "niet geschikt voor delers",
    "no sharing",
    "working professional",
]

ALLOW_WORDS = [
    "student",
    "students",
    "woningdelers toegestaan",
]

# ====== SEEN ======

def load_seen():
    try:
        with open("seen.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen_links):
    with open("seen.json", "w") as f:
        json.dump(list(seen_links), f)

seen_links = load_seen()

# ====== TELEGRAM ======

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message
    }
    requests.post(url, data=data)

# ====== DETAIL SCRAPER ======

def get_full_description(link):
    try:
        response = requests.get(link, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        desc_div = soup.find("div", class_="listing-description__content")

        if desc_div:
            return desc_div.text.lower()

        return ""
    except:
        return ""

# ====== MAIN SCRAPER ======

def scrape():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    listings = soup.find_all("section", class_="listing-search-item")

    results = []

    for listing in listings:
        try:
            title = listing.find("a").text.strip()
            link = "https://www.pararius.nl" + listing.find("a")["href"]

            if link in seen_links:
                continue

            # prijs
            price_tag = listing.find("div", class_="listing-search-item__price")
            if not price_tag:
                continue

            price_str = price_tag.text.replace(".", "").replace("€", "").strip()
            price = int(''.join(filter(str.isdigit, price_str)))

            if price > MAX_PRICE:
                continue

            # 👉 HAAL VOLLEDIGE BESCHRIJVING OP
            full_description = get_full_description(link)

            # combineer met korte tekst
            description = (listing.text + " " + full_description).lower()

            # ===== FILTERS =====

            if not any(room in description for room in ROOM_OPTIONS):
                continue

            if not any(area in description for area in AREAS):
                continue

            if any(word in description for word in BLOCK_WORDS):
                continue

            if not any(word in description for word in ALLOW_WORDS):
                continue

            seen_links.add(link)

            results.append((title, link, price))

            print("✔ Match gevonden:", title)

            # kleine delay (voorkomt blokkade)
            time.sleep(1)

        except Exception as e:
            print("Skip listing:", e)
            continue

    return results

# ====== LOOP ======

print(" Bot gestart...")

while True:
    try:
        new_listings = scrape()

        for title, link, price in new_listings:
            message = f"🏠 {title}\n💰 €{price}\n{link}"
            send_telegram(message)
            print("✅ Sent:", title)

        save_seen(seen_links)

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(30)
