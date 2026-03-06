##  Streamlit-Based Web GIS for Spatial and Attribute Join Operations on (Streamlit) 
It allows users to upload two spatial datasets and perform spatial and attribute joins directly in a web interface.
 # Features 
 #  Upload Spatial Files
Upload Shapefile (ZIP) as Left layer
Upload GeoJSON as Right layer
Automatic validation of files
CRS consistency handling
# Data Preview
Display interactive maps using Folium
Show first 5 rows of each dataset
# Spatial Join
Supported relationships:
intersects
within
contains
# Join types:
left
inner
right
Automatic CRS correction
# Attribute Join
Select join fields from both datasets
# Join types:
left
inner
right
outer
Geometry preserved
Clear result messages
# Download Result 
Export final result as GeoJSON
Automatically prioritizes:
Attribute Join result (if exists)
Otherwise Spatial Join result
# Technologies Used
Fiona
PyProj
Rtree
PyArrow
Streamlit
GeoPandas
Folium
Shapely

# Run Locally 
#  Activate Environment
conda activate PYTHONGIS
If the environment does not exist:
conda env create -f PYTHONGIS.yml
conda activate PYTHONGIS
## Run the Application
streamlit run Magdy_2026.py
# Future Improvements
Add CRS selection tool
Add support for multiple layer visualization
