import urllib.request
import json


def get_weather(lat, lon):

    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

    try:

        with urllib.request.urlopen(url) as response:

            data = json.loads(response.read().decode())

            weather = data["current_weather"]

            return {
                "temperature": weather["temperature"],
                "windspeed": weather["windspeed"]
            }

    except Exception as e:

        return {"error": str(e)}
