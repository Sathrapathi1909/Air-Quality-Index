
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random  # For demo predictions

from module2_ingestion import load_aqi
from module3_calculation import (
    classify_aqi, severity_level, evaluate_pollutant,
    pollutant_explanation, respiratory_risk, aqi_color
)
from module4_pollutants import get_pollutant_details
from module5_city_analysis import (
    get_city_records, average_aqi, city_industrial_risk
)
from module6_health import health_advice, format_health_stats


# =====================================================
# ASCII BAR CHART HELPER
# =====================================================
def ascii_bar(value, max_value, width=30):
    filled = int((value / max_value) * width)
    return "█" * filled + " " * (width - filled)


# =====================================================
# MAIN DASHBOARD CLASS
# =====================================================
class AQIDashboardGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Air Quality Monitoring Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg="#eef3ff")

        self.dataset = []
        self.cities = []

        self.build_ui()

    # =================================================
    # BUILD GUI
    # =================================================
    def build_ui(self):
        # Title
        title = tk.Label(
            self.root,
            text="AIR QUALITY INDEX MONITORING SYSTEM",
            bg="#eef3ff", fg="#0d1b7e",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=15)

        # Left panel
        self.left_panel = tk.Frame(self.root, bg="#d9e1ff", width=260)
        self.left_panel.pack(side="left", fill="y")

        # Right output text area
        self.output = ScrolledText(self.root, width=90, height=34, font=("Consolas", 11))
        self.output.pack(side="right", padx=10, pady=10)

        # Buttons
        btn = {"bg": "#364fc7", "fg": "white", "font": ("Arial", 12), "width": 23}
        tk.Button(self.left_panel, text="LOAD DATASET", command=self.load_data, **btn).pack(pady=10)
        tk.Button(self.left_panel, text="CITY DETAILS", command=self.show_city_details, **btn).pack(pady=10)
        tk.Button(self.left_panel, text="POLLUTANT LEVELS", command=self.show_pollutants, **btn).pack(pady=10)
        tk.Button(self.left_panel, text="AQI REPORT", command=self.show_aqi_report, **btn).pack(pady=10)
        tk.Button(self.left_panel, text="HEALTH IMPACT", command=self.show_health_impact, **btn).pack(pady=10)
        tk.Button(self.left_panel, text="CITY RISK INDEX", command=self.show_city_risk, **btn).pack(pady=10)
        tk.Button(self.left_panel, text="FUTURE AQI PREDICTION", command=self.show_future_prediction, **btn).pack(pady=10)

        tk.Label(self.left_panel, text="Select City:", bg="#d9e1ff", font=("Arial", 12, "bold")).pack(pady=(20, 5))
        self.city_var = tk.StringVar()
        self.city_dropdown = tk.OptionMenu(self.left_panel, self.city_var, ())
        self.city_dropdown.pack()

    # =================================================
    # LOAD DATA
    # =================================================
    def load_data(self):
        self.dataset = load_aqi()
        self.cities = sorted(list({d["city"] for d in self.dataset}))

        # Update dropdown
        menu = self.city_dropdown["menu"]
        menu.delete(0, "end")
        for c in self.cities:
            menu.add_command(label=c, command=lambda x=c: self.city_var.set(x))

        self.output.insert(tk.END, "✔ Dataset loaded successfully. 200+ records ready.\n")
        self.output.insert(tk.END, "Cities available:\n")
        self.output.insert(tk.END, ", ".join(self.cities) + "\n\n")

    # =================================================
    # SHOW CITY DETAILS
    # =================================================
    def show_city_details(self):
        city = self.city_var.get()
        if not city:
            self.output.insert(tk.END, "⚠ Select a city first!\n")
            return

        records = get_city_records(self.dataset, city)
        avg_aqi = average_aqi(self.dataset, city)
        category = classify_aqi(avg_aqi)
        severity = severity_level(avg_aqi)
        color = aqi_color(avg_aqi)

        self.output.insert(tk.END, f"\n=============================\n")
        self.output.insert(tk.END, f" AIR QUALITY REPORT: {city}\n")
        self.output.insert(tk.END, f"=============================\n")
        self.output.insert(tk.END, f"AQI Value: {avg_aqi} ({category})\n")
        self.output.insert(tk.END, f"Severity Level: {severity}/5\n")
        self.output.insert(tk.END, f"AQI Color Code: {color}\n")
        self.output.insert(tk.END, f"Total records analyzed: {len(records)}\n\n")

    # =================================================
    # SHOW POLLUTANT LEVELS
    # =================================================
    def show_pollutants(self):
        city = self.city_var.get()
        if not city:
            self.output.insert(tk.END, "⚠ Select a city first!\n")
            return

        avg_pollution = get_pollutant_details(self.dataset, city)
        max_val = max(avg_pollution.values())

        self.output.insert(tk.END, f"\nPOLLUTANT LEVELS for {city}\n")
        self.output.insert(tk.END, "-"*60 + "\n")

        for p, v in avg_pollution.items():
            bar = ascii_bar(v, max_val)
            evaluation = evaluate_pollutant(p, v)
            self.output.insert(tk.END, f"{p:<7} | {bar} {v}\n")
            self.output.insert(tk.END, f"→ {evaluation}\n\n")

    # =================================================
    # SHOW AQI REPORT
    # =================================================
    def show_aqi_report(self):
        city = self.city_var.get()
        if not city:
            self.output.insert(tk.END, "⚠ Select a city first!\n")
            return

        avg_aqi = average_aqi(self.dataset, city)
        reason = respiratory_risk(avg_aqi)
        industrial_risk = city_industrial_risk(self.dataset, city)

        self.output.insert(tk.END, f"\nAQI ANALYSIS for {city}\n")
        self.output.insert(tk.END, "-"*60 + "\n")
        self.output.insert(tk.END, f"AQI Value: {avg_aqi}\n")
        self.output.insert(tk.END, f"Respiratory Risk: {reason}\n")
        self.output.insert(tk.END, f"Industrial Risk Index: {industrial_risk}/10\n")

    # =================================================
    # SHOW HEALTH IMPACT (5-year stats)
    # =================================================
    def show_health_impact(self):
        city = self.city_var.get()
        if not city:
            self.output.insert(tk.END, "⚠ Select a city first!\n")
            return

        record = get_city_records(self.dataset, city)[0]
        stats = record["health_stats"]

        self.output.insert(tk.END, f"\nHEALTH IMPACT ANALYSIS for {city}\n")
        self.output.insert(tk.END, "-"*60 + "\n")
        self.output.insert(tk.END, format_health_stats(stats))
        avg_aqi = average_aqi(self.dataset, city)
        self.output.insert(tk.END, f"\nCurrent AQI: {avg_aqi}\n")
        self.output.insert(tk.END, f"Advice: {health_advice(avg_aqi)}\n")

    # =================================================
    # SHOW CITY RISK RATING (ASCII GRAPH)
    # =================================================
    def show_city_risk(self):
        if not self.dataset:
            self.output.insert(tk.END, "⚠ Load data first!\n")
            return

        self.output.insert(tk.END, "\nCITY RISK RATING (AQI + Industrial)\n")
        self.output.insert(tk.END, "-"*70 + "\n")

        risk_data = {}
        for city in self.cities:
            avg_aqi = average_aqi(self.dataset, city)
            industrial_score = city_industrial_risk(self.dataset, city)
            total_risk = avg_aqi + (industrial_score * 20)
            risk_data[city] = total_risk

        max_val = max(risk_data.values())
        for city, val in sorted(risk_data.items(), key=lambda x: x[1], reverse=True):
            bar = ascii_bar(val, max_val)
            self.output.insert(tk.END, f"{city:<10} | {bar} {val}\n")

    # =================================================
    # FUTURE AQI PREDICTION (BAR GRAPH + Clear Numbers)
    # =================================================
    def show_future_prediction(self):
        city = self.city_var.get()
        if not city:
            messagebox.showwarning("Select City", "Please select a city first!")
            return

        # Generate demo future predictions (next 5 years)
        avg_aqi = average_aqi(self.dataset, city)
        years = [f"Year {i}" for i in range(1, 6)]
        future_aqi = [max(0, avg_aqi + random.randint(-10, 15)) for _ in range(5)]

        # Display clear numbers in the output
        self.output.insert(tk.END, f"\nFUTURE AQI PREDICTIONS for {city} (Next 5 Years)\n")
        self.output.insert(tk.END, "-"*60 + "\n")
        for year, aqi in zip(years, future_aqi):
            self.output.insert(tk.END, f"{year}: {aqi}\n")

        # Plot bar graph in a new window
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.bar(years, future_aqi, color='orange')
        for i, v in enumerate(future_aqi):
            ax.text(i, v + 1, str(v), ha='center', fontweight='bold')
        ax.set_title(f"Future AQI Predictions for {city}")
        ax.set_ylabel("Predicted AQI")
        ax.set_xlabel("Year")
        ax.grid(axis='y', linestyle='--', alpha=0.7)

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)


# =====================================================
# RUN APP
# =====================================================
if __name__ == "__main__":
    root = tk.Tk()
    AQIDashboardGUI(root)
    root.mainloop()
