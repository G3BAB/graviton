# If you want to look at nice looking code, please select a different module

import configparser
import tkinter as tk
from tkinter import filedialog
import json
import os
import re
import geopandas as gpd
from utils.calculation_handler import Measurement_point, Planet, load_planet

# Keeps config variables, their values an their labels
METHODS = {
    "NORMAL_GRAVITY": {
        "label": "Normal gravity model",
        "options": ["GRS80"]
    },
    "ATMOSPHERIC": {
        "label": "Atmospheric correction model",
        "options": ["Standard atmospheric model"]
    },
    "BOUGUER": {
        "label": "Bouguer correction method",
        "options": ["Spherical", "Plate"]
    },
    "FREE_AIR": {
        "label": "Free-air correction method",
        "options": ["Simplified", "Precise"]
    }
}

def resolve_attribute_column(attribute_name, columns, keywords):
    lower_columns = [col.lower() for col in columns]
    matches = [columns[i] for i, col in enumerate(lower_columns) if any(re.search(kw, col) for kw in keywords)]

    if len(matches) == 1:
        return matches[0]
    else:
        print(f"\nCould not detect a column for '{attribute_name}'.")
        selected_idx = select_from_list(f"Select column for {attribute_name} manually:", columns)
        return columns[selected_idx]


def select_file():
    root = tk.Tk()
    root.withdraw()
    filetypes = [("Shapefiles", "*.shp"), ("All files", "*.*")]
    filepath = filedialog.askopenfilename(title="Select data file", filetypes=filetypes)
    return filepath


def select_from_list(prompt, options, default=None):
    """Common 'select by number' interface"""
    while True:
        print(f"\n{prompt}")
        for idx, opt in enumerate(options):
            print(f"{idx + 1}. {opt}")
        if default is not None:
            print(f"Press ENTER to use default: '{options[default]}'")
        choice = input("\nInput the number to select (or 'Q' to quit): ").strip()
        if choice.lower() == "q":
            print("Exiting.")
            exit(0)
        if not choice and default is not None:
            return default
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
        print("Invalid selection. Try again (or 'Q' to quit).")


def interactive_setup():
    print("=== Gravity Correction Interactive Setup ===")
    input("Press ENTER to choose your CSV or SHP file...")
    filepath = select_file()
    print(f"Selected file: {filepath}")

    with open("planets_definitions.json", "r") as f:
        planet_data = json.load(f)

    planets = list(planet_data.keys()) + ["Custom (enter manually)"]
    planet_choice = select_from_list("Select a planet:", planets)

    if planet_choice == len(planets) - 1:
        print("\nEnter custom planet parameters:")
        r_mean = float(input("Mean radius (m): "))
        r_equator = float(input("Equatorial radius (m): "))
        r_pole = float(input("Polar radius (m): "))
        mean_crust_density = float(input("Mean crust density (kg/m^3): "))
        planet = Planet(r_mean, r_equator, r_pole, mean_crust_density)
    else:
        planet = load_planet(planets[planet_choice])

    method_config = {}
    for key, data in METHODS.items():
        choice = select_from_list(data["label"], data["options"])
        method_config[key] = choice

    return filepath, planet, method_config


def config_setup(config_path="config.cfg"):
    config = configparser.ConfigParser()
    config.read(config_path)

    # === FILEPATH ===
    filepath = config["INPUT"].get("file", "").strip()
    if not filepath or not os.path.exists(filepath):
        print("[Config] Invalid or missing file path.")
        input("Press ENTER to choose file manually")
        filepath = select_file()

    # === PLANET ===
    planet_name = config["PLANET"].get("name", "").strip()
    with open("planets_definitions.json", "r") as f:
        planet_data = json.load(f)
    planets = list(planet_data.keys())

    if planet_name not in planets:
        print(f"[Config] Invalid planet name: '{planet_name}'")
        idx = select_from_list("Select a valid planet:", planets + ["Custom (enter manually)"])
        if idx == len(planets):
            print("\nEnter custom planet parameters:")
            r_mean = float(input("Mean radius (m): "))
            r_equator = float(input("Equatorial radius (m): "))
            r_pole = float(input("Polar radius (m): "))
            mean_crust_density = float(input("Mean upper crust density (kg/m^3): "))
            planet = Planet(r_mean, r_equator, r_pole, mean_crust_density)
        else:
            planet = load_planet(planets[idx])
    else:
        planet = load_planet(planet_name)

    # === METHODS ===
    method_config = {}
    for method, options in METHODS.items():
        try:
            choice = int(config["CALCULATIONS"].get(method, "").strip())
            if choice < 0 or choice >= len(options):
                raise ValueError()
        except:
            print(f"[Config] Invalid {method} method in config.")
            choice = select_from_list(f"Choose {method} method:", options)
        method_config[method] = choice

    return filepath, planet, method_config


def load_from_shapefile(filepath):
    """Loads data from a shapefile and attempts to map column names to attributes"""
    gdf = gpd.read_file(filepath)
    columns = gdf.columns.tolist()

    attribute_keywords = {
        "id": [r"id", r"point.*id"],
        "lat": [r"lat", r"latitude", r"y"],
        "lon": [r"lon", r"long", r"longitude", r"x"],
        "h": [r"elev", r"height", r"alt"],
        "measurement": [r"meas", r"grav", r"value", r"g_mgal", r"reading"]
    }

    assigned_fields = {}
    for attr, keywords in attribute_keywords.items():
        assigned_fields[attr] = resolve_attribute_column(attr, columns, keywords)

    # Showcase a preview of the attribute pairing
    preview_count = min(3, len(gdf))
    print("\nPreview of attribute assignment and sample data:\n")

    attributes = list(assigned_fields.keys())
    columns = [assigned_fields[attr] for attr in attributes]

    preview_rows = min(preview_count, len(gdf))
    sample_data = [
        [str(gdf.iloc[i][assigned_fields[attr]]) for attr in attributes]
        for i in range(preview_rows)
    ]

    col_widths = [max(len(str(val)) for val in [attr, col] + [row[i] for row in sample_data]) + 2 for i, (attr, col) in enumerate(zip(attributes, columns))]
    label_col_width = max(len("ASSIGNED COLUMN:"), len(str(preview_rows))) + 2

    
    def format_row(label, row_data):
        label_str = f"{label:<{label_col_width}}"
        row_strs = [f"{val:<{col_widths[i]}}" for i, val in enumerate(row_data)]
        return "| " + label_str + "| " + " | ".join(row_strs) + " |"

    print(format_row("ATTRIBUTE:", attributes))
    print(format_row("ASSIGNED COLUMN:", columns))

    for idx, row in enumerate(sample_data, start=1):
        print(format_row("DATA " + str(idx) + ".", row))

    while True:
        confirm = input("\nPress ENTER to confirm column assignments, or type 'Q' to quit: ").strip()
        if confirm.lower() == "q":
            print("Exiting.")
            exit(0)
        elif confirm == "":
            break
        else:
            print("Invalid input. Press ENTER to confirm, or Q to quit.")

    measurement_points = []
    for _, row in gdf.iterrows():
        point = Measurement_point(
            id=str(row[assigned_fields["id"]]),
            lat=row[assigned_fields["lat"]],
            lon=row[assigned_fields["lon"]],
            h=row[assigned_fields["h"]],
            measurement=row[assigned_fields["measurement"]],
            corrected_measurement=None
        )
        measurement_points.append(point)

    return measurement_points
