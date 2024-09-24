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
        self.farms = []
        self.leafUserId = None
        self.farmId = None


    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        if not self.users:
            self.params[0].filter.list = []
            return

        usersFilter = [user["name"] for user in self.users]
        usersFilter.sort()
        self.params[0].filter.list = usersFilter
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        if self.params[0].altered and self.params[0].value:
            self.params[1].setWarningMessage(str(len(self.users)))
            self.leafUserId = self.searchLeafUserByName(self.params[0].value)
            self.params[2].value = self.leafUserId
            self.farms = self.getAllFarms(self.leafUserId)
            farmsFilter = []
            if self.farms:
                for farm in self.farms:
                    if "name" in farm:
                        farmsFilter.append(farm["name"])
                        continue
                    
                    if "providerFarmName" in farm:
                        farmsFilter.append(farm["providerFarmName"])
                        continue
                farmsFilter.sort()
            self.params[1].filter.type = "ValueList"
            self.params[1].filter.list = farmsFilter
        
        if self.params[1].altered and self.leafUserId and self.params[1].value:
            self.farmId = self.searchFarmByName(self.params[1].value)
            self.params[3].value = self.farmId

        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        self.params[0].clearMessage()
        if not self.users:
            self.params[0].setWarningMessage("No users available.")
        return
    
    def isLicensed(self):
         # set tool isLicensed.
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
    
    def getAllGrowers(self, leaf_user_id):
        all_growes = []
        page = 0
        endpoint = f'https://api.withleaf.io/services/fields/api/growers?leafUserId={leaf_user_id}'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}


        while True:
            params = {'page': page, 'size': 100}
            response = requests.get(endpoint, headers=headers, params=params)


            if response.status_code != 200:
                return None


            all_growes.extend(response.json())
            if len(all_growes) >= int(response.headers.get('X-Total-Count', 0)):
                return all_growes

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
    
    def searchLeafUserByName(self, name):
        if not self.users:
            return None

        for user in self.users:
            if name == user["name"]:
                return user["id"]
        
        return None

    def searchFarmByName(self, name):
        if not self.farms:
            return None

        for farm in self.farms:
            if "name" in farm and name == farm["name"]:
                return farm["id"]
            
            if "providerFarmName" in farm and name == farm["providerFarmName"]:
                return farm["id"]
        
        return None