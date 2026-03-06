import io
import os
import zipfile
import tempfile

import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Magdy_2026", layout="wide")
st.markdown("""
<style>

div[data-testid="stHorizontalBlock"] > div:nth-child(1),
div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
    background-color: #e6f2ff;   /* أزرق فاتح موحد */
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #cce0ff;
}

h3 {
    color: #003366;
    font-weight: bold;
}

div[data-testid="stAlert"] {
    background-color: #dbeeff !important;
    border-left: 5px solid #3399ff !important;
}

</style>
""", unsafe_allow_html=True)
st.markdown("""
<div style="
    background-color: #e6f2ff;
    padding: 25px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #cce0ff;
">
    <h1 style="
        color: #003366;
        margin: 0;
        font-size: 30px;
        font-weight: bold;
    ">
      Streamlit-Based Web GIS for Spatial and Attribute Join Operations
    </h1>
</div>
""", unsafe_allow_html=True)
st.write("Please upload a Shapefile (ZIP) and a GeoJSON file to visualize the layers, perform Spatial and Attribute Join operations, and preview the results")
# ------------------------------------------------- Helpers ----------------------------------------------------------
def read_geojson(uploaded_file) -> gpd.GeoDataFrame:
    try:
        content = uploaded_file.read()
        uploaded_file.seek(0)
        return gpd.read_file(io.BytesIO(content))
    except Exception as e:
        raise ValueError(f"GeoJSON غير صالح أو لا يمكن قراءته. التفاصيل: {e}")

def read_shapefile_zip(uploaded_zip) -> gpd.GeoDataFrame:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = os.path.join(tmpdir, "data.zip")
            with open(zip_path, "wb") as f:
                f.write(uploaded_zip.read())
            uploaded_zip.seek(0)

            with zipfile.ZipFile(zip_path, "r") as z:
                z.extractall(tmpdir)

            shp_files = []
            for root, _, files in os.walk(tmpdir):
                for name in files:
                    if name.lower().endswith(".shp"):
                        shp_files.append(os.path.join(root, name))

            if not shp_files:
                raise ValueError(" Shapefile must be in ZIP format  ")

            shp_path = shp_files[0]
            gdf = gpd.read_file(shp_path)
            return gdf

    except zipfile.BadZipFile:
        raise ValueError(" The ZIP file is corrupted or not a valid ZIP format   ")
    except Exception as e:
        raise ValueError(f"Unable to read Shapefile from ZIP. Details : {e}")

def make_map(gdf: gpd.GeoDataFrame, name: str):
    if gdf is None or gdf.empty:
        st.warning(f"  : {name}")
        return

    try:
        if gdf.crs is None:
            gdf_wgs = gdf
        else:
            gdf_wgs = gdf.to_crs(epsg=4326)
    except Exception:
        gdf_wgs = gdf

    center = [0, 0]
    try:
        c = gdf_wgs.geometry.unary_union.centroid
        center = [c.y, c.x]
    except Exception:
        pass

    m = folium.Map(location=center, zoom_start=6, control_scale=True)

    try:
        folium.GeoJson(
            data=gdf_wgs.__geo_interface__,
            name=name
        ).add_to(m)
        folium.LayerControl().add_to(m)
    except Exception as e:
        st.error(f"   Unable to display the map for  {name}. Details: {e}")
        return

    st_folium(m, height=320, width=None, key=f"map_{name}")

#  FIX: دالة معاينة للجدول بدون مشاكل geometry
def preview_gdf(gdf: gpd.GeoDataFrame, n: int = 5):
    preview = gdf.head(n).copy()
    if "geometry" in preview.columns:
        preview["geometry"] = preview["geometry"].astype(str)  
    return preview

# ---------------------------------- Sidebar ----------------------------------------
with st.sidebar:

    st.markdown("""
    <h2 style="
        text-align:center;
        font-size:26px;
        font-weight:700;
        color:#003366;
        margin-bottom:25px;
    ">
    Please upload your files
    </h2>
    """, unsafe_allow_html=True)


    st.markdown("""
    <h3 style="
        font-size:22px;
        font-weight:600;
        color:#0b3d91;
        margin-bottom:5px;
    ">
    Left: Shapefile ZIP
    </h3>
    """, unsafe_allow_html=True)

    left_zip = st.file_uploader(
        "",  
        type=["zip"],
        accept_multiple_files=False
    )


    st.markdown("""
    <h3 style="
        font-size:22px;
        font-weight:600;
        color:#0b3d91;
        margin-top:20px;
        margin-bottom:5px;
    ">
    Right: GeoJSON
    </h3>
    """, unsafe_allow_html=True)

    right_geojson = st.file_uploader(
        "",  
        type=["geojson", "json"],
        accept_multiple_files=False
    )

# ---------------------------- Main area layout ---------------------------------
col_left, col_right = st.columns(2)

if "left_gdf" not in st.session_state:
    st.session_state.left_gdf = None
if "right_gdf" not in st.session_state:
    st.session_state.right_gdf = None
if "join_result" not in st.session_state:
    st.session_state.join_result = None
if "attr_result" not in st.session_state:
    st.session_state.attr_result = None

# ------------------------------ Read Left ----------------------------------------
with col_left:
    st.markdown(
        "<h3 style='text-align: center;'> Shapefile (ZIP)</h3>",
        unsafe_allow_html=True
    )

    if left_zip is not None:
        with st.spinner("Reading file ZIP"):
            try:
                st.session_state.left_gdf = read_shapefile_zip(left_zip)
                st.success("   The file was uploaded successfully.  ")
            except ValueError as e:
                st.session_state.left_gdf = None
                st.error(str(e))

    if st.session_state.left_gdf is not None:
        make_map(st.session_state.left_gdf, "Left Layer")
        st.write("  First 5 rows:")
        st.dataframe(preview_gdf(st.session_state.left_gdf, 5))

# ------------------------------ Read Right ----------------------------------------
with col_right:
    st.markdown(
        "<h3 style='text-align: center;'> GeoJSON</h3>",
        unsafe_allow_html=True
    )

    if right_geojson is not None:
        with st.spinner("Reading file  GeoJSON"):
            try:
                st.session_state.right_gdf = read_geojson(right_geojson)
                st.success("   The file was uploaded successfully. ")
            except ValueError as e:
                st.session_state.right_gdf = None
                st.error(str(e))

    if st.session_state.right_gdf is not None:
        make_map(st.session_state.right_gdf, "Right Layer")
        st.write("  First 5 rows:")
        st.dataframe(preview_gdf(st.session_state.right_gdf, 5))

# ============================================================================
#  Spatial Join (ربط مكاني فقط)
# ============================================================================
st.divider()
st.header(" Spatial Join ")

if st.session_state.left_gdf is None or st.session_state.right_gdf is None:
    st.warning(" Upload the Left and Right files first, then run the spatial join")
else:
    with st.sidebar:
        st.header(" Spatial Join")

        spatial_pred = st.selectbox(
            "اختر العلاقة المكانية:",
            options=["intersects", "contains", "within"],
            index=0
        )

        how_option = st.selectbox(
            " Join type:",
            options=["left", "inner", "right"],
            index=0
        )

        run_spatial = st.button(" Spatial Join")

    if run_spatial:
        with st.spinner("Reading fileSpatial Join..."):
            try:
                left_gdf = st.session_state.left_gdf
                right_gdf = st.session_state.right_gdf

                # عملت توحيد نظام الاحداثيات عشان ما يصير اي خطا
                if left_gdf.crs is not None and right_gdf.crs is not None:
                    if left_gdf.crs != right_gdf.crs:
                        right_gdf = right_gdf.to_crs(left_gdf.crs)

                # هنا تنفيد Spatial Join
                result = gpd.sjoin(
                    left_gdf,
                    right_gdf,
                    how=how_option,
                    op=spatial_pred,
                    
                )

                st.session_state.join_result = result

                if result.empty:
                    st.warning(" No results: No spatial matches were found")
                else:
                    st.success(f" Spatial Join executed successfully. Number of resulting records: {len(result)}")
                    st.subheader(" Results preview (first 10 rows)")
                    st.dataframe(preview_gdf(result, 10))

            except Exception as e:
                st.session_state.join_result = None
                st.error(f"حدث خطأ أثناء Spatial Join: {e}")

# ================================================================================================
#  Attribute Join (ربط وصفي فقط)
# ================================================================================================
st.divider()
st.header(" Attribute Join")

if st.session_state.left_gdf is None or st.session_state.right_gdf is None:
    st.warning(" Upload the Left and Right files first, then run the spatial join")
else:
    left_cols = [c for c in st.session_state.left_gdf.columns if c != "geometry"]
    right_cols = [c for c in st.session_state.right_gdf.columns if c != "geometry"]

    if len(left_cols) == 0 or len(right_cols) == 0:
        st.error("لا توجد أعمدة كافية للربط الوصفي (تحقق من الجداول).")
    else:
        with st.sidebar:
            st.header(" إعدادات Attribute Join")

            left_key = st.selectbox("اختر عمود الربط من Left:", options=left_cols)
            right_key = st.selectbox("اختر عمود الربط من Right:", options=right_cols)

            how_attr = st.selectbox(
                "نوع الربط:",
                options=["left", "inner", "right", "outer"],
                index=0
            )

            run_attr = st.button(" تنفيذ Attribute Join")

        if run_attr:
            with st.spinner("جارٍ تنفيذ Attribute Join"):
                try:
                    left_gdf = st.session_state.left_gdf.copy()
                    right_df = st.session_state.right_gdf.copy()

                    if "geometry" in right_df.columns:
                        right_df = right_df.drop(columns=["geometry"])

                    left_gdf[left_key] = left_gdf[left_key].astype(str)
                    right_df[right_key] = right_df[right_key].astype(str)

                    result_attr = left_gdf.merge(
                        right_df,
                        how=how_attr,
                        left_on=left_key,
                        right_on=right_key,
                        suffixes=("_L", "_R")
                    )

                    st.session_state.attr_result = result_attr

                    if result_attr.empty:
                        st.warning(" لا توجد نتائج: لم يتم العثور على أي تطابق وصفي")
                    else:
                        st.success(f" Attribute Join  executed successfully. Number of resulting records: {len(result_attr)}")
                        st.subheader("  Results preview (first 10 rows)")
                        st.dataframe(preview_gdf(result_attr, 10))

                except Exception as e:
                    st.session_state.attr_result = None
                    st.error(f"حدث خطأ أثناء Attribute Join: {e}")

# ================================================================================================
#  تنزيل النتائج (GeoJSON فقط)
# ==========================================================================================================
st.divider()
st.header(" Run Results ")

final_result = None
final_name = None

if st.session_state.attr_result is not None:
    final_result = st.session_state.attr_result
    final_name = "attribute_join_result.geojson"
elif st.session_state.join_result is not None:
    final_result = st.session_state.join_result
    final_name = "spatial_join_result.geojson"

if final_result is None:
    st.info("نفّذ Spatial Join أو Attribute Join أولاً لتظهر إمكانية التنزيل.")
else:
    if final_result.empty:
        st.info("لا يوجد ملف لتنزيله لأن النتيجة فارغة.")
    else:
        try:
            geojson_bytes = final_result.to_json().encode("utf-8")
            st.download_button(
                label=" تنزيل النتيجة GeoJSON",
                data=geojson_bytes,
                file_name=final_name,
                mime="application/geo+json"
            )
        except Exception as e:
            st.error(f"تعذر تجهيز ملف GeoJSON للتنزيل: {e}")
