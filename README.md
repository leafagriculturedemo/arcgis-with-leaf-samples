# Starting to develop for ArcGIS with Leaf API

In this repository, you will find sample codes to use Leaf API resources directly in ArcGIS products, such as ArcGIS Pro, ArcGIS Enterprise, and Experience Builder.

## ArcGIS Pro

One of the ways to consume the data provided by the Leaf API in ArcGIS Pro is through toolboxes using `arcpy`.

In the ArcGIS Pro folder, you will find samples to handle the following data:

- Authentication with Leaf
- Connecting with Ag data providers using Magic Link
- Uploading machine data files using Magic Link
- Field Boundary Management
- Field Operations Management
- Crop Monitoring using Satellite images

### How to use the Leaf sample toolbox

This is a ready-to-use sample, you can use it directly in ArcGIS Pro. You will need a Leaf account to use it and you can create it [here](https://withleaf.io/account/quickstart).

1 - Download the `Leaf Agriculture.atbx` file and move it to a desired folder;
2 - Connect the folder with your Catalog and access it;
3 - Open the toolbox and start with the "Authenticate with Leaf" tool informing your Leaf credentials.

More details about the example tools are available in [this tutorial]().

### How to customize the toolbox 

To edit the files, you can follow [this tutorial](https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/editing-script-tool-code.htm) from the ArcGIS Pro documentation.

The code can be adjusted to suit your needs. Other Leaf products and more details about each endpoint and integrations can be found in our API tutorials and documentation, [available here](https://withleaf.io/for-developers/).

## ArcGIS Enterprise

Another integration option is through [Leaf Alerts](https://docs.withleaf.io/docs/alerts_overview) via webhooks, which means Leaf can notify directly a geoprocessing published in your ArcGIS Enterprise.

### How to configure the integration

The sample file contains a toolbox prepared to be published as geoprocessing.
1 - Open the `Leaf for Enterprise.atbx` toolbox in Pro;
2 - Edit the example script to add the necessary information, and run the tool;
3 - After that, perform the geoprocessing publication procedures as described [in the ArcGIS documentation](https://pro.arcgis.com/en/pro-app/latest/help/analysis/geoprocessing/share-analysis/publishing-geoprocessing-service-in-arcgis-pro.htm).

A complete guide and the next steps for configuring the alert are available in [this Leaf tutorial]().


## ArcGIS Experience Builder

If you are using ArcGIS Experience Builder Developer Edition you can take advantage of Leaf's ready-to-use components through Leaf Link. These are widgets that can be easily adapted for use as ExB widgets.


### How to implement it with Leaf Link

Two options are available: using Leaf Link, which are widgets that can be embedded in your ExB widget, or Magic Link, which will require less code to get ready.

Here are the example details:
