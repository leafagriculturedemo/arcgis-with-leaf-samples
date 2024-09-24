"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
from datetime import datetime
from datetime import timedelta
import os
import requests
import tempfile
import uuid
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
def is_valid_field(TOKEN, fieldId):
    if not fieldId:
        return False
    endpoint = f'https://api.withleaf.io/services/satellite/api/fields/{fieldId}'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(endpoint, headers=headers)
    return response.status_code == 200
def dateParametersValidation(startTime, endTime):
    if startTime:
        if startTime.strftime("%d/%m/%Y") == '30/12/1899':
            raise Exception("Invalid startTime.")
        if startTime > datetime.now():
            raise Exception("Invalid startTime." )
    if endTime:
        if endTime.strftime("%d/%m/%Y") == '30/12/1899':
            raise Exception("Invalid endTime.")
        if endTime > datetime.now():
            raise Exception("Invalid endTime.")
    if startTime and endTime:
        if startTime > endTime:
            raise Exception("Start time must be before the end time.")
        
        diff_month = (endTime.year - startTime.year) * 12 + endTime.month - startTime.month
        if diff_month > 6:
            raise Exception("For this process, the maximum allowed period is 6 months.")
def parse_date(date_str):
    return date_str.strftime('%Y-%m-%d')
def get_satellite_images(TOKEN, field, startTime, endTime):
    all_images = []
    page = 0
    endpoint = f'https://api.withleaf.io/services/satellite/api/fields/{field}/processes'
    headers = {'Authorization': f'Bearer {TOKEN}'}
    while True:
        params = {
            'startDate': startTime,
            'endDate': endTime,
            'sort': 'date,desc',
            'page': page,
            'size': 100,
            'minCoverage': 90,
            'maxClouds': 0}
        
        response = requests.get(endpoint, headers=headers, params=params)
        if not response.ok:
            return None
        all_images.extend(response.json())
        if len(all_images) >= int(response.headers.get('X-Total-Count', 0)):
            return all_images
        page += 1
def get_best_recent_image(images):
    if not images:
        return None
    
    best = images[0]
    for image in images:
        if image["clouds"] < best["clouds"]:
            best = image
        
        if best["clouds"] == 0:
            return best
    
    return best
def download_satellite_image(TOKEN, url, file_name=None):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(url, headers=headers)
    
    path = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    if not os.path.exists(path):
        os.makedirs(path)
    
    if not file_name:
        file_name = url.rsplit('/', 1)[-1]
    output_path = os.path.join(path, file_name)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path
def get_image_download_urls(images):
    img = {}
    for link in images:
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
    return img
def download_best_image(TOKEN, fieldId, startTime, endTime, imageType):
    images = get_satellite_images(TOKEN, fieldId, startTime, endTime)
    if not images:
        return None
    best_image = images[0]#get_best_recent_image(images)
    image_date = best_image["date"].rsplit("T")[0]
    field_name = f"{fieldId}-{image_date}-{imageType}.tif"
    '''if best_image["clouds"] > 50:
        arcpy.AddWarning(f'Best image available has {best_image["clouds"]}% of cloud coverage.')'''
    
    urls = get_image_download_urls(best_image["images"])
    if imageType not in urls:
        raise Exception("Unsupported image type")
    url = urls[imageType]
    return download_satellite_image(TOKEN, url, field_name)
if __name__ == "__main__":
    try:
        TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ3aXRobGVhZmludGVncmF0aW9uQHNtYnNjLmNvbSIsImF1dGgiOiJST0xFX1VTRVIiLCJpYXQiOjE3MjA3MjU0MjAsImV4cCI6MTcyMTkxMTgyMH0.mrAJ-oVb41hHvv4JSsovTZ15TgwAD649CvqyJLdIOuqVtChsBTGKT__H9quxP-B_NJUeoV-CVRfbB11bI4SbZA"#get_leaf_token()
        if not TOKEN:
            raise Exception("Please authenticate with Leaf again")
        
        fieldId = arcpy.GetParameterAsText(0)
        arcpy.AddMessage(f"Field '{fieldId}'")
        if not is_valid_field(TOKEN, fieldId):
            raise Exception(f"The {fieldId} does not exist.")
        
        startTime = arcpy.GetParameter(1)
        endTime = arcpy.GetParameter(2)
        dateParametersValidation(startTime, endTime)
        startTime = parse_date(startTime)
        endTime = parse_date(endTime)
        imageType = arcpy.GetParameterAsText(3)
        
        image = download_best_image(TOKEN, fieldId, startTime, endTime, imageType)
        if image:
            arcpy.SetParameterAsText(4, image)
        else:
            arcpy.AddWarning(f"No image found for '{fieldId}' on given dates")
    except Exception as e:
        arcpy.AddError(str(e))
