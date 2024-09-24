class ToolValidator:
  # Class to add custom behavior and properties to the tool and tool parameters.

    def __init__(self):
        # Set self.params for use in other validation methods.
        self.params = arcpy.GetParameterInfo()

    def initializeParameters(self):
        # Customize parameter properties. This method gets called when the
        # tool is opened.
        self.params[1].filter.type = "ValueList"
        self.params[1].filter.list = []
        return

    def updateParameters(self):
        # Modify the values and properties of parameters before internal
        # validation is performed.
        return

    def updateMessages(self):
        # Modify the messages created by internal validation for each tool
        # parameter. This method is called after internal validation.
        if self.params[0].altered:
            layer = self.params[0].value
            self.params[1].filter.list = self.getLayerColumnNames(layer)
        return

    # def isLicensed(self):
    #     # Set whether the tool is licensed to execute.
    #     return True

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    #     return
    
    def getLayerColumnNames(self, layer):
        fieldnames = [f.name for f in arcpy.ListFields(layer) if f.type == 'String']
        fieldnames.sort()
        return fieldnames
