import arcpy
from datetime import datetime, timedelta


class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.
    
    def __init__(self):
        # set self.params for use in other function
        self.params = arcpy.GetParameterInfo()


    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        today = datetime.today()
        self.params[1].value = today - timedelta(days=7)
        self.params[2].value = today
        return

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        return

    def updateMessages(self):
        return


    def isLicensed(self):
         # set tool isLicensed.
        return True