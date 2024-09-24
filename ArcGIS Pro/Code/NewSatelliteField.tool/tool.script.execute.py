import arcpy
import json
import requests
import uuid
from datetime import datetime
from datetime import timedelta
import os
import tempfile

def get_leaf_token():
    leaf_config_table = "leaf_config"
    fc = os.path.join(arcpy.env.workspace, leaf_config_table)

    if not arcpy.Exists(fc):
        return None
    
    with arcpy.da.SearchCursor(fc, ["config_value", "update_time"],
                        where_clause="config_name='leaf_token'") as cursor:
        for row in cursor:
            token = row[0]
            last_update = row[1]
            date_diff = abs(datetime.now() - last_update)
            if date_diff > timedelta(hours=24):
                return None
            return token
    
    return None

def create_fields(TOKEN, layer, name_column, providers, start_time):
    feature_count = int(arcpy.GetCount_management(layer).getOutput(0))
    if feature_count == 0:
        arcpy.AddWarning(f"{layer} has no features.")
        return
    
    temp_geojson = os.path.join(tempfile.gettempdir(), f'{str(uuid.uuid4())}.geojson')
    arcpy.conversion.FeaturesToJSON(layer, temp_geojson, geoJSON=True, outputToWGS84='WGS84')

    creation_count = 0

    with open(temp_geojson) as file:
        geojson_data = json.load(file)

        for feature in geojson_data["features"]:
            name = feature["properties"][name_column]

            if not name:
                arcpy.AddWarning(f"Invalid field: empty name on column {name_column}")
                continue

            try:
                geometry = feature["geometry"]
                if geometry["type"] == "Polygon":
                    multipolygon = []
                    multipolygon.append(geometry["coordinates"])
                    geometry["coordinates"] = multipolygon
                    geometry["type"] = "MultiPolygon"

                result = create_satellite_field(TOKEN, name, providers, start_time, geometry)

                if not result.ok:
                    response = result.json()
                    message = f"Failed to create field {name}."
                    
                    if "message" in response:
                        message += f" Detail: {str(response['message'])}."
                    
                    arcpy.AddWarning(message)
                    continue
                creation_count += 1
                arcpy.AddMessage(f"Field {name} created.")
            except Exception as e:
                raise e

    if feature_count > creation_count:
        arcpy.AddWarning(f"Some fields were not created {str(creation_count)}/{str(feature_count)}.")


    
def create_satellite_field(TOKEN, name, providers, start_time, geometry):
    endpoint = 'https://api.withleaf.io/services/satellite/api/fields'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    payload = {
        "externalId": name,
        "providers": providers,
        "geometry": geometry
    }

    if 'planet' in providers:
        payload['assetTypes'] = ['ortho_analytic_8b_sr', 'ortho_udm2', 'ortho_visual']
    
    if start_time:
        payload['startDate'] = start_time


    response = requests.post(endpoint, headers=headers, json=payload)
    return response


if __name__ == "__main__":
    TOKEN = get_leaf_token()
    if not TOKEN:
        raise Exception("Please authenticate with Leaf again")

    layer = arcpy.GetParameterAsText(0)
    name_column = arcpy.GetParameterAsText(1)
    
    providers = arcpy.GetParameterAsText(2)
    providers =  providers.split(";")
    providers =  list(dict.fromkeys(providers))
    
    start_time = arcpy.GetParameter(3)
    try:
        start_time =  start_time.strftime('%Y-%m-%d')
    except:
        arcpy.AddErrorMessage("Invalid date")

    create_fields(TOKEN, layer, name_column, providers, start_time)