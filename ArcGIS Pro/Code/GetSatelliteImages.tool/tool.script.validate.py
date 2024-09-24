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
        self.satelliteImages = {}
        self.errors = []

        self.params = arcpy.GetParameterInfo()
        self.TOKEN = self.getLeafToken()
        self.paramInField = 0
        self.paramInStartTime = 1
        self.paramInEndTime = 2
        self.paramInAvailability = 3
        self.paramInImageType = 4
        self.paramOutURL = 5
        self.paramOutImage = 6


    def initializeParameters(self):
        # Customize parameter properties. 
        # This gets called when the tool is opened.
        satelllite_fields = []
        if self.TOKEN:
            satelllite_fields = self.getAllSatelliteFields()
            satelllite_fields =  [f["externalId"] for f in satelllite_fields]
            satelllite_fields.sort()
        self.params[self.paramInField].filter.type = "ValueList"
        self.params[self.paramInField].filter.list = satelllite_fields
        self.params[self.paramInImageType].filter.list = []

    def updateParameters(self):
        # Modify parameter values and properties.
        # This gets called each time a parameter is modified, before 
        # standard validation.
        if self.params[self.paramInField].altered or self.params[self.paramInStartTime].altered or self.params[self.paramInEndTime].altered:
            if self.params[self.paramInField].value and self.params[self.paramInStartTime].value and self.params[self.paramInEndTime].value:  
                images = None

                #dates_validation_errors = self.date_validation(self.params[self.paramInStartTime].value, self.params[self.paramInEndTime].value)
                #if not dates_validation_errors:
                startTime = self.params[self.paramInStartTime].value.strftime('%Y-%m-%d')
                endTime = self.params[self.paramInEndTime].value.strftime('%Y-%m-%d')
                images = self.getSatelliteImages(self.params[self.paramInField].value, startTime, endTime)
                
                if images:
                    for image in images:
                        img = {}
                        for link in image["images"]:
                            ortho = False
                            if link["downloadUrl"].endswith("RGB.tif"):
                                if "assetType" in link:
                                    if ortho:
                                        continue
                                    img["RGB"] = link["downloadUrl"]
                                    if link["assetType"] == "ortho_visual":
                                        ortho  = True  
                                else: #Sentinel image
                                    img["RGB"] = link["downloadUrl"]
                                continue
                            
                            if link["downloadUrl"].endswith("NDVI_color.tif"):
                                img["NDVI (colored)"] = link["downloadUrl"]
                                continue
                            
                            if link["downloadUrl"].endswith("NDVI.tif"):
                                img["NDVI"] = link["downloadUrl"]
                                continue
                            
                            if link["downloadUrl"].endswith("NDRE_color.tif"):
                                img["NDRE (colored)"] = link["downloadUrl"]
                                continue
                            
                            if link["downloadUrl"].endswith("NDRE.tif"):
                                img["NDRE"] = link["downloadUrl"]
                                continue

                            if link["downloadUrl"].endswith("biomass_color.tif"):
                                img["Biomass (colored)"] = link["downloadUrl"]
                                continue

                            if link["downloadUrl"].endswith("biomass.tif"):
                                img["Biomass"] = link["downloadUrl"]
                                continue
                                                        
                            if link["type"] == "tif_multiband":
                                img["Multiband"] = link["downloadUrl"]
                                continue

                            if "assetType" in link and link["assetType"] == "ortho_udm2":
                                img["Usable Data Mask (UDM)"] = link["downloadUrl"]
                                continue

                        image_key = f'{image["date"]} - ☁️ {image["clouds"]}%'
                        self.satelliteImages[image_key] = img

                    imagesAvailable = list(self.satelliteImages.keys())
                    self.params[self.paramInAvailability].filter.type = "ValueList"
                    self.params[self.paramInAvailability].filter.list = imagesAvailable
                    self.params[self.paramInImageType].filter.type = "ValueList"
                    img_types = []
                    if self.params[self.paramInAvailability].value:
                        img_types = list(self.satelliteImages[self.params[self.paramInAvailability].value].keys())
                        img_types.sort()
                    self.params[self.paramInImageType].filter.list = img_types

                else:
                    self.params[self.paramInAvailability].value = None
                    self.params[self.paramInAvailability].filter.list = []
                    self.params[self.paramInImageType].value = None
                    self.params[self.paramInImageType].filter.list = []
        
        if self.params[self.paramInAvailability].altered or self.params[self.paramInImageType].altered:
            if self.satelliteImages and self.params[self.paramInAvailability].value and self.params[self.paramInImageType].value:
                self.params[self.paramOutURL].value = self.satelliteImages[self.params[self.paramInAvailability].value][self.params[self.paramInImageType].value]

        return

    def updateMessages(self):
        self.params[0].clearMessage()
        self.params[3].clearMessage()

        if not self.TOKEN:
            self.params[0].setErrorMessage("Missing Leaf account information.")
            return

        date_error = self.date_validation(self.params[self.paramInStartTime].value, self.params[self.paramInEndTime].value)
        #self.errors.append((self.paramInAvailability, "No images found for the given filter."))
        if date_error:
            self.params[date_error[0]].setErrorMessage(date_error[1])
        
        '''if self.params[self.paramInField].value and self.params[self.paramInStartTime].value and self.params[self.paramInEndTime].value:  
            if not self.params[self.paramInAvailability].filter.list:
                self.params[self.paramInAvailability].setWarningMessage("No images found for the given filter.")'''


    def isLicensed(self):
         # set tool isLicensed.
        return self.TOKEN is not None

    # def postExecute(self):
    #     # This method takes place after outputs are processed and
    #     # added to the display.
    # return
    def date_validation(self, startTime, endTime):
        if startTime:
            if startTime.strftime("%d/%m/%Y") == '30/12/1899':
                return (self.paramInStartTime, "Invalid date.")

            if startTime > datetime.now():
                return (self.paramInStartTime, "Invalid date. It must be a date in the past." )

        if endTime:
            if endTime.strftime("%d/%m/%Y") == '30/12/1899':
                return (self.paramInEndTime, "Invalid date.")

            if endTime > datetime.now():
                return (self.paramInEndTime, "Invalid date. It must be a date in the past." )

        if startTime and endTime:
            if startTime > endTime:
                return (self.paramInEndTime, "Start time must be before the end time.")
            
            if self.diff_month(startTime, endTime) > 6:
                return (self.paramInEndTime, "For this search, the maximum allowed period is 6 months.")
    
    def diff_month(self, startTime, endTime):
        return (endTime.year - startTime.year) * 12 + endTime.month - startTime.month

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
    
    def getSatelliteImages(self, field, startTime, endTime):
        all_images = []
        page = 0
        endpoint = f'https://api.withleaf.io/services/satellite/api/fields/{field}/processes'
        headers = {'Authorization': f'Bearer {self.TOKEN}'}

        while True:
            params = {
                'startDate': startTime,
                'endDate': endTime,
                'sort': 'date,desc',
                'page': page,
                'size': 100,
                'minCoverage': 90}
            #maxClouds
            response = requests.get(endpoint, headers=headers, params=params)

            if not response.ok:
                return None


            all_images.extend(response.json())
            if len(all_images) >= int(response.headers.get('X-Total-Count', 0)):
                return all_images

            page += 1