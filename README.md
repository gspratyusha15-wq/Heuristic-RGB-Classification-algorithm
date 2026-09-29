# Heuristic-RGB-Classification-algorithm
Automates the extraction of district-level categorical data from unstructured RGB thematic maps, bridging the gap between visual meteorology and localized agricultural planning.
# Spatial Extraction of Climatological Forecasts (SECF)

**Automated Spatial Extraction of Climatological Forecast Probabilities from Unstructured RGB Raster Maps**

## Overview
This repository contains the geoprocessing pipeline and Python (ArcPy) scripts required to reverse-engineer visual thematic forecast maps into structured, administrative-level datasets. It is specifically designed to process unstructured RGB raster maps—such as the India Meteorological Department (IMD) seasonal rainfall probability forecasts—and translate their visual legend gradients into quantitative district-wise tabular data.

This tool was developed to accelerate spatial intelligence gathering for agricultural disaster risk management initiatives. By automating the extraction of district-level metrics, the pipeline supports rapid localized modeling, evaluates inputs for Catchment Resilience Indices (CRI) in river basin management, and aids in formulating targeted agricultural contingencies ahead of the Kharif season.

## Features
* **Multispectral Disaggregation:** Automatically separates georeferenced visual rasters into independent Red, Green, and Blue (RGB) bands.
* **Spatial Feature Engineering:** Utilizes zonal statistics to calculate the mean pixel intensity across complex administrative boundaries (e.g., districts or blocks), mitigating overlaps and compression artifacts.
* **Heuristic RGB Classification:** Applies a rule-based conditional algorithm to determine meteorological categories (Below Normal, Normal, Above Normal) and estimate probability percentiles (e.g., 35-45%, >65%) based on color dominance and saturation.
* **Automated Tabular Output:** Generates a structured GIS table linking administrative zone IDs to standardized climatic probabilities, ready for spatial mapping or database integration.

## Prerequisites
* **ArcGIS Pro** (Tested on version 3.x)
* **Python 3** (Included with ArcGIS Pro)
* **Spatial Analyst Extension** (Required for the `ZonalStatisticsAsTable` function)
* **Input Data:**
  * Georeferenced RGB thematic map (e.g., `May_second_forecast.tif`).
  * Administrative boundary shapefile/feature class (e.g., `INDIA_DISTRICTS_LATEST_2025.shp` with a unique ID field).

## Installation and Usage

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YourUsername/SECF-Forecast-Extractor.git](https://github.com/YourUsername/SECF-Forecast-Extractor.git)

## Setup ArcGIS Pro Environment:

Open your ArcGIS Pro project.

Add your input thematic raster and your district boundary shapefile to the active map frame.

## Execute the Script:

Open the Python Window in ArcGIS Pro (View > Python Window).

Copy the contents of extract_probabilities.py from this repository.

Update the user-defined variables at the top of the script to match your layer names:

layer_name = "Your_Forecast_Raster.tif"
map_name = "Your_Map_Frame_Name"
districts_shp = "Your_District_Boundaries"
zone_field = "Unique_Zone_ID"

Press Enter to run. The script will generate a standalone table named District_Probability_Table in your project's default geodatabase.

## Customizing the Heuristic Algorithm
The default heuristic logic in extract_probabilities.py is calibrated for the standard IMD tercile probability legend (Yellow/Red for Below Normal, Greens for Normal, Blues for Above Normal).

If you are processing maps from a different meteorological agency or evaluating a different climatic index (e.g., drought severity maps), you will need to adjust the RGB thresholding logic in the script's UpdateCursor block to match the specific color ramps of your target legend.
