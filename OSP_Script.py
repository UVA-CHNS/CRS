import arcpy
import datetime
#########################INTRODUCTORY INFORMATION#############################################

#This Python script was written by Logan Grant, Master's student at the University of Virginia (E-mail: lng8yx@virginia.edu).
#This script is designed to be run from within an ArcGIS Toolbox (CRS_Toolbox.tbx). The Toolbox was developed in ArcGIS Pro 2.9.1.
#This is a tool for automatically mapping a community's Open Space Preservation (OSP) opportunities, which may be eligible for credits through FEMA's NFIP Community Rating System.

#Last edited: 7/6/2022

#INSTRUCTIONS
# 1. Open a new project with blank map in Arc. You will likely want to save the project to a working directory where other related files and GIS data are located. Note the path to this directory (i.e., C:\Users\John\GIS Work)
# 2. Note the name of the geodatabase you would like to use for storing new data. This will likely be the default geodatabase named after your project, created by Arc when you opened the new project (i.e., CRS_OSP.gdb)
# 3. The basic functionality of this tool requires 6 input datasets. The first 2 must be downloaded from FEMA, and are contained within the The National Flood Hazard Layer (files named S_POL_AR.shp and S_FLD_HAZ_AR.shp).
# 4. The next 2 datasets come from USGS's National Hydrography Dataset (NHD): NHD Areas and NHD Waterbodies. These are in a geodatabase downloaded from NHD.
# 5. The 5th dataset is Land Cover. There are many sources available; however, at this stage of development, the tool requires land cover data from the National Land Cover Database (NLCD). This should be downloaded as a .tif file containing raster data. The tool require two NLCD rasters, one of land cover types and one of percent impervious area.
# 6. The 6th and final essential dataset is Preserved Open Space. This is the most important layer; a community may only receive OSP credits for land that is protected from development.
#       6.1. Data may be downloaded from USGS's Protected Areas Database of the US (PAD-US), which is nationally available.
#       6.2. It is preferable to use more updated/accurate local data for this layer. Please contact Logan Grant at the address above if you want to use your own data.
# 7. Note your NFIP community ID number.
# 8. Add the tool to your project, and run the script. You will be prompted to provide parameters, such as your community's name, ID number, and the paths to the input datasets.


#NOTES
#See 'NOAA Workflow for mapping OSP' to supplement this tool. It includes directions for acquiring nationally available datasets.
#Once tool has been run, click 'view details'. Here you will see any warnings or other important messages.
#To see outputs in your geodatabase, you may need to refresh it in the Catalog pane after running the tool

#####################################BEGIN CODE - RECEIVE USER INPUTS#############################################

#ask for state, determines coordinate system
state = arcpy.GetParameterAsText(0)
if state == 'NC':
    ProjCoordSys = 'PROJCS["NAD_1983_StatePlane_North_Carolina_FIPS_3200_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",2000000.002616666],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-79.0],PARAMETER["Standard_Parallel_1",34.33333333333334],PARAMETER["Standard_Parallel_2",36.16666666666666],PARAMETER["Latitude_Of_Origin",33.75],UNIT["Foot_US",0.3048006096012192]]'
elif state =='FL':
    ProjCoordSys = 'PROJCS["NAD_1983_StatePlane_Florida_North_FIPS_0903_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",1968500.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-84.5],PARAMETER["Standard_Parallel_1",29.58333333333333],PARAMETER["Standard_Parallel_2",30.75],PARAMETER["Latitude_Of_Origin",29.0],UNIT["Foot_US",0.3048006096012192]]'
elif state =='VA':
    ProjCoordSys = 'PROJCS["NAD_1983_StatePlane_Virginia_South_FIPS_4502_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",11482916.66666666],PARAMETER["False_Northing",3280833.333333333],PARAMETER["Central_Meridian",-78.5],PARAMETER["Standard_Parallel_1",36.76666666666667],PARAMETER["Standard_Parallel_2",37.96666666666667],PARAMETER["Latitude_Of_Origin",36.33333333333334],UNIT["Foot_US",0.3048006096012192]]'
elif state =='SC':
    ProjCoordSys = 'PROJCS["NAD_1983_StatePlane_South_Carolina_FIPS_3900_Feet",GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Lambert_Conformal_Conic"],PARAMETER["False_Easting",1999996.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",-81.0],PARAMETER["Standard_Parallel_1",32.5],PARAMETER["Standard_Parallel_2",34.83333333333334],PARAMETER["Latitude_Of_Origin",31.83333333333333],UNIT["Foot_US",0.3048006096012192]]'
else:
    arcpy.AddWarning("State not supported")
#If your state is not supported, contact Logan Grant at the address above.

#ask user if they are modeling one community or several at once.
Comm_binary = arcpy.GetParameterAsText(1)

#ask for NFHL community ID number, used to create the community boundary from the NFHL
CommID = arcpy.GetParameterAsText(2)

#ask for geodatabase, where the outputs will be saved
Workspace = arcpy.GetParameterAsText(3)

#ask for path to NFHL file
NFHL_Loc = arcpy.GetParameterAsText(4)

#ask for path to SFHA file
SFHA_Loc = arcpy.GetParameterAsText(5)

#ask for path to NHD Area file
NHD_Area_Loc = arcpy.GetParameterAsText(6)

#ask for path to NHD Waterbody file
NHD_Waterbody_Loc = arcpy.GetParameterAsText(7)

#ask for path to NLCD Percent Impervious file
LandCover_Loc = arcpy.GetParameterAsText(8)

#ask for path to NLCD Land Cover file
LandCover_Loc_NLCD = arcpy.GetParameterAsText(9)

#ask if the user wants to use custom Protected Areas data, or if they will be using PAD-US
Protected_Areas_Binary = arcpy.GetParameterAsText(10)

if Protected_Areas_Binary = 'Custom Protected Areas Dataset':
    arcpy.AddWarning("Custom Protected Areas may not be supported. If tool fails, contact Developer for assistance.")

#ask for path to Protected Areas file
PADUS_Loc = arcpy.GetParameterAsText(11)

#ask user if they have parcel data.
Parcels_binary = arcpy.GetParameterAsText(12)

#ask for path to parcel data.
Parcels_Loc = arcpy.GetParameterAsText(13)

#If VA, ask for path to DCR protected lands data.
DCR_protected = arcpy.GetParameterAsText(14)

#If VA, ask for path to RPA data.
RPA_Loc = arcpy.GetParameterAsText(15)


###################################BEGIN GEOPROCESSING###########################################
#Create a Map object. Allows the script to add layers to the current map.
aprx = arcpy.mp.ArcGISProject("CURRENT")
aprxMap = aprx.listMaps()[0]

#Below is a list of CIDs representing communities in VA that protect Resource Protection Areas (RPAs) under the Chesapeake Bay Preservation Act
RPA_list = [510001,515520,510249,510198,510035,510048,515525,510071,510237,510077,510303,510201,510082,510312,510304,510084,510096,510098,510306,510105,510107,510204,510119,510310,510308,510154,510157,510250,510182,515519,510034,510039,515524,510054,510065,515527,510080,510103,510104,510112,510183,515529,510129,510156,515531,510294]


#The following layers are useful if modelling several communities at once. All outputs are merged into these.
with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
    aSFHA_layer = arcpy.management.CreateFeatureclass(Workspace, "aSFHA", "POLYGON", None, "DISABLED", "DISABLED")
    NFOS1_layer = arcpy.management.CreateFeatureclass(Workspace, "NFOS1", "POLYGON", None, "DISABLED", "DISABLED")
    OSP_Eligible_layer = arcpy.management.CreateFeatureclass(Workspace, "OSP_Eligible", "POLYGON", None, "DISABLED", "DISABLED")
    Future_OSP_Parcels_layer = arcpy.management.CreateFeatureclass(Workspace, "Future_OSP_Parcels", "POLYGON", None, "DISABLED", "DISABLED")
    OSP_Opportunities_layer = arcpy.management.CreateFeatureclass(Workspace, "OSP_Opportunities", "POLYGON", None, "DISABLED", "DISABLED")


###create copy of s_pol_ar file, this will hold data outputs from the tool.
NFHL_Copy = arcpy.CopyFeatures_management(NFHL_Loc, Workspace+"/NFHL_Copy")

#Add NFHL_Copy to the map
aprxMap.addDataFromPath(NFHL_Copy)

#add fields to NFHL copy to hold data outputs
arcpy.management.AddField("NFHL_Copy", "SFHA_Area_Acres", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "aSFHA_Area_Acres", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Acres_Curr", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Acres_Future", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Acres_Total", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "NFOS1_Acres_Curr", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Cred_Curr", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Cred_Future", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "NFOS1_Cred_Curr", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "NFOS1_Cred_Future_Max", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "NFOS2_Cred_Future_Max", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "DR_Cred_Future_Max", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Cred_Curr_Total", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Cred_Future_Total", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
arcpy.management.AddField("NFHL_Copy", "OSP_Cred_Future_Max", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')


#For modelling a single community 
if Comm_binary == 'One':
    CID_List = []
    CID_List.append(CommID)

#for modelling several communities at once
#Create array of CID's in the NFHL file
else:
    CID_List = [row[0] for row in arcpy.da.SearchCursor('NFHL_Copy', 'CID')]

#Begin Master for-loop. Iterates through all specified communities.    
for i in CID_List:

    #ArcGIS memory is cleared. This is necessary to prevent lag when modelling many communities at once.
    arcpy.Delete_management("in_memory")
    #Time is recorded. Modelling time is provided once the tool finishes. 
    now = datetime.datetime.now()
    #Used for naming outputs:
    CommName = 'CID'+i
    whereClause='"CID"='+ "'"+i+"'"

    #Extract community boundary from NFHL
    with arcpy.EnvManager(scratchWorkspace= Workspace, outputCoordinateSystem=ProjCoordSys, workspace=Workspace):
        Comm_Boundary = arcpy.analysis.Select(NFHL_Loc, "in_memory/"+ CommName + '_Boundary', whereClause)

    #Extract SFHA data within the community and save to the geodatabase:
    S_FLD_HAZ_AR_Clip = arcpy.analysis.Clip(SFHA_Loc, Comm_Boundary, "in_memory"+"\S_FLD_HAZ_AR_Clip", None)
    with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
        SFHA = arcpy.analysis.Select(S_FLD_HAZ_AR_Clip, Workspace+'/'+CommName+'_SFHA', "SFHA_TF = 'T'")
        
    #Calculate the area of the community's SFHA, in acres. Areas are summed and stored in a statistics table.
    arcpy.management.AddGeometryAttributes(SFHA, "AREA_GEODESIC", '', "ACRES", None)
    SFHA_Statistics = arcpy.analysis.Statistics(SFHA, "in_memory"+"\SFHA_Statistics", "AREA_GEO SUM", None)
    #Assign area sum to an object to be used later.
    rows = arcpy.SearchCursor(SFHA_Statistics)
    for row in rows:
        SFHA_Area_Sum = row.getValue('SUM_AREA_GEO')
    #Add SFHA to map
    aprxMap.addDataFromPath(SFHA)

    #Extract PAD-US data within the community
    PADUS_Clip = arcpy.management.SelectLayerByLocation(PADUS_Loc, "INTERSECT", Comm_Boundary, None, "NEW_SELECTION", "NOT_INVERT")
    with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
        PADUS_aoi = arcpy.management.CopyFeatures(PADUS_Clip, 'in_memory'+"\PADUS_aoi", '', None, None, None)

    #If using PAD-US, check for federal and tribal lands. If there are any, extract those greater than 10 acres
    if Protected_Areas_Binary == 'USGS PAD-US Dataset':
        Federal_Tribal_Lands_select = arcpy.analysis.Select(PADUS_aoi, 'in_memory'+"\Federal_Tribal_Lands_select", "Mang_Type = 'FED' Or Mang_Type = 'TRIB'")
        result = arcpy.management.GetCount(Federal_Tribal_Lands_select)
        count = int(result.getOutput(0))
        if count>0:
            Federal_Tribal_Lands_sp = arcpy.management.MultipartToSinglepart(Federal_Tribal_Lands_select, 'in_memory'+"\Federal_Tribal_Lands_sp")
            arcpy.management.AddGeometryAttributes(Federal_Tribal_Lands_sp, "AREA_GEODESIC", '', "ACRES", None)
            Federal_Tribal_Lands_g10acres = arcpy.analysis.Select(Federal_Tribal_Lands_sp, 'in_memory/'+"Federal_Tribal_Lands_g10acres", "AREA_GEO > 10")

    #Extract NHD data in the community
    with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
        NHD_Area_Clip = arcpy.management.SelectLayerByLocation(NHD_Area_Loc, "INTERSECT", Comm_Boundary, None, "NEW_SELECTION", "NOT_INVERT")
    with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
        NHD_Waterbody_Clip = arcpy.management.SelectLayerByLocation(NHD_Waterbody_Loc, "INTERSECT", Comm_Boundary, None, "NEW_SELECTION", "NOT_INVERT")
    NHDWaterbody_aoi = arcpy.management.CopyFeatures(NHD_Waterbody_Clip, 'in_memory/'+"NHDWaterbody_aoi", '', None, None, None)
    NHDArea_aoi = arcpy.management.CopyFeatures(NHD_Area_Clip, 'in_memory/'+"NHDArea_aoi", '', None, None, None)

    #Select bays, inlets, seas, oceans, streams, rivers, lakes, ponds, reservoirs, and estuaries from NHD data, and merge.
    NHDArea_aoi_Select = arcpy.analysis.Select(NHDArea_aoi, 'in_memory/'+"NHDArea_aoi_Select", "FType = 445 Or FType = 460 Or FType = 312")
    NHDWaterbody_aoi_Select = arcpy.analysis.Select(NHDWaterbody_aoi, 'in_memory/'+"NHDWaterbody_aoi_Select", "FType = 390 Or FType = 436 Or FType = 493")
    NHD_Area_Waterbody_Select_Merge = arcpy.management.Merge([NHDWaterbody_aoi_Select,NHDArea_aoi_Select], 'in_memory/'+"NHD_Area_Waterbody_Select_Merge")

    #Dissolve waterbody features
    arcpy.management.AddField(NHD_Area_Waterbody_Select_Merge, "Open_Water", "SHORT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.CalculateField(NHD_Area_Waterbody_Select_Merge, "Open_Water", "1", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
        NHD_Area_Waterbody_Select_Merge_Dissolve = arcpy.management.Dissolve(NHD_Area_Waterbody_Select_Merge, 'in_memory/'+"NHD_Area_Waterbody_Select_Merge_Dissolve", "Open_Water", None, "SINGLE_PART", "DISSOLVE_LINES")

    #Extract open waters greater than 10 acres
    arcpy.management.AddGeometryAttributes(NHD_Area_Waterbody_Select_Merge_Dissolve, "AREA_GEODESIC", '', "ACRES", None)
    Open_Water_g10acres = arcpy.analysis.Select(NHD_Area_Waterbody_Select_Merge_Dissolve, 'in_memory/'+"Open_Water_g10acres", "AREA_GEO > 10")
 
    #Erase Excluded Areas from the SFHA
    if Protected_Areas_Binary == 'USGS PAD-US Dataset':
        if count>0:
            Excluded_Areas = arcpy.management.Merge([Federal_Tribal_Lands_g10acres,Open_Water_g10acres], 'in_memory/'+"Excluded_Areas")
        else:
            Excluded_Areas = Open_Water_g10acres
    else:
        Excluded_Areas = Open_Water_g10acres
    
    SFHA_Erase = arcpy.analysis.Erase(SFHA, Excluded_Areas, 'in_memory/'+CommName+'_SFHA_Erase', None)
    
    with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
        aSFHA = arcpy.management.Dissolve(SFHA_Erase, Workspace+'/'+CommName+"_aSFHA", "SFHA_TF", None, "MULTI_PART", "DISSOLVE_LINES")
        #NOAA workflow calls for dissolve by "FLD_ZONE," but I do not see the benefit in this. Dissolving by "SFHA_TF" should result in one aSFHA polygon, which helps with intersection with parcels.
        #aSFHA = arcpy.management.Dissolve(SFHA_Erase, Workspace+'/'+CommName+"_aSFHA", "FLD_ZONE", None, "MULTI_PART", "DISSOLVE_LINES")
        
    #Add aSFHA to map and append data to master aSFHA layer
    aprxMap.addDataFromPath(aSFHA)
    arcpy.management.Append(Workspace+'/'+CommName+"_aSFHA", Workspace+'/'+"aSFHA", "NO_TEST", None, '', '')
    aSFHA_GetCount = arcpy.management.GetCount(aSFHA)[0]

    #Calculate the area of the community's SFHA minus excluded areas. This is known as the impact adjusted SFHA, or aSFHA.
    arcpy.management.AddGeometryAttributes(aSFHA, "AREA_GEODESIC", '', "ACRES", None)
    aSFHA_Statistics = arcpy.analysis.Statistics(aSFHA, "in_memory"+"/aSFHA_Statistics", "AREA_GEO SUM", None)
    rows = arcpy.SearchCursor(aSFHA_Statistics)
    for row in rows:
        aSFHA_Area_Sum = row.getValue('SUM_AREA_GEO')

    #Prepare protected areas layer
    if Protected_Areas_Binary == 'USGS PAD-US Dataset':
        Protected_Areas = arcpy.analysis.Select(PADUS_aoi, 'in_memory/'+"Protected_Areas", "Mang_Type <> 'FED' Or Mang_Type <> 'TRIB'")
    else:
        Protected_Areas = PADUS_aoi

    arcpy.management.AddField(Protected_Areas, "OSP_ID", "TEXT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
    arcpy.management.CalculateField(Protected_Areas, "OSP_ID", '"PADUS_"+str(!OBJECTID!)', "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    #Extract protected areas within the aSFHA 
    #Locailities that enforce floodplain standards outside the aSFHA may be able to get points for OSP in those areas. Check CRS Coordinator's Manual
    Protected_Areas_Clip = arcpy.analysis.Clip(Protected_Areas, aSFHA, 'in_memory/'+"Protected_Areas_Clip", None)

 
#####################Geoprocessing for Natural Functions Open Space - 1 (NFOS1) Extra Credit########################################
#Note: The reason this is out-of-order from the NOAA Workflow, is because you need to do this before adding supplemental protected areas data.
#PAD-US is the only dataset with GAP Status Codes, which are used for determining NFOS1 eligibility.
    
    #Calculate areas of protected lands, in acres. See note below!
    arcpy.management.AddGeometryAttributes(Protected_Areas_Clip, "AREA_GEODESIC", '', "ACRES", None)


#IMPORTANT NOTE:
#When running "zonal statistics as table", the zone features (protected area polygon) cannot be smaller than the raster cell size (NLCD)
#The NLCD 2019 30-meter raster cell size is 900 square meters - about .22 acres
#The NOAA workflow encourages you to delete OSP eligble areas less than 0.01 acres, but we will need to up this value to agree with our raster data. See below.    

    #delete polygons less than 0.3 acres
    with arcpy.da.UpdateCursor(Protected_Areas_Clip, "AREA_GEO") as cursor:
        for row in cursor:
            if row[0] < .3:
                cursor.deleteRow()

    #Check that there are protected areas before proceeding.
    Protected_Areas_Clip_GetCount = arcpy.management.GetCount(Protected_Areas_Clip)[0]
    
    if not Protected_Areas_Clip_GetCount == '0':

        #Extract land cover data within the community and calculate impervious areas.
        with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
            Land_Cover_ext = arcpy.sa.ExtractByMask(LandCover_Loc, Comm_Boundary); Land_Cover_ext.save('in_memory/'+"Land_Cover_ext")

        Protected_Areas_Clip_NLCD_Impervious_MEAN = arcpy.sa.ZonalStatisticsAsTable(Protected_Areas_Clip,"OBJECTID", Land_Cover_ext, 'in_memory/'+"OSP_Eligible_NLCD_Impervious_MEAN", "DATA", "MEAN", "CURRENT_SLICE", 90, "AUTO_DETECT")

        arcpy.management.AlterField(Protected_Areas_Clip_NLCD_Impervious_MEAN, "MEAN", "NLCD_MEAN_PctImperv", '', "DOUBLE", 8, "NULLABLE", "DO_NOT_CLEAR")

        arcpy.management.JoinField(Protected_Areas_Clip, "OBJECTID", Protected_Areas_Clip_NLCD_Impervious_MEAN, "OBJECTID", "NLCD_MEAN_PctImperv")

        arcpy.management.AddField(Protected_Areas_Clip, "Imperv_acres", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

        arcpy.management.CalculateField(Protected_Areas_Clip, "Imperv_acres", "(!NLCD_MEAN_PctImperv!/100)*!AREA_GEO!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

        #Calculate impact adjusted area of protected areas
        arcpy.management.AddField(Protected_Areas_Clip, "aOSP", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
        
        arcpy.management.CalculateField(Protected_Areas_Clip, "aOSP", "!AREA_GEO!-!Imperv_acres!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
        
        #Check GAP Status Codes for areas preserved in their natural state
        Gap_Sts_List = [row[0] for row in arcpy.da.SearchCursor(Protected_Areas_Clip, 'GAP_Sts')]

        if '1' in Gap_Sts_List or '2' in Gap_Sts_List:      
                
            arcpy.management.AddField(Protected_Areas_Clip, "NFOS1", "SHORT", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

            arcpy.management.SelectLayerByAttribute(Protected_Areas_Clip, "NEW_SELECTION", "GAP_Sts IN ('1', '2')", None)

            arcpy.management.CalculateField(Protected_Areas_Clip, "NFOS1", "1", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

            arcpy.management.SelectLayerByAttribute(Protected_Areas_Clip, "SWITCH_SELECTION", '', None)

            arcpy.management.CalculateField(Protected_Areas_Clip, "NFOS1", "0", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

            arcpy.management.AddField(Protected_Areas_Clip, "aNFOS1", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

            arcpy.management.AddField(Protected_Areas_Clip, "cNFOS1", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

            arcpy.management.SelectLayerByAttribute(Protected_Areas_Clip, "NEW_SELECTION", "NFOS1 = 1", None)

            arcpy.management.CalculateField(Protected_Areas_Clip, "aNFOS1", "!aOSP!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

            Protected_Areas_Clip_Statistics2 = arcpy.analysis.Statistics(Protected_Areas_Clip, "in_memory"+"\Protected_Areas_Clip_Statistics2", "aNFOS1 SUM", None)

            rows = arcpy.SearchCursor(Protected_Areas_Clip_Statistics2)
            for row in rows:
                NFOS_Acres_Sum = row.getValue('SUM_aNFOS1')
            

            #Calculate NFOS1 credit estimate
            arcpy.management.CalculateField(Protected_Areas_Clip, "cNFOS1", "(!aNFOS1!/"+str(aSFHA_Area_Sum)+")*190", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

            Protected_Areas_Clip_Statistics2 = arcpy.analysis.Statistics(Protected_Areas_Clip, "in_memory"+"\Protected_Areas_Clip_Statistics2", "cNFOS1 SUM", None)

            rows = arcpy.SearchCursor(Protected_Areas_Clip_Statistics2)
            for row in rows:
                NFOS_Credit_Sum = row.getValue('SUM_cNFOS1')

            #Create an NFOS1 layer for visualization and append to master NFOS1 layer. This is not part of the NOAA workflow.
            NFOS1 = arcpy.management.CopyFeatures(Protected_Areas_Clip, Workspace+'/'+CommName+"_NFOS1", '', None, None, None)
            aprxMap.addDataFromPath(NFOS1)
            arcpy.management.Append(NFOS1, NFOS1_layer, "NO_TEST", None, '', '')

            arcpy.management.SelectLayerByAttribute(Protected_Areas_Clip, "SWITCH_SELECTION", '', None)

            arcpy.management.CalculateField(Protected_Areas_Clip, "cNFOS1", "0", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    #If there are no NFOS1 areas, assign zeroes to the corresponding data fields.
        else:
            NFOS_Acres_Sum = 0
            NFOS_Credit_Sum = 0

    else:
        NFOS_Acres_Sum = 0
        NFOS_Credit_Sum = 0



##########################Geoprocessing using VA specific data###############################
    #If in VA, include DCR and RPA data as protected areas
    if state =='VA':
        #Dissolve protected areas. We don't want to double count areas!
        with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
            OSP_Eligible_Original = arcpy.management.Dissolve(Protected_Areas_Clip, 'in_memory/'+"OSP_Eligible_Original", "OSP_ID", None, "MULTI_PART", "DISSOLVE_LINES")


        #Extract DCR protected lands data in the community
        DCRprotected_Clip = arcpy.analysis.Clip(DCR_protected, Comm_Boundary, "in_memory"+"\DCRprotected_Clip", None)
        DCR_NewOSP = arcpy.analysis.Erase(DCRprotected_Clip, OSP_Eligible_Original, 'in_memory/'+"DCR_NewOSP", None)
        OSP_areas_withDCR = arcpy.management.Merge([OSP_Eligible_Original,DCR_NewOSP], 'in_memory/'+"OSP_areas")  
    

        #if an RPA community (see list above), then extract RPA data in the community
        if int(i) in RPA_list:
            RPA_Clip = arcpy.analysis.Clip(RPA_Loc, Comm_Boundary, "in_memory"+"\RPA_Clip", None)
            RPA_NewOSP = arcpy.analysis.Erase(RPA_Clip, OSP_areas_withDCR, 'in_memory/'+"RPA_NewOSP", None)            
            OSP_areas = arcpy.management.Merge([OSP_Eligible_Original,DCR_NewOSP,RPA_NewOSP], 'in_memory/'+"OSP_areas")  

        else:
            OSP_areas = OSP_areas_withDCR
  
    else:
        with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
            OSP_areas = arcpy.management.Dissolve(Protected_Areas_Clip, 'in_memory/'+"OSP_areas", "OSP_ID", None, "MULTI_PART", "DISSOLVE_LINES")

############################################################################################

    #Create OSP_Eligible layer, add it to the map, and append to the master OSP Eligible layer
    OSP_Eligible = arcpy.analysis.Clip(OSP_areas, aSFHA, Workspace+'/'+CommName+"_OSP_Eligible", None)
    aprxMap.addDataFromPath(OSP_Eligible)
    arcpy.management.Append(OSP_Eligible, OSP_Eligible_layer, "NO_TEST", None, '', '')

#Below is a similar workflow to NFOS1 section, above:
    #See IMPORTANT NOTE, above, about running "zonal statistics as table".
    arcpy.management.AddGeometryAttributes(OSP_Eligible, "AREA_GEODESIC", '', "ACRES", None)
    
    with arcpy.da.UpdateCursor(OSP_Eligible, "AREA_GEO") as cursor:
        for row in cursor:
            if row[0] < .3:
                cursor.deleteRow()

    
    OSP_Eligible_GetCount = arcpy.management.GetCount(OSP_Eligible)[0]
    
    if not OSP_Eligible_GetCount == '0':

        #Extract land cover data within the community
        with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
            Land_Cover_ext = arcpy.sa.ExtractByMask(LandCover_Loc, Comm_Boundary); Land_Cover_ext.save('in_memory/'+"Land_Cover_ext")

        OSP_Eligible_NLCD_Impervious_MEAN = arcpy.sa.ZonalStatisticsAsTable(OSP_Eligible,"OBJECTID", Land_Cover_ext, 'in_memory/'+"OSP_Eligible_NLCD_Impervious_MEAN", "DATA", "MEAN", "CURRENT_SLICE", 90, "AUTO_DETECT")

        arcpy.management.AlterField(OSP_Eligible_NLCD_Impervious_MEAN, "MEAN", "NLCD_MEAN_PctImperv", '', "DOUBLE", 8, "NULLABLE", "DO_NOT_CLEAR")

        arcpy.management.JoinField(OSP_Eligible, "OBJECTID", OSP_Eligible_NLCD_Impervious_MEAN, "OBJECTID", "NLCD_MEAN_PctImperv")

        arcpy.management.AddField(OSP_Eligible, "Imperv_acres", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')

        arcpy.management.CalculateField(OSP_Eligible, "Imperv_acres", "(!NLCD_MEAN_PctImperv!/100)*!AREA_GEO!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

        #Calculate impact adjusted area of eligible open space (aOSP)
        arcpy.management.AddField(OSP_Eligible, "aOSP", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
        
        arcpy.management.CalculateField(OSP_Eligible, "aOSP", "!AREA_GEO!-!Imperv_acres!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

        OSP_Eligible_Statistics = arcpy.analysis.Statistics(OSP_Eligible, "in_memory"+"\OSP_Eligible_Statistics", "aOSP SUM", None)
        rows = arcpy.SearchCursor(OSP_Eligible_Statistics)
        for row in rows:
            OSP_Acres_Sum = row.getValue('SUM_aOSP')
            
        #Calculate possible credits (cOSP)
        arcpy.management.AddField(OSP_Eligible, "cOSP", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
        arcpy.management.CalculateField(OSP_Eligible, "cOSP", "(!aOSP!/"+str(aSFHA_Area_Sum)+")*1450", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
        OSP_Eligible_Statistics = arcpy.analysis.Statistics(OSP_Eligible, "in_memory"+"\OSP_Eligible_Statistics", "cOSP SUM", None)
        rows = arcpy.SearchCursor(OSP_Eligible_Statistics)
        for row in rows:
            OSP_Credit_Sum = row.getValue('SUM_cOSP')
        
        SFHA_removeOSP_Eligible = arcpy.analysis.Erase(aSFHA, OSP_Eligible, 'in_memory/'+"SFHA_removeOSP_Eligible", None)

    #If no OSP Eligible areas: 
    else:
        OSP_Acres_Sum = 0
        OSP_Credit_Sum = 0
        SFHA_removeOSP_Eligible = aSFHA
 

###################Begin future OSP Opportunities workflow#########################################
    #Check that there is aSFHA
    if not aSFHA_GetCount == '0':

        #Check for OSP Eligible areas. By definition, these cannot be OSP Opportunities!
        if OSP_Eligible_GetCount != "0":
            aSFHA_LandCover = arcpy.sa.ExtractByMask(LandCover_Loc_NLCD, SFHA_removeOSP_Eligible); aSFHA_LandCover.save('in_memory/'+"aSFHA_LandCover")
        else:
            aSFHA_LandCover = arcpy.sa.ExtractByMask(LandCover_Loc_NLCD, aSFHA); aSFHA_LandCover.save('in_memory/'+"aSFHA_LandCover")

        #Check NLCD for open spaces and convert them to polygons
        #There is a known (and extremely rare) bug here: if a community's aSFHA does not have any open space (has only occurred with a couple very small communities so far), then there is an error.
        aSFHA_Undeveloped = arcpy.sa.ExtractByAttributes(aSFHA_LandCover, "Value > 31 And Value <> 81 And Value <> 82"); aSFHA_Undeveloped.save("in_memory/"+"aSFHA_Undeveloped")

        with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
            aSFHA_Undeveloped_polygons = arcpy.conversion.RasterToPolygon(aSFHA_Undeveloped, "in_memory/"+"aSFHA_Undeveloped_polygons", "SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
            
        aSFHA_undeveloped_GetCount = arcpy.management.GetCount(aSFHA_Undeveloped_polygons)[0]
        

        #if using parcel data, extract parcels in the community. Counting them is necessary when running multiple communities at once, because the parcel dataset may not cover all of them.
        if Parcels_binary == 'Yes':
            Parcels_Clip = arcpy.analysis.Clip(Parcels_Loc, Comm_Boundary, "in_memory"+"\Parcels_Clip", None)
            Parcels_Clip_GetCount = arcpy.management.GetCount(Parcels_Clip)[0]
        else:
            Parcels_Clip_GetCount = '0'

        #Extract parcels of interest that contain OSP Opportunity area
        if not Parcels_Clip_GetCount == '0':
            with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
                Parcels_aoi = arcpy.management.CopyFeatures(Parcels_Clip, 'in_memory'+"\Parcels_aoi", '', None, None, None)
            OSP_opportunities_1 = arcpy.management.SelectLayerByLocation(Parcels_aoi, "INTERSECT", aSFHA_Undeveloped_polygons, None, "NEW_SELECTION", "NOT_INVERT")
            
            #Add parcels of interest to map and append to master layer
            with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
                Future_OSP_Parcels = arcpy.management.CopyFeatures(OSP_opportunities_1, Workspace+'/'+CommName+"Future_OSP_Parcels", '', None, None, None)
            aprxMap.addDataFromPath(Future_OSP_Parcels)
            arcpy.management.Append(Future_OSP_Parcels, Future_OSP_Parcels_layer, "NO_TEST", None, '', '')

            #Calculate area of parcels that are open space. Useful for screening out those that don't present great opportunity.
            Parcels_aSFHA_intersect = arcpy.analysis.Intersect([Future_OSP_Parcels , aSFHA_Undeveloped_polygons], 'in_memory'+"\Parcels_aSFHA_intersect", "ALL", None, "INPUT")
            arcpy.management.AddGeometryAttributes(Parcels_aSFHA_intersect, "AREA_GEODESIC", '', "ACRES", None)
            arcpy.management.CalculateField(Parcels_aSFHA_intersect, "intersect_area_acres", "!AREA_GEO!", "PYTHON3", '', "DOUBLE", "NO_ENFORCE_DOMAINS")
            arcpy.management.JoinField(Future_OSP_Parcels, "OBJECTID", Parcels_aSFHA_intersect, "OBJECTID", "intersect_area_acres")
            arcpy.management.AddGeometryAttributes(Future_OSP_Parcels, "AREA_GEODESIC", '', "ACRES", None)
            arcpy.management.CalculateField(Future_OSP_Parcels, "Percent_aSFHA", "(!intersect_area_acres! / !AREA_GEO!) * 100", "PYTHON3", '', "DOUBLE", "NO_ENFORCE_DOMAINS")
              
            #Now, clip the parcels of interest to the aSFHA_remove_OSP_Eligible in order to create the OSP Opportunities layer.
            #Add it to the map, append to master layer, and calculate area in acres.
            with arcpy.EnvManager(outputCoordinateSystem=ProjCoordSys):
                OSP_opportunities = arcpy.analysis.Clip(Future_OSP_Parcels, aSFHA_Undeveloped_polygons, Workspace+'/'+CommName+"_OSP_Opportunities", None)
            aprxMap.addDataFromPath(OSP_opportunities)
            arcpy.management.Append(OSP_opportunities, OSP_Opportunities_layer, "NO_TEST", None, '', '')
            arcpy.management.AddGeometryAttributes(OSP_opportunities, "AREA_GEODESIC", '', "ACRES", None)


        #for use without parcels data:
        elif not aSFHA_undeveloped_GetCount == '0':
            OSP_opportunities = arcpy.management.CopyFeatures(aSFHA_Undeveloped_polygons, Workspace+'/'+CommName+"_OSP_opportunities", '', None, None, None)
            aprxMap.addDataFromPath(OSP_opportunities)
            arcpy.management.AddGeometryAttributes(OSP_opportunities, "AREA_GEODESIC", '', "ACRES", None)

            with arcpy.da.UpdateCursor(OSP_opportunities, "AREA_GEO") as cursor:
                for row in cursor:
                    #arbitrary value defined below: delete OSP opportunities that are less than half an acre...
                    if row[0] < .5:
                        cursor.deleteRow()

            arcpy.management.Append(OSP_opportunities, OSP_Opportunities_layer, "NO_TEST", None, '', '')
    
        else:
            OSP_opportunities = arcpy.management.CreateFeatureclass(Workspace, "OSP_opportunities", "POLYGON", None, "DISABLED", "DISABLED")
            aprxMap.addDataFromPath(OSP_opportunities)
            arcpy.management.Append(OSP_opportunities, OSP_Opportunities_layer, "NO_TEST", None, '', '')
            arcpy.management.AddGeometryAttributes(OSP_opportunities, "AREA_GEODESIC", '', "ACRES", None)

        OSP_opportunities_Statistics = arcpy.analysis.Statistics(OSP_opportunities, "in_memory/"+"OSP_opportunities_Statistics", "AREA_GEO SUM", None)

        rows = arcpy.SearchCursor(OSP_opportunities_Statistics)
        for row in rows:
            Credit_Opportunities_Acres = row.getValue('SUM_AREA_GEO')
        
        #Calculate possible credits (cOSP_opportunities)
        arcpy.management.AddField(OSP_opportunities, "cOSP", "DOUBLE", None, None, None, '', "NULLABLE", "NON_REQUIRED", '')
        arcpy.management.CalculateField(OSP_opportunities, "cOSP", "(!AREA_GEO!/"+str(aSFHA_Area_Sum)+")*1450", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

        OSP_opportunities_Statistics = arcpy.analysis.Statistics(OSP_opportunities, "in_memory/"+"OSP_opportunities_Statistics", "cOSP SUM", None)
        rows = arcpy.SearchCursor(OSP_opportunities_Statistics)
        for row in rows:
            Credit_Opportunities_Sum = row.getValue('SUM_cOSP')
       
 
        #if no OPS Opportunities
        if not 'Credit_Opportunities_Sum' in locals():
            Credit_Opportunities_Acres = 0
            Credit_Opportunities_Sum = 0

    #Below are crediting scenario calculations. Values are added to the NFHL_Copy data table      
        #Compute total OSP acres (Current + Future)
        OSP_Acres_Total = OSP_Acres_Sum + Credit_Opportunities_Acres

        #Compute maximum potential NFOS1 credits if Current & Potential OSP areas are in or restored to natural state.
        NFOS1_Cred_Future_Max = (OSP_Acres_Total / aSFHA_Area_Sum) * 190

        #Compute maximum potential NFOS2 credits if Current & Potential OSP areas are designated in a natural floodplain protection plan.
        #Deed restrictions use the same formula
        NFOS2_Cred_Future_Max = (OSP_Acres_Total / aSFHA_Area_Sum) * 50
        DR_Cred_Future_Max = NFOS2_Cred_Future_Max

        #Compute total credits currently available (OSP Eligible + NFOS1)
        OSP_Cred_Curr_Total = OSP_Credit_Sum + NFOS_Credit_Sum

        #Compute potential credits (current + future) without extra credit, except known NFOS1.
        OSP_Cred_Future_Total = OSP_Cred_Curr_Total + Credit_Opportunities_Sum
        
        #Compute maximum potential credits with extra credit
        OSP_Cred_Future_Max = OSP_Credit_Sum + Credit_Opportunities_Sum + NFOS1_Cred_Future_Max + NFOS2_Cred_Future_Max + DR_Cred_Future_Max

    #if no aSFHA:
    else:
        SFHA_Area_Sum = 0
        aSFHA_Area_Sum = 0
        OSP_Acres_Sum = 0
        OSP_Credit_Sum = 0
        NFOS_Acres_Sum = 0
        NFOS_Credit_Sum = 0
        Credit_Opportunities_Acres = 0
        Credit_Opportunities_Sum = 0
        OSP_Acres_Total = 0
        NFOS1_Cred_Future_Max = 0
        NFOS2_Cred_Future_Max = 0
        DR_Cred_Future_Max = 0
        OSP_Cred_Curr_Total = 0
        OSP_Cred_Future_Max = 0
        OSP_Cred_Future_Total = 0

    #Select community within NFHL_Copy layer
    arcpy.management.SelectLayerByAttribute("NFHL_Copy", "NEW_SELECTION", whereClause , None)

        
    #Insert data into table for selected community 
    arcpy.management.CalculateField("NFHL_Copy", "SFHA_Area_Acres", SFHA_Area_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "aSFHA_Area_Acres", aSFHA_Area_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Acres_Curr", OSP_Acres_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Cred_Curr", OSP_Credit_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "NFOS1_Acres_Curr", NFOS_Acres_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "NFOS1_Cred_Curr", NFOS_Credit_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Acres_Future", Credit_Opportunities_Acres, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Cred_Future", Credit_Opportunities_Sum, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Acres_Total", OSP_Acres_Total, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "NFOS1_Cred_Future_Max", NFOS1_Cred_Future_Max, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "NFOS2_Cred_Future_Max", NFOS2_Cred_Future_Max, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "DR_Cred_Future_Max", DR_Cred_Future_Max, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Cred_Curr_Total", OSP_Cred_Curr_Total, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Cred_Future_Max", OSP_Cred_Future_Max, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")
    arcpy.management.CalculateField("NFHL_Copy", "OSP_Cred_Future_Total", OSP_Cred_Future_Total, "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    arcpy.management.SelectLayerByAttribute("NFHL_Copy", "CLEAR_SELECTION", '', None)
                                                                    
    later = datetime.datetime.now()
    Elapsed = later - now
    arcpy.AddMessage(str(i)+' loop time = '+str(Elapsed))  


if not aSFHA_GetCount == '0':
    aprxMap.addDataFromPath(Workspace+'/'+"aSFHA")
    aprxMap.addDataFromPath(Workspace+'/'+"NFOS1")
    aprxMap.addDataFromPath(Workspace+'/'+"OSP_Eligible")
    aprxMap.addDataFromPath(Workspace+'/'+"Future_OSP_Parcels")
    aprxMap.addDataFromPath(Workspace+'/'+"OSP_Opportunities")
