"""
Delete a selected satellite field

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import requests
from datetime import datetime
from datetime import timedelta
import os

def get_leaf_token() -> str:
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

def delete_field(TOKEN: str, fieldId: str):
    """
    Delete a satellite field.
    More info at https://docs.withleaf.io/docs/crop_monitoring_endpoints#delete-a-satellite-field.

    Parameters:
    - TOKEN (str): The session Leaf token
    - fieldId (str): The satellite field ID to be deleted
    """
    endpoint = f'https://api.withleaf.io/services/satellite/api/fields/{fieldId}'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    response = requests.delete(endpoint, headers=headers)
    if response.ok:
        arcpy.AddMessage(f'{fieldId} deleted')
    else:
        arcpy.AddErrorMessage(f'Failed to delete {fieldId}.')
    return


if __name__ == "__main__":
    TOKEN = get_leaf_token()
    if not TOKEN:
        raise Exception("Please authenticate with Leaf again")

    field = arcpy.GetParameterAsText(0)

    delete_field(TOKEN, field)