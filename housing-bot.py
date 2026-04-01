import requests
from bs4 import BeautifulSoup
import time
import json
import os

# ====== CONFIG ======
TELEGRAM_TOKEN = os.getenv("8443772760:AAG-Is4O6sl6e9lT-lqQkIs_OGh4uocIBPM")
CHAT_ID = os.getenv("8713710491")

BASE_URL = "https://www.rentalrotterdam.nl"
SEARCH_URL = "https://www.rentalrotterdam.nl/woningaanbod/huur"

MAX_PRICE = 3000

ROOM_OPTIONS = ["3", "4"]

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

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "nl-NL,nl;q=0.9"
}

# ===== SEEN STORAGE =====

def load_seen():
    try:
        with open("seen.json", "r") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    with open("seen.json", "w") as f:
        json.dump(list(seen), f)

seen_links = load_seen()

# ===== TELEGRAM =====

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# ===== GET DESCRIPTION =====

def get_description(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        desc = soup.get_text().lower()  # robuust → hele pagina
        return desc
    except:
        return ""

# ===== MAIN SCRAPER =====

def scrape():
    results = []

    res = requests.get(SEARCH_URL, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    links = soup.find_all("a", href=True)

    for link in links:
        href = link.get("href")

        if "/huurwoning/" not in href:
            continue

        full_link = BASE_URL + href

        if full_link in seen_links:
            continue

        try:
            # open detail pagina
            description = get_description(full_link)

            # ===== FILTERS =====

            # prijs
            price = None
            for word in description.split():
                if "€" in word:
                    digits = ''.join(filter(str.isdigit, word))
                    if digits:
                        price = int(digits)
                        break

            if not price or price > MAX_PRICE:
                continue

            # kamers (simpel maar effectief)
            if not any(r + " kamer" in description for r in ROOM_OPTIONS):
                continue

            # wijk
            if not any(area in description for area in AREAS):
                continue

            # block
            if any(word in description for word in BLOCK_WORDS):
                continue

            # allow
            if not any(word in description for word in ALLOW_WORDS):
                continue

            title = link.text.strip() or "Woning"

            seen_links.add(full_link)

            results.append((title, full_link, price))

            print("✔ MATCH:", title)

            time.sleep(1)  # anti-block

        except Exception as e:
            print("skip:", e)
            continue

    return results

# ===== LOOP =====

print("Bot gestart...")

while True:
    try:
        listings = scrape()

        for title, link, price in listings:
            msg = f"🏠 {title}\n💰 €{price}\n{link}"
            send_telegram(msg)
            print("Sent:", title)

        save_seen(seen_links)

    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
