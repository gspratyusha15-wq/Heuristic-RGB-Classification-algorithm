import arcpy
from arcpy.sa import *
import os

# 1. Setup Environment
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# Define Input Variables
layer_name = "May_second_forecast.tif"
map_name = "second forecast"
districts_shp = "INDIA_DISTRICTS_LATEST_2025"
zone_field = "cc"
output_table = "District_Probability_Table"

try:
    # 2. Get the actual file path of the raster layer from the project
    aprx = arcpy.mp.ArcGISProject("CURRENT")
    
    maps = aprx.listMaps(map_name)
    if not maps:
        raise ValueError(f"Could not find map named '{map_name}'.")
    target_map = maps[0]
    
    raster_path = None
    for lyr in target_map.listLayers():
        if lyr.name == layer_name:
            raster_path = lyr.dataSource
            break
            
    if not raster_path:
        raise ValueError(f"Could not find layer '{layer_name}' in the map.")

    print(f"Raster absolute path found: {raster_path}")

    band_count = int(arcpy.management.GetRasterProperties(raster_path, "BANDCOUNT").getOutput(0))
    if band_count < 3:
        raise ValueError(f"Raster has {band_count} band(s). The script requires an RGB (3-band) image.")

    # 3. Access the individual RGB bands using the absolute path
    band_r = Raster(os.path.join(raster_path, "Band_1"))
    band_g = Raster(os.path.join(raster_path, "Band_2"))
    band_b = Raster(os.path.join(raster_path, "Band_3"))

    print("Extracting Zonal Statistics for RGB bands...")
    
    # 4. Calculate Mean values for each band per district
    zonal_r = ZonalStatisticsAsTable(districts_shp, zone_field, band_r, "in_memory/zonal_r", "DATA", "MEAN")
    zonal_g = ZonalStatisticsAsTable(districts_shp, zone_field, band_g, "in_memory/zonal_g", "DATA", "MEAN")
    zonal_b = ZonalStatisticsAsTable(districts_shp, zone_field, band_b, "in_memory/zonal_b", "DATA", "MEAN")

    # 5. Consolidate into a single output table
    print("Consolidating tables...")
    arcpy.management.CopyRows(zonal_r, output_table)
    
    # Add fields to store G, B means, category, AND the new Probability Value
    arcpy.management.AddField(output_table, "MEAN_G", "DOUBLE")
    arcpy.management.AddField(output_table, "MEAN_B", "DOUBLE")
    arcpy.management.AddField(output_table, "Forecast_Category", "TEXT", field_length=50)
    arcpy.management.AddField(output_table, "Probability_Value", "TEXT", field_length=20) # Added Field

    arcpy.management.JoinField(output_table, zone_field, zonal_g, zone_field, ["MEAN"])
    arcpy.management.CalculateField(output_table, "MEAN_G", "!MEAN_1!", "PYTHON3")
    arcpy.management.DeleteField(output_table, "MEAN_1")

    arcpy.management.JoinField(output_table, zone_field, zonal_b, zone_field, ["MEAN"])
    arcpy.management.CalculateField(output_table, "MEAN_B", "!MEAN_1!", "PYTHON3")
    arcpy.management.DeleteField(output_table, "MEAN_1")
    
    arcpy.management.AlterField(output_table, "MEAN", "MEAN_R", "MEAN_R")

    # 6. Classify probabilities and estimate values based on RGB intensity
    print("Classifying categories and probability values...")
    
    with arcpy.da.UpdateCursor(output_table, ["MEAN_R", "MEAN_G", "MEAN_B", "Forecast_Category", "Probability_Value"]) as cursor:
        for row in cursor:
            r, g, b = row[0], row[1], row[2]
            
            if r is None or g is None or b is None:
                row[3] = "No Data"
                row[4] = "N/A"
                cursor.updateRow(row)
                continue

            # Climatological probability (White/Grey pixels)
            if r > 200 and g > 200 and b > 200:
                row[3] = "Climatological"
                row[4] = "33%" # Equal chance
            
            # Below Normal (Yellow to Red)
            elif r > g and r > b:
                row[3] = "Below Normal"
                # If Green is high, it's yellow (low prob). If Green is low, it's red (high prob).
                if g > 180: row[4] = "34-45%"
                elif g > 100: row[4] = "45-55%"
                elif g > 50: row[4] = "55-65%"
                else: row[4] = "> 65%"
                
            # Above Normal (Light Blue to Dark Blue)
            elif b > r and b > g:
                row[3] = "Above Normal"
                # If Red/Green are high, it's light blue (low prob). If low, it's dark blue (high prob).
                avg_rg = (r + g) / 2
                if avg_rg > 180: row[4] = "34-45%"
                elif avg_rg > 100: row[4] = "45-55%"
                elif avg_rg > 50: row[4] = "55-65%"
                else: row[4] = "> 65%"
                
            # Normal (Light Green to Dark Green)
            elif g > r and g > b:
                row[3] = "Normal"
                # If Red/Blue are high, it's light green (low prob). If low, it's dark green (high prob).
                avg_rb = (r + b) / 2
                if avg_rb > 180: row[4] = "34-45%"
                elif avg_rb > 100: row[4] = "45-55%"
                elif avg_rb > 50: row[4] = "55-65%"
                else: row[4] = "> 65%"
                
            else:
                row[3] = "Unclassified"
                row[4] = "Unknown"

            cursor.updateRow(row)

    print(f"Success! Output generated: {output_table}")
    
except Exception as e:
    print(f"An error occurred: {e}")