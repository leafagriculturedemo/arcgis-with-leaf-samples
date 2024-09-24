import arcpy
import json
import requests
import uuid
from datetime import datetime
from datetime import timedelta
import os

class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()
        self.TOKEN = self.getLeafToken()


    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        satelllite_fields = []
        if self.TOKEN:
            satelllite_fields = self.getAllSatelliteFields()
            satelllite_fields =  [f["externalId"] for f in satelllite_fields]
            satelllite_fields.sort()
        self.params[0].filter.type = "ValueList"
        self.params[0].filter.list = satelllite_fields

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        self.params[0].clearMessage()
        if not self.TOKEN:
            self.params[0].setErrorMessage("Missing Leaf account information.")
            return
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

    def getAllSatelliteFields(self):
        all_fields = []
        page = 0
        endpoint = 'https://api.withleaf.io/services/satellite/api/fields'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}


        while True:
            params = {'page': page, 'size': 100}
            response = requests.get(endpoint, headers=headers, params=params)


            if response.status_code != 200:
                return None


            all_fields.extend(response.json())
            if len(all_fields) >= int(response.headers.get('X-Total-Count', 0)):
                return all_fields


            page += 1