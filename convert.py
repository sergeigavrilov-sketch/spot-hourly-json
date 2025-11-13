import json
from datetime import datetime, timedelta, timezone
from statistics import mean
from urllib.request import urlopen

SOURCE_URL = "https://spot.utilitarian.io/electricity/FI/latest/"
BIDDING_ZONE = "FI"
TIMEZONE = "Europe/Helsinki"
OFFSET = timedelta(hours=2)  # UTC+2 зимой (Finland STD time)

def fetch_data():
    with urlopen(SOURCE_URL) as r:
        return json.load(r)

def parse_iso(ts):
    if ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")
    return datetime.fromisoformat(ts)

def aggregate_hourly(data):
    hourly = {}
    for e in data:
        t_utc = parse_iso(e["timestamp"])
        hour_utc = t_utc.replace(minute=0, second=0, microsecond=0)
        hourly.setdefault(hour_utc, []).append(float(e["value"]))

    results = []
    for hour_utc, values in sorted(hourly.items()):
        avg = mean(values)
        # переводим в Finland local time (+02:00)
        local_time = hour_utc + OFFSET
        results.append({
            "time": local_time.strftime("%Y-%m-%d %H:%M:%S+02:00"),
            "price": round(avg * 10, 4)  # *10 чтобы перевести в EUR/MWh, если нужно
        })
    return results

def build_output(hourly):
    hourly_prices = {}
    day_index = 0
    hour_index = 0
    prev_day = None
    for h in hourly:
        day = h["time"].split(" ")[0]
        if prev_day is None:
            prev_day = day
        if day != prev_day:
            day_index += 1
            hour_index = 0
            prev_day = day
        key = f"{day_index}.{hour_index}"
        hourly_prices[key] = h
        hour_index += 1

    meta = {
        "bidding_zone": BIDDING_ZONE,
        "timezone": TIMEZONE,
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S+00:00"),
        "units": "EUR/MWh",
        "resolution": "1H"
    }

    return {"hourly_prices": hourly_prices, "meta": meta}

def main():
    print("Fetching data...")
    raw = fetch_data()
    hourly = aggregate_hourly(raw)
    result = build_output(hourly)
    with open("docs/hourly.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=None, separators=(",", ": "))
    print("Created docs/hourly.json with", len(result["hourly_prices"]), "entries.")

if __name__ == "__main__":
    main()
