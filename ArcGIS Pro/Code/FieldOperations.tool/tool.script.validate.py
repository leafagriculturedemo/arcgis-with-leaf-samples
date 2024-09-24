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
        self.leaf = LeafAPI()
        self.TOKEN = self.leaf.getLeafToken()

        self.users = self.leaf.getLeafUsers()
        self.fields = []
        self.operations = []
        self.leafUserId = None
        self.fieldId = None
        self.operationId = None


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
            self.leafUserId = self.leaf.searchLeafUserByName(self.params[0].value)
            self.params[3].value = self.leafUserId

            self.fields = self.leaf.getAllFields(self.leafUserId)
            fieldsFilter = []
            if self.fields:
                for field in self.fields:
                    if "name" in field:
                        fieldsFilter.append(field["name"])
                        continue
                    
                    if "providerFieldName" in field:
                        fieldsFilter.append(field["providerFieldName"])
                        continue
                fieldsFilter.sort()
                self.params[1].filter.type = "ValueList"
                self.params[1].filter.list = fieldsFilter

        if self.params[1].altered and self.leafUserId and self.params[1].value:
            self.fieldId = self.leaf.searchFieldByName(self.params[1].value)
            self.params[4].value = self.fieldId

            self.operations = self.leaf.getAllOperations(self.fieldId)
            operationsFilter = []
            for operation in self.operations:
                startTime = operation['startTime'].split(".")[0].replace("Z", "")
                startTime = datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%S")
                formatedStartTime = startTime.strftime("%m/%d/%Y %H:%M")
                operationsFilter.append(f"{operation['type']} ({formatedStartTime}) - {operation['id']}")
            self.params[2].filter.type = "ValueList"
            self.params[2].filter.list = operationsFilter
        
        if self.params[2].altered and self.params[2].value:
            self.operationId = self.params[2].value.split(" - ")[1].strip()
            self.params[5].value = self.operationId


        '''if self.params[1].altered and self.leafUserId and self.params[1].value:
            self.farmId = self.search_farm_by_name(self.params[1].value)
            self.params[3].value = self.farmId'''

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

class LeafAPI:
    def __init__(self):
        self.TOKEN = None
        self.users = None
        self.farms = None
        self.fields = None

    def getLeafToken(self):
        leaf_config_table = "leaf_config"
        fc = os.path.join(arcpy.env.workspace, leaf_config_table)

        if not arcpy.Exists(fc):
            return None
        
        with arcpy.da.SearchCursor(fc, ["config_value", "update_time"],
                           where_clause="config_name='leaf_token'") as cursor:
            for row in cursor:
                self.TOKEN = row[0]
                last_update = row[1]
                date_diff = abs(datetime.now() - last_update)
                if date_diff > timedelta(hours=24):
                    return None
                return self.TOKEN
        
        return None

    def getLeafUsers(self):
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
                self.users = all_users
                return self.users

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
                self.farms = all_farms
                return self.farms

            page += 1
    
    def getAllFields(self, leaf_user_id):
        all_fields = []
        page = 0
        endpoint = f'https://api.withleaf.io/services/fields/api/fields?leafUserId={leaf_user_id}'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}


        while True:
            params = {'page': page, 'size': 100}
            response = requests.get(endpoint, headers=headers, params=params)


            if response.status_code != 200:
                return None


            all_fields.extend(response.json())
            if len(all_fields) >= int(response.headers.get('X-Total-Count', 0)):
                self.fields = all_fields
                return self.fields

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

    def searchFieldByName(self, name):
        if not self.fields:
            return None

        for field in self.fields:
            if "name" in field and name == field["name"]:
                return field["id"]
            
            if "providerFieldName" in field and name == field["providerFieldName"]:
                return field["id"]
        
        return None 
    
    def getAllOperations(self, fieldId):
        endpoint = f'https://api.withleaf.io/services/operations/api/operations?fieldId={fieldId}&size=100&page=0&sort=startTime,desc'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}

        response = requests.get(endpoint, headers=headers)
        return response.json()