"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import arcpy
import requests
import tempfile
import uuid
import json
from datetime import datetime
from datetime import timedelta
import os

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

def get_field(TOKEN, leafUserId, fieldId):
    endpoint = f'https://api.withleaf.io/services/fields/api/users/{leafUserId}/fields/{fieldId}'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    response = requests.get(endpoint, headers=headers)
    if not response.ok:
        return None
    return response.json()

def get_field_boundary(TOKEN, leafUserId, fieldId):
    endpoint = f'https://api.withleaf.io/services/fields/api/users/{leafUserId}/fields/{fieldId}/boundary'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    response = requests.get(endpoint, headers=headers)
    if not response.ok:
        return None
    return response.json()

def get_a_farm(TOKEN, leafUserId, farmId):
    endpoint = f'https://api.withleaf.io/services/fields/api/users/{leafUserId}/farms/{farmId}'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    response = requests.get(endpoint, headers=headers)
    if not response.ok:
        return None
    return response.json()

def field_to_feature(field):
    feature = {}
    feature["type"] = "Feature"
    feature["geometry"] = field["boundary"]["geometry"]
    
    properties = {}
    properties["id"] = field["id"]
    
    if "name" in field:
        properties["name"] = field["name"]
    elif "providerFieldName" in field:
        properties["name"] = field["providerFieldName"]
    
    properties["area"] = field["boundary"]["area"]["value"]
    properties["areaUnit"] = field["boundary"]["area"]["unit"]
    
    if "farm" in field:
        if "name" in field["farm"]:
            properties["farmName"] = field["name"]
        elif "providerFieldName" in field["farm"]:
            properties["farmName"] = field["providerFieldName"]
        properties["farmId"] = field["farmId"]

    if "providerName" in field:
        properties["provider"] = field["providerName"]
    properties["type"] = field["type"]
    
    feature["properties"] = properties

    return feature

def feature_to_geojson(feature):
    geojson = {}
    geojson["type"] = "FeatureCollection"
    geojson["features"] = [feature]

    fileName = f'{str(uuid.uuid4())}.geojson'
    with open(fileName, 'w') as fp:
        json.dump(geojson, fp)
    
    return fileName

def get_operation_summary(TOKEN, operationId):
    endpoint = f'https://api.withleaf.io/services/operations/api/operations/{operationId}/summary'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    response = requests.get(endpoint, headers=headers)
    return response.json()

def get_operation_stdGeoJSON(TOKEN, operationId):
    endpoint = f'https://api.withleaf.io/services/operations/api/operations/{operationId}/standardGeojson'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    response = requests.get(endpoint, headers=headers)
    return response.json()

def downloadFile(TOKEN, url):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(url, headers=headers)
    
    path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    if not os.path.exists(path):
        os.makedirs(path)
    output_path = os.path.join(path, url.rsplit('/', 1)[-1])
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path

def execute(TOKEN, leafUserId, fieldId, operationId):
    field = get_field(TOKEN, leafUserId, fieldId)
    boundary = get_field_boundary(TOKEN, leafUserId, fieldId)
    fieldLayer = None
    
    if boundary:
        field["boundary"] = boundary
        geojson = feature_to_geojson(field_to_feature(field))

        fieldLayer = arcpy.conversion.JSONToFeatures(geojson, f"in_memory\\fields", "POLYGON")
    
    summaryLayer = None
    summary = get_operation_summary(TOKEN, operationId)
    if summary:
        summaryGeojson = feature_to_geojson(summary)
        summaryLayer = arcpy.conversion.JSONToFeatures(summaryGeojson, f"in_memory\\summary", "POLYGON")
    
    operationLayer = None
    stdGeoJsonUrl = get_operation_stdGeoJSON(TOKEN, operationId)
    if "downloadStandardGeojson" in stdGeoJsonUrl:
        stdGeoJsonFile = downloadFile(TOKEN, stdGeoJsonUrl["downloadStandardGeojson"])
        operationLayer = arcpy.conversion.JSONToFeatures(stdGeoJsonFile, f"in_memory\\operation", "POINT")

    return fieldLayer, summaryLayer, operationLayer


if __name__ == "__main__":
    TOKEN = get_leaf_token()
    if not TOKEN:
        raise Exception("Please authenticate with Leaf again")

    leafUserId = arcpy.GetParameterAsText(3)
    if not leafUserId:
        raise Exception("Error fetching the user.")
    fieldId = arcpy.GetParameterAsText(4)
    operationId = arcpy.GetParameterAsText(5)

    result = execute(TOKEN, leafUserId, fieldId, operationId)
    if result[0]:
        arcpy.SetParameterAsText(6, result[0])
    if result[1]:
        arcpy.SetParameterAsText(7, result[1])
    if result[2]:
        arcpy.SetParameterAsText(8, result[2])