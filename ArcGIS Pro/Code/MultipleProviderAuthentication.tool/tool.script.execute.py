"""
Script documentation

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

def create_magic_link_with_user_creation(TOKEN, externalId, user, email, settings):
    endpoint = 'https://api.withleaf.io/services/widgets/api/magic-link/provider'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    data = {
        "externalId": externalId,
        "name": user,
        "email": email,
        "expiresIn": 900,
        "settings": settings
    }

    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()["link"]

def create_magic_link(TOKEN, leafUserId, settings):
    endpoint = f'https://api.withleaf.io/services/widgets/api/magic-link/users/{leafUserId}/provider'
    headers = {'Authorization': f'Bearer {TOKEN}'}

    data = {
        "expiresIn": 900,
        "settings": settings
    }

    response = requests.post(endpoint, headers=headers, json=data)
    return response.json()["link"]

def execute(option, externalId, name, email, companyName, companyLogo, headerImage, backgroundColor, leafUserId, TOKEN):
    """Script code goes below"""

    OPTION_NEW_USER = "New user"
    OPTION_EXISTENT_NAME = "Existent user (by Name)"
    OPTION_EXISTENT_EXTERNALID = "Existent user (by External ID)"

    settings = {
        "backgroundColor": backgroundColor,
        "headerImage": headerImage,
        "companyLogo": companyLogo,
        "companyName": companyName,
        "showLeafUserName": "true"
    }
    
    link = None
    if option == OPTION_NEW_USER:
        if not externalId:
            arcpy.AddError("The external ID is required")
            return
        
        if not name:
            arcpy.AddError("The name ID is required")
            return

        if not email:
            arcpy.AddError("The email ID is required")
            return

        link = create_magic_link_with_user_creation(TOKEN, externalId, name, email, settings)
    else:
        if not leafUserId:
            arcpy.AddError("Failed to recover the leaf user info.")
            return
        link = create_magic_link(TOKEN, leafUserId, settings)
    
    if not link:
        arcpy.AddError("Failed to generate the magic link.")
        return
    
    arcpy.SetParameterAsText(10, link)
    if link:
        arcpy.AddMessage(f"Link created: {link} ")
    return


if __name__ == "__main__":
    TOKEN = get_leaf_token()
    if not TOKEN:
        raise Exception("Please authenticate with Leaf again")

    option = arcpy.GetParameterAsText(0)
    externalId = arcpy.GetParameterAsText(1)
    name = arcpy.GetParameterAsText(2)
    email = arcpy.GetParameterAsText(3)

    companyName = arcpy.GetParameterAsText(5)
    companyLogo = arcpy.GetParameterAsText(6)
    headerImage = arcpy.GetParameterAsText(7)
    backgroundColor = arcpy.GetParameterAsText(8)

    leafUserId = arcpy.GetParameterAsText(9)

    execute(option, externalId, name, email, companyName, companyLogo, headerImage, backgroundColor, leafUserId, TOKEN)