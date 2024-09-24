"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import tempfile
import uuid
import os
from datetime import datetime
from datetime import timedelta
import zipfile
import requests

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

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), 
                       os.path.relpath(os.path.join(root, file), 
                                       os.path.join(path, '..')))

def upload_fields(TOKEN, leaf_user_id, zip_file):
    endpoint = f'https://api.withleaf.io/services/uploadservice/api/upload?leafUserId={leaf_user_id}'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    files = {'file': open(zip_file, 'rb')}

    response = requests.post(endpoint, headers=headers, files=files)
    response.raise_for_status()
    upload_id = response.json().get("id")
    return upload_id

def execute_tool(leaf_user_id, files):
    token = get_leaf_token()
    if not token:
        raise Exception("Please authenticate with Leaf again")
    
    temp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    fields_dir = os.path.join(temp_dir, "files")
    if not os.path.exists(fields_dir):
        os.makedirs(fields_dir)
        
    for file in files:
        output = os.path.join(fields_dir, f"{file}.shp")
        arcpy.conversion.ExportFeatures(file, output)
    
    zip = os.path.join(temp_dir, 'fields.zip')
    with zipfile.ZipFile(zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipdir(fields_dir, zipf)
    
    uploadId = upload_fields(token, leaf_user_id, zip)
    arcpy.SetParameterAsText(3, uploadId)
    return


if __name__ == "__main__":
    leafUserId = arcpy.GetParameterAsText(2)
    if not leafUserId:
        raise Exception("Error fetching the user.")

    providers = arcpy.GetParameterAsText(0)
    providers =  providers.split(";")
    providers =  list(dict.fromkeys(providers))

    execute_tool(leafUserId, providers)