import arcpy
import requests
from datetime import datetime
from datetime import timedelta
import os

class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()
        self.TOKEN = self.getLeafToken()
        
        self.users = self.getLeafUsers()
        self.leafUserId = None

    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        if not self.users:
            self.params[1].filter.list = []
            return

        usersFilter = [f'{user.get("name")} ({user.get("id")})' for user in self.users]
        usersFilter.sort()
        self.params[1].filter.list = usersFilter
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        if self.params[1].altered and self.params[1].value:
            self.leafUserId = self.getLeafUserId(self.params[1].value)
            self.params[2].value = self.leafUserId
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        return

    def isLicensed(self):
        return self.TOKEN is not None

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    # return

    def getLeafToken(self):
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

    def getLeafUsers(self):
        if not self.TOKEN:
            return None
        all_users = []
        page = 0
        endpoint = 'https://api.withleaf.io/services/usermanagement/api/users'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}


        while True:
            params = {'page': page, 'size': 100}
            response = requests.get(endpoint, headers=headers, params=params)


            if response.status_code != 200:
                return None


            all_users.extend(response.json())
            if len(all_users) >= int(response.headers.get('X-Total-Count', 0)):
                return all_users

            page += 1
    

    def getAllFarms(self, leaf_user_id):
        all_farms = []
        page = 0
        endpoint = f'https://api.withleaf.io/services/fields/api/farms?leafUserId={leaf_user_id}'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}


        while True:
            params = {'page': page, 'size': 100}
            response = requests.get(endpoint, headers=headers, params=params)


            if response.status_code != 200:
                return None


            all_farms.extend(response.json())
            if len(all_farms) >= int(response.headers.get('X-Total-Count', 0)):
                return all_farms

            page += 1
    
    def getLeafUserId(self, name):
        if not name:
            return None
        
        return name.split("(")[-1].replace(")", "")
    
    def getFarmId(self, name):
        if not name:
            return None
        
        return name.split("(")[-1].replace(")", "")