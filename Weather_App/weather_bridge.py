import requests
import datetime

# Συντεταγμένες πόλεων
coords = {
    "Thessaloniki": (40.6401, 22.9444),
    "Athens": (37.9838, 23.7275),
    "Patras": (38.2466, 21.7346),
    "Larisa": (39.6390, 22.4190),
    "Heraklion": (35.3400, 25.1340),
    "Volos": (39.3617, 22.9427),
    "Ioannina": (39.6640, 20.8537),
    "Kavala": (40.9390, 24.4119),
    "Chania": (35.5122, 24.0180),
    "Rhodes": (36.4349, 28.2176)
}

# Μετατροπή ISO ημερομηνίας -> Ελληνική συντομογραφία ημέρας
def greek_day_name(date_str):
    days_gr = ["Δευ", "Τρι", "Τετ", "Πεμ", "Παρ", "Σαβ", "Κυρ"]
    d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    return days_gr[d.weekday()]


def fetch_weather_for_gui(city):
    try:
        lat, lon = coords[city]

        # Ζητάμε τρέχον καιρό + 7ήμερη πρόγνωση
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current_weather=true"
            f"&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max"
            f"&timezone=auto"
        )

        data = requests.get(url, timeout=5).json()

        # -----------------------------
        # Τρέχων καιρός
        # -----------------------------
        w = data["current_weather"]
        temperature = w["temperature"]
        windspeed = w["windspeed"]

        # -----------------------------
        # 7ήμερη πρόγνωση
        # -----------------------------
        days_iso = data["daily"]["time"]
        days = [greek_day_name(d) for d in days_iso]

        temp_max = data["daily"]["temperature_2m_max"]
        wind_max = data["daily"]["windspeed_10m_max"]

        forecast7 = {
            "days": days,
            "temp": temp_max,
            "wind": wind_max
        }

        return {
            "city": city,
            "temperature": temperature,
            "windspeed": windspeed,
            "forecast7": forecast7
        }

    except Exception as e:
        return {"error": f"Weather error: {e}"}
