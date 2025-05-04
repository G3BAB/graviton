from math import radians
import utils.correction_calculations as cc
import json

class Planet:
    def __init__(self, r_mean, r_equator, r_pole, mean_crust_density):
        self.r_mean = r_mean
        self.r_equator = r_equator
        self.r_pole = r_pole
        self.mean_crust_density = mean_crust_density
        self.flattening = ( r_equator - r_pole ) / r_equator

class Point:
    def __init__(self, id, lat, lon, h):
        self.id = id
        self.lat = radians(float(lat))
        self.lon = radians(float(lon))
        self.h = float(h)

class Measurement_point(Point):
    def __init__(self, id, lat, lon, h, measurement, corrected_measurement):
        super().__init__(id, lat, lon, h)
        self.measurement = measurement
        self.corrected_measurement = corrected_measurement

"""def load_correction_config(config_path="config.cfg"):
    config = configparser.ConfigParser()
    config.read(config_path)

    methods = {

        "NORMAL_GRAVITY": int(config["CALCULATIONS"].get("NORMAL_GRAVITY", 0)),
        "FREE_AIR": int(config["CALCULATIONS"].get("FREE_AIR", 0)),
        "ATMOSPHERIC": int(config["CALCULATIONS"].get("ATMOSPHERIC", 0)),
        "BOUGUER": int(config["CALCULATIONS"].get("BOUGUER", 0)),
    }
    return methods"""

def load_planet(planet_name, filepath="planets_definitions.json"):
    with open(filepath, "r") as f:
        data = json.load(f)
        if planet_name not in data:
            raise ValueError(f"Planet '{planet_name}' not found in {filepath}.")
        p = data[planet_name]
        return Planet(
            r_mean=p["r_mean"],
            r_equator=p["r_equator"],
            r_pole=p["r_pole"],
            mean_crust_density=p["mean_crust_density"]
        )

def initial_corrections(measurement_points, planet, method_config):
    results = {point.id: {} for point in measurement_points}

    # === NORMAL GRAVITY ===
    match method_config.get("NORMAL_GRAVITY", -1):
        case 0:
            for point in measurement_points:
                results[point.id]["normal_gravity"] = cc.calc_gravity_from_latitude_GRS80(point)
        case _:
            for point in measurement_points:
                results[point.id]["normal_gravity"] = 0.0

    # === FREE AIR ===
    match method_config.get("FREE_AIR", -1):
        case 0:
            for point in measurement_points:
                results[point.id]["free_air_correction"] = cc.calc_free_air_simplified(point)
        case 1:
            for point in measurement_points:
                results[point.id]["free_air_correction"] = cc.calc_free_air_precise(point)
        case _:
            for point in measurement_points:
                results[point.id]["free_air_correction"] = 0.0

    # === ATMOSPHERIC ===
    match method_config.get("ATMOSPHERIC", -1):
        case 0:
            for point in measurement_points:
                results[point.id]["atmospheric_correction"] = cc.calc_atmospheric(point)
        case _:
            for point in measurement_points:
                results[point.id]["atmospheric_correction"] = 0.0

    # === BOUGUER ===
    match method_config.get("BOUGUER", -1):
        case 0:
            for point in measurement_points:
                results[point.id]["bouguer_correction"] = cc.calc_bouguer_spherical(point, planet)
        case 1:
            for point in measurement_points:
                results[point.id]["bouguer_correction"] = cc.calc_bouguer_plate(point, planet)
        case _:
            for point in measurement_points:
                results[point.id]["bouguer_correction"] = 0.0

    # === FINAL ANOMALY ===
    for point in measurement_points:
        r = results[point.id]
        r["anomaly"] = (
            point.measurement
            + r["free_air_correction"]
            + r["atmospheric_correction"]
            - r["bouguer_correction"]
            - r["normal_gravity"]
        )

    return results


