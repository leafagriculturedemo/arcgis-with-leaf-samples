"""
Search for images from a selected satellite field

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import arcpy
from datetime import datetime
from datetime import timedelta
import os
import requests
import tempfile
import uuid

def get_leaf_token():
    """
    Retrieves from the current workspace the token created after authentication

    Returns:
    - str: The Leaf token. 'None' if it is not available.
    """
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

def downloadSatelliteImage(TOKEN: str, url: str) -> str:
    """
    Download a satellite image

    Parameters:
    - TOKEN (str): The session Leaf token
    - url (str): The image download url

    Returns:
    - str: The output path of the downloaded image
    """
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(url, headers=headers)
    
    path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    if not os.path.exists(path):
        os.makedirs(path)
    output_path = os.path.join(path, url.rsplit('/', 1)[-1])
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


if __name__ == "__main__":
    TOKEN = get_leaf_token()
    if not TOKEN:
        raise Exception("Please authenticate with Leaf again")

    url = arcpy.GetParameterAsText(5)
    
    if not url:
        raise Exception("Error fetching the image URL.")

    image = downloadSatelliteImage(TOKEN, url)
    arcpy.SetParameterAsText(6, image)