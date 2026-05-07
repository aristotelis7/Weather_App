import tkinter as tk
from PIL import Image, ImageTk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import weather_bridge

# -----------------------------
# Ρυθμίσεις χάρτη
# -----------------------------
MAP_W, MAP_H = 600, 625
MIN_LAT, MAX_LAT = 34.5, 42.3
MIN_LON, MAX_LON = 19.0, 28.6

def geo_to_pixel(lat, lon):
    x = (lon - MIN_LON) / (MAX_LON - MIN_LON) * MAP_W
    y = (MAX_LAT - lat) / (MAX_LAT - MIN_LAT) * MAP_H
    return int(x), int(y)

cities = [
    ("Thessaloniki", 40.64, 22.94),
    ("Athens", 37.98, 23.72),
    ("Patras", 38.24, 21.73),
    ("Larisa", 39.63, 22.41),
    ("Heraklion", 35.34, 25.13),
     ("Κοζάνη", 40.3000, 21.7833), ("Καστοριά", 40.5225, 21.2679),
    ("Τρίκαλα", 39.5549, 21.7684), ("Πρέβεζα", 38.9562, 20.7508),
    ("Λαμία", 38.8950, 22.4333), ("Χαλκίδα", 38.4626, 23.5951),
    ("Καλαμάτα", 37.0389, 22.1142), ("Τρίπολη", 37.5140, 22.3726),
    ("Σπάρτη", 37.0733, 22.4297), ("Κέρκυρα", 39.6200, 19.9197),
    ("Ζάκυνθος", 37.7817, 20.8953), ("Αργοστόλι", 38.1750, 20.4890),
    ("Ρόδος", 36.4349, 28.2176), ("Χανιά", 35.5122, 24.0180),
    ("Ερμούπολη", 37.4398, 24.9388), ("Μυτιλήνη", 39.1100, 26.5547),
    ("Χίος", 38.3678, 26.1361), ("Σάμος", 37.7543, 26.9771)
]

cities = [{"name": c, "pos": geo_to_pixel(lat, lon)} for c, lat, lon in cities]

# -----------------------------
# Κλάση εφαρμογής
# -----------------------------
class WeatherApp:
    def __init__(self, root):
        self.root = root
        root.title("Weather Map Greece")

        tk.Label(root, text="Weather Map Greece", font=("Arial", 16, "bold")).pack(pady=5)

        # Χάρτης
        self.canvas = tk.Canvas(root, width=MAP_W, height=MAP_H)
        self.canvas.pack()

        self.map_img = ImageTk.PhotoImage(Image.open("greece_map.png").resize((MAP_W, MAP_H)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.map_img)

        # Φόρτωση icons
        self.icons = {
            name: ImageTk.PhotoImage(
                Image.open(f"icons/{name}.png").resize((40, 40))
            )
            for name in ["sun", "cloud", "rain", "wind"]
        }

        self.current_icon = None  # reference για να μην εξαφανίζεται

        # Τοποθέτηση πόλεων
        for c in cities:
            x, y = c["pos"]
            self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="red")
            self.canvas.create_text(x, y-12, text=c["name"], font=("Arial", 9, "bold"))

        self.canvas.bind("<Button-1>", self.on_click)

        self.info_label = tk.Label(root, font=("Arial", 12))
        self.info_label.pack(pady=10)

        self.graph_canvas = None

    # Επιλογή icon ανάλογα με καιρό
    def pick_icon(self, temp, wind):
        if wind > 35:
            return self.icons["wind"]
        if temp > 25:
            return self.icons["sun"]
        if temp < 15:
            return self.icons["rain"]
        return self.icons["cloud"]

    # Κλικ σε πόλη
    def on_click(self, e):
        for c in cities:
            x, y = c["pos"]
            if abs(e.x - x) < 15 and abs(e.y - y) < 15:
                self.show_weather(c)
                return

    # Εμφάνιση καιρού
    def show_weather(self, city):
        data = weather_bridge.fetch_weather_for_gui(city["name"])

        if "error" in data:
            self.info_label.config(text=data["error"])
            return

        temp = data["temperature"]
        wind = data["windspeed"]

        self.info_label.config(text=f"{city['name']}: {temp}°C, Wind {wind} km/h")

        # Εμφάνιση icon
        icon = self.pick_icon(temp, wind)
        self.current_icon = icon  # κρατάμε reference

        x, y = city["pos"]
        self.canvas.create_image(x, y - 40, image=self.current_icon)

        # Γράφημα
        self.show_graph(city["name"], data["forecast7"])

    # Γράφημα 7 ημερών
    def show_graph(self, city, forecast):
        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()

        fig, ax1 = plt.subplots(figsize=(6, 3))
        ax1.plot(forecast["days"], forecast["temp"], marker="o", color="red")
        ax1.set_ylabel("Temp (°C)", color="red")
        ax1.grid(True)

        ax2 = ax1.twinx()
        ax2.plot(forecast["days"], forecast["wind"], marker="o", color="blue")
        ax2.set_ylabel("Wind (km/h)", color="blue")

        fig.suptitle(f"7-Day Forecast - {city}")

        self.graph_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(pady=10)

# -----------------------------
# Εκκίνηση εφαρμογής
# -----------------------------
root = tk.Tk()
root.geometry("750x850")
WeatherApp(root)
root.mainloop()
