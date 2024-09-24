import requests
import os
from datetime import datetime
from datetime import timedelta
import arcpy

class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()
        self.TOKEN = self.getLeafToken()

        self.users = []
        self.OPTION_NEW_USER = "New user"
        self.OPTION_EXISTENT_NAME = "Existent user (by Name)"
        self.OPTION_EXISTENT_EXTERNALID = "Existent user (by External ID)"

        self.paramIdxOption = 0
        self.paramIdxExternalId = 1
        self.paramIdxName = 2
        self.paramIdxEmail = 3
        self.paramIdxUser= 4
        self.paramIdxLeafUserId=9

    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        if self.TOKEN:
            #self.params[0].value = self.params[0].filter.list[0]
            self.params[self.paramIdxUser].enabled = False
            self.params[self.paramIdxExternalId].enabled = True
            self.params[self.paramIdxName].enabled = True
            self.params[self.paramIdxEmail].enabled = True
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        option = self.params[self.paramIdxOption].value
        selectedUser = self.params[self.paramIdxUser].value

        if self.params[self.paramIdxOption].altered:
            if option == self.OPTION_NEW_USER:
                self.params[self.paramIdxUser].enabled = False
                self.params[self.paramIdxExternalId].enabled = True
                self.params[self.paramIdxName].enabled = True
                self.params[self.paramIdxEmail].enabled = True
            else:
                self.params[self.paramIdxUser].enabled = True
                self.params[self.paramIdxExternalId].enabled = False
                self.params[self.paramIdxName].enabled = False
                self.params[self.paramIdxEmail].enabled = False
                
                if not self.users:
                    self.users = self.get_leaf_users()
                
                name_options = []
                if self.users:
                    if option == self.OPTION_EXISTENT_NAME:
                        name_options = [user["name"] for user in self.users]
                    elif option == self.OPTION_EXISTENT_EXTERNALID:
                        name_options = [user["externalId"] for user in self.users if user["externalId"]]
                    name_options.sort()
                    
                self.params[self.paramIdxUser].filter.list = name_options 
            
            if self.params[self.paramIdxUser].altered:
                if option == self.OPTION_EXISTENT_NAME:
                    self.params[self.paramIdxLeafUserId].value = self.search_leaf_user_by_name(selectedUser)
                elif option == self.OPTION_EXISTENT_EXTERNALID:
                    self.params[self.paramIdxLeafUserId].value = self.search_leaf_user_by_externalId(selectedUser)
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        self.params[0].clearMessage()
        self.params[self.paramIdxExternalId].clearMessage()

        if not self.TOKEN:
            self.params[0].setErrorMessage("Missing Leaf account information.")
            return
       
        option = self.params[self.paramIdxOption].value

        if self.params[self.paramIdxExternalId].value and option == self.OPTION_NEW_USER:
            user = self.getLeafUserByExernalId(self.params[self.paramIdxExternalId].value)
            if user:
                self.params[self.paramIdxExternalId].setErrorMessage("A user with this external ID already exists.")


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
    
    def get_leaf_users(self):
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
    
    def search_leaf_user_by_name(self, name):
        if not self.users:
            return None

        for user in self.users:
            if name == user["name"]:
                return user["id"]
        
        return None

    def search_leaf_user_by_externalId(self, externalId):
        if not self.users:
            return None

        for user in self.users:
            if externalId == user["externalId"]:
                return user["id"]
        
        return None
    
    def getLeafUserByExernalId(self, externalId):
        endpoint = f'https://api.withleaf.io/services/usermanagement/api/users/?externalId={externalId}'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}

        response = requests.get(endpoint, headers=headers)
        if not response.ok:
            return None
        return response.json()