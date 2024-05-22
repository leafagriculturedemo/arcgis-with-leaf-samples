"""
Authentication with Leaf

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""

import arcpy
import os
import requests

def get_leaf_token(leaf_username: str, leaf_password: str) -> str:
    """
    Authentication to obtain a valid Leaf token.
    More information at https://docs.withleaf.io/docs/authentication.

    Parameters:
    - leaf_username (str): The API Owner username
    - leaf_password (str): The account password

    Returns:
    - str: The Leaf token. 'None' if an error occurs.
    """
    url = "https://api.withleaf.io/api/authenticate"
    data = {'username': leaf_username, 'password': leaf_password}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=data)

    if response.ok:
        token = response.json()["id_token"]
        return token
    else:
        raise Exception("Authentication failed")

def create_leaf_configuration(token: str):
    """
    Stores, in the current workspace, information about the user session,
    such as the token obtained after authentication. This allows for easier recovery later.

    Parameters:
    - token (str): The session Leaf token
    """
    leaf_config_name = "leaf_config"
    config_path = os.path.join(arcpy.env.workspace, leaf_config_name)

    if arcpy.Exists(config_path):
        with arcpy.da.UpdateCursor(config_path, ["config_name", "config_value"], where_clause="config_name='leaf_token'") as cursor:
            for row in cursor:
                row[1] = token
                cursor.updateRow(row)
    else:
        table = arcpy.management.CreateTable(arcpy.env.workspace, leaf_config_name)
        arcpy.AddField_management(table, "config_name", "TEXT", field_length=20)
        arcpy.AddField_management(table, "config_value", "TEXT", field_length=300)
        arcpy.AddField_management(table, "creation_time", "DATE")
        arcpy.AddField_management(table, "update_time", "DATE")

        arcpy.management.EnableEditorTracking(table, creation_date_field="creation_time", last_edit_date_field="update_time")

        with arcpy.da.InsertCursor(table, ["config_name", "config_value"]) as cursor:
            cursor.insertRow(["leaf_token", token])

if __name__ == "__main__":
    username = arcpy.GetParameterAsText(0)
    password = arcpy.GetParameterAsText(1)

    TOKEN = get_leaf_token(username, password)
    create_leaf_configuration(TOKEN)