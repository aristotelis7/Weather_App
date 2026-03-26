import matplotlib
matplotlib.use("Agg")  # Απαραίτητο για PyInstaller + matplotlib

import tkinter as tk
from PIL import Image, ImageTk
import weather_bridge
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys, os

# ---------------------------------------------------------
# PyInstaller resource path
# ---------------------------------------------------------
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return relative

# ---------------------------------------------------------
# Ρυθμίσεις Χάρτη
# ---------------------------------------------------------
MAP_W, MAP_H = 600, 625
MIN_LAT, MAX_LAT = 34.5, 42.3
MIN_LON, MAX_LON = 19.0, 28.6

def geo_to_pixel(lat, lon):
    x = (lon - MIN_LON) / (MAX_LON - MIN_LON) * MAP_W
    y = (MAX_LAT - lat) / (MAX_LAT - MIN_LAT) * MAP_H
    return int(x), int(y)

cities_raw = [
    ("Thessaloniki", 40.6401, 22.9444),
    ("Athens", 37.9838, 23.7275),
    ("Patras", 38.2466, 21.7346),
    ("Larisa", 39.6390, 22.4190),
    ("Heraklion", 35.3400, 25.1340),
    ("Volos", 39.3617, 22.9427),
    ("Ioannina", 39.6640, 20.8537),
    ("Kavala", 40.9390, 24.4119),
    ("Chania", 35.5122, 24.0180),
    ("Rhodes", 36.4349, 28.2176)
]

cities = [{"city": c, "x": geo_to_pixel(lat, lon)} for c, lat, lon in cities_raw]

# ---------------------------------------------------------
# GUI
# ---------------------------------------------------------
class WeatherGUI:
    def __init__(self, root):
        self.root = root
        root.title("Weather Map Greece")

        tk.Label(root, text="Weather Map Greece", font=("Arial", 18, "bold"), fg="#003366").pack(pady=(10, 0))
        tk.Label(root, text="Κάνε κλικ σε μια πόλη για να δεις τρέχον καιρό.", font=("Arial", 11), fg="#444444").pack(pady=(0, 10))

        self.canvas = tk.Canvas(root, width=MAP_W, height=MAP_H)
        self.canvas.pack()

        # Φόρτωση χάρτη με resource_path
        img = Image.open(resource_path("greece_map.png")).resize((MAP_W, MAP_H))
        self.map_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor="nw", image=self.map_img)

        # Φόρτωση icons με resource_path
        self.icons = {
            name: ImageTk.PhotoImage(
                Image.open(resource_path(f"icons/{name}.png")).resize((35, 35))
            )
            for name in ["sun", "cloud", "rain", "wind"]
        }

        for c in cities:
            x, y = c["x"]
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
            self.canvas.create_text(x, y-12, text=c["city"], font=("Arial", 8, "bold"))

        self.canvas.bind("<Button-1>", self.on_click)

        self.label = tk.Label(root, font=("Arial", 12))
        self.label.pack(pady=10)
        self.icon_item, self.graph_canvas = None, None

    def pick_icon(self, temp, wind):
        if wind > 35:
            return self.icons["wind"]
        return self.icons["sun"] if temp > 25 else self.icons["cloud"]

    def on_click(self, e):
        for c in cities:
            x, y = c["x"]
            if abs(e.x - x) < 20 and abs(e.y - y) < 20:
                self.show_weather(c)
                return
        self.label.config(text="Καμία πόλη")

    def show_graph_7days(self, city_name, forecast7):
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()

        fig, ax1 = plt.subplots(figsize=(6, 3))
        ax1.set_xlabel("Ημέρα")
        ax1.set_ylabel("Θερμοκρασία (°C)", color="red")
        ax1.plot(forecast7["days"], forecast7["temp"], marker="o", color="red")
        ax1.tick_params(axis="y", labelcolor="red")
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.set_ylabel("Άνεμος (km/h)", color="blue")
        ax2.plot(forecast7["days"], forecast7["wind"], marker="o", color="blue")
        ax2.tick_params(axis="y", labelcolor="blue")

        fig.suptitle(f"Πρόγνωση 7 Ημερών - {city_name}")

        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(pady=10)

    def show_weather(self, city):
        data = weather_bridge.fetch_weather_for_gui(city["city"])

        if "error" in data:
            self.label.config(text=data["error"])
            return

        temp, wind = data["temperature"], data["windspeed"]
        self.label.config(text=f"{city['city']}  {temp}°C  Άνεμος {wind} km/h")

        if self.icon_item:
            self.canvas.delete(self.icon_item)

        icon = self.pick_icon(temp, wind)
        self.icon_item = self.canvas.create_image(city["x"][0], city["x"][1] - 30, image=icon)

        self.show_graph_7days(city["city"], data["forecast7"])

# ---------------------------------------------------------
# Εκκίνηση εφαρμογής
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x900")
    WeatherGUI(root)
    root.mainloop()

