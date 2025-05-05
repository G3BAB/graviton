# Graviton - A Gravity Correction Calculator

This script provides a quick way to calculate gravity corrections based on geospatial data stored in a Shapefile.

## 📄 Requirements for Input Shapefile

The Shapefile must include the following fields:

- **Longitude** (in degrees)
- **Latitude** (in degrees)
- **Elevation** (in meters)
- **Gravity measurement** (in mGals)

## ⚙️ Features

- Choose from multiple gravity correction methods depending on your needs.
- Interactive setup interface.
- More automated configuration via a config file **coming soon**.
- Designed to be extensible — new correction methods will be added over time.

## 🧮 Calculations Performed

The current version supports the following gravity-related calculations:

- **Normal gravity** based on latitude
- **Free-air correction**
- **Atmospheric correction**
- **Bouguer plate correction**
- **Final gravity anomaly**

> **Note:** Support for **topographic anomaly** will be added in the future.


## Known Issues

- **Automatic field detection cannot detect latitude field**
