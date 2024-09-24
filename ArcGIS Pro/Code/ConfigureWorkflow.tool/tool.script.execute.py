"""
Script documentation

- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy


def script_tool(param0, param1):
    """Script code goes below"""

    return


if __name__ == "__main__":

    param0 = arcpy.GetParameterAsText(0)
    param1 = arcpy.GetParameterAsText(1)

    script_tool(param0, param1)
    arcpy.SetParameterAsText(2, "Result")