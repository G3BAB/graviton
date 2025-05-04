# TO DO:
# 1. Ask the user if lat / lon in degrees/radians (or another)

import sys
from utils.setup_handler import interactive_setup, config_setup, load_from_shapefile
from utils.calculation_handler import Measurement_point, initial_corrections

import os
import geopandas as gpd

def save_results_to_shapefile(original_path, results_dict):
    """Adds the corrections to the shapefile as new columns"""

    gdf = gpd.read_file(original_path)

    sample_result = next(iter(results_dict.values()))
    result_keys = sample_result.keys()

    # Match id, combine data
    for key in result_keys:
        gdf[key] = None

    for idx, row in gdf.iterrows():
        point_id = str(row['id'])
        if point_id in results_dict:
            for key in result_keys:
                gdf.at[idx, key] = results_dict[point_id][key]

    # Save as a new file
    base, ext = os.path.splitext(original_path)
    new_path = base + "_gravcor" + ext
    gdf.to_file(new_path)
    print(f"\nSaved corrected shapefile to: {new_path}")


def main():
    if "-c" in sys.argv:
        print("Config mode enabled.")
        filepath, planet, method_config = config_setup()
    else:
        filepath, planet, method_config = interactive_setup()

    points = load_from_shapefile(filepath)
    results = initial_corrections(points, planet, method_config)

    save_results_to_shapefile(filepath, results)

if __name__ == "__main__":
    main()
