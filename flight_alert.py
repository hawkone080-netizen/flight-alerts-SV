import requests
import json
import os

# ===============================
# CONFIGURA TU VUELO
# ===============================
ORIGIN = "SAL"
DESTINATION = "MEX"

DEPARTURE_DATE = "2026-04-01"
RETURN_DATE = "2026-04-05"

PRICE_FILE = "price.json"

# ===============================
# CREDENCIALES (VIENEN DE GITHUB)
# ===============================
AMADEUS_KEY = os.environ["AMADEUS_KEY"]
AMADEUS_SECRET = os.environ["AMADEUS_SECRET"]
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]


def get_amadeus_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": AMADEUS_KEY,
        "client_secret": AMADEUS_SECRET
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]


def get_price():
    token = get_amadeus_token()
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "originLocationCode": ORIGIN,
        "destinationLocationCode": DESTINATION,
        "departureDate": DEPARTURE_DATE,
        "returnDate": RETURN_DATE,
        "adults": 1,
        "max": 1
    }

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    price = float(data["data"][0]["price"]["total"])
    return price


def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


def load_old_price():
    try:
        with open(PRICE_FILE) as f:
            return json.load(f)["price"]
    except:
        return None


def save_price(price):
    with open(PRICE_FILE, "w") as f:
        json.dump({"price": price}, f)


def main():
    new_price = get_price()
    old_price = load_old_price()

    print(f"Precio actual: {new_price}")

    if old_price is None:
        save_price(new_price)
        return

    if new_price < old_price:
        send_telegram(
            f"✈️ Bajó el precio del vuelo SAL ⇄ MEX\n"
            f"📅 1–5 de abril\n"
            f"💰 Nuevo precio: ${new_price}"
        )

    save_price(new_price)


if __name__ == "__main__":
    main()
