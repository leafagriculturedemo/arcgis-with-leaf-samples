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

def get_fields(TOKEN, leafUserId, farmId):
    endpoint = f'https://api.withleaf.io/services/fields/api/fields?size=100&leafUserId={leafUserId}'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    if farmId:
        endpoint += f"&farmId={farmId}"

    response = requests.get(endpoint, headers=headers)
    if not response.ok:
        return []
    return (response.headers["X-Total-Count"], response.json())

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
            properties["farmName"] = field["farm"]["name"]
        elif "providerFarmName" in field["farm"]:
            properties["farmName"] = field["farm"]["providerFarmName"]
        properties["farmId"] = field["farmId"]
    else:
        properties["farmName"] = ""
        properties["farmId"] = ""


    if "providerName" in field:
        properties["provider"] = field["providerName"]
    else:
        properties["provider"] = ""

    properties["type"] = field["type"]
    properties["leafUserId"] = field["leafUserId"]
    
    feature["properties"] = properties

    return feature

def features_to_geojson(features):
    geojson = {}
    geojson["type"] = "FeatureCollection"
    geojson["features"] = features

    fileName = f'{str(uuid.uuid4())}.geojson'
    with open(fileName, 'w') as fp:
        json.dump(geojson, fp)
    
    return fileName

def execute(TOKEN, leafUserId, farmId):
    fieldsResult = get_fields(TOKEN, leafUserId, farmId)

    if not fieldsResult or not fieldsResult[1]:
        arcpy.AddWarning("No records found.")
        return
    
    fieldsCount = fieldsResult[0]
    fields = fieldsResult[1]
    features = []

    for field in fields:
        boundary = get_field_boundary(TOKEN, leafUserId, field["id"])
        if not boundary:
            continue
        field["boundary"] = boundary
        if "farmId" in field:
            field["farm"] = get_a_farm(TOKEN, leafUserId, field["farmId"])
    
    for field in fields:
        if "boundary" in field:
            features.append(field_to_feature(field))

    geojson = features_to_geojson(features)
    if len(fields) < int(fieldsCount):
        arcpy.AddWarning(f"The results are filtered. Displaying {len(fields)} from {fieldsCount} fields.")
    return arcpy.conversion.JSONToFeatures(geojson, f"in_memory\\fields", "POLYGON")


if __name__ == "__main__":
    TOKEN = get_leaf_token()
    if not TOKEN:
        raise Exception("Please authenticate with Leaf again")

    leafUserId = arcpy.GetParameterAsText(2)
    if not leafUserId:
        raise Exception("Error fetching the user.")
    farmId = arcpy.GetParameterAsText(3)

    fieldLayer = execute(TOKEN, leafUserId, farmId)
    arcpy.SetParameterAsText(4, fieldLayer)