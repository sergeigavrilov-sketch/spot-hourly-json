import requests, json, datetime, pytz

url = "https://spot.utilitarian.io/electricity/FI/latest/"
data = requests.get(url).json()

hours = {}
tz = pytz.timezone("Europe/Helsinki")

# группируем каждые 4 интервала по часу
for i in range(0, len(data), 4):
    hour_block = data[i:i+4]
    avg = sum(float(x["value"]) for x in hour_block) / len(hour_block)
    t = datetime.datetime.fromisoformat(hour_block[0]["timestamp"]).astimezone(tz)
    hours[f"{i//4}.0"] = {
        "time": t.strftime("%Y-%m-%d %H:%M:%S%z"),
        "price": round(avg, 3)
    }

output = {
    "hourly_prices": hours,
    "meta": {
        "bidding_zone": "FI",
        "timezone": "Europe/Helsinki",
        "generated_at": datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S%z"),
        "units": "EUR/MWh",
        "resolution": "1H"
    }
}

with open("hourly.json", "w") as f:
    json.dump(output, f, indent=2)
