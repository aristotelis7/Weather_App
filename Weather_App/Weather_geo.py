import urllib.request
import urllib.parse
import json


def get_coordinates(city_name):

    encoded_city = urllib.parse.quote(city_name)

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded_city}&count=1"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urllib.request.urlopen(req, timeout=10) as response:

            data = json.loads(response.read().decode())

            if "results" not in data:
                return {"error": "Η πόλη δεν βρέθηκε"}

            result = data["results"][0]

            return {
                "lat": result["latitude"],
                "lon": result["longitude"],
                "name": result["name"]
            }

    except Exception as e:

        return {"error": str(e)}