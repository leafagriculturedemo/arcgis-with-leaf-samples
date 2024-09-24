from datetime import datetime
from datetime import timedelta
import os
import arcpy

class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()
        self.TOKEN = self.getLeafToken()

    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        self.params[1].filter.type = "ValueList"
        self.params[1].filter.list = []
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        if self.params[0].altered:
            layer = self.params[0].value
            self.params[1].filter.list = self.getLayerColumnNames(layer)
        return

    def updateMessages(self):
        # Customize messages for the parameters.
        # This gets called after standard validation.
        self.params[3].clearMessage()
        self.params[0].clearMessage()
        if not self.TOKEN:
            self.params[0].setErrorMessage("Missing Leaf account information.")
            return

        if self.params[3].value:
            startTime = self.params[3].value

            if startTime.strftime("%d/%m/%Y") == '30/12/1899':
                self.params[3].setErrorMessage("Invalid date.")
                return

            if startTime > datetime.now():
                self.params[3].setErrorMessage("Invalid date. It must be a date in the past." )
                return

            if startTime < (datetime.now() - timedelta(days= 5 * 365)):
                self.params[3].setErrorMessage("Invalid date. It allows 5 years in past." )
                return
        return

    def isLicensed(self):
         # set tool isLicensed.
        return self.TOKEN is not None

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    # return
    
    def getLayerColumnNames(self, layer):
        fieldnames = [f.name for f in arcpy.ListFields(layer) if f.type == 'String']
        fieldnames.sort()
        return fieldnames
    
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