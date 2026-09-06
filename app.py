import streamlit as st
import leafmap.foliumap as leafmap
import folium
import base64
import json
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import requests
from matplotlib.colors import LinearSegmentedColormap, Normalize
from PIL import Image
from rasterio.features import rasterize
from rasterio.io import MemoryFile
from rasterio.warp import transform_bounds
from rasterio.transform import from_bounds
from io import BytesIO
from urllib.parse import quote, urlencode


st.set_page_config(
    page_title="Elephant Habitat Suitability",
    page_icon="🐘",
    layout="wide",
)


LUND_BROWN = "#543A27"
LUND_BLUE = "#5D6414"
LUND_BACKGROUND = "#FFFDF5"
PALETTE_OCHRE = "#AE873B"
PALETTE_GOLD = "#E5B957"
PALETTE_BEIGE = "#E2D0A2"
PALETTE_SAGE = "#DDD7A6"
PALETTE_INK = "#281A0B"


st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {LUND_BACKGROUND};
        color: {PALETTE_INK};
    }}
    [data-baseweb="tab-list"] [aria-selected="true"]::after,
    [data-baseweb="tab-list"] [aria-selected="true"] > div {{
        background-color: {LUND_BROWN} !important;
        border-color: {LUND_BROWN} !important;
    }}

    [data-testid="stSegmentedControl"] {{
        margin-bottom: 1.25rem;
    }}

    [data-testid="stSegmentedControl"] [role="radiogroup"] {{
        gap: 0;
        border: none !important;
        border-radius: 0;
        background: transparent !important;
        box-shadow: none !important;
    }}

    [data-testid="stSegmentedControl"] [data-baseweb="button-group"],
    [data-testid="stSegmentedControl"] [data-baseweb="button"],
    [data-testid="stSegmentedControl"] [role="radiogroup"] > label {{
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
    }}

    [data-testid="stSegmentedControl"] button {{
        color: {LUND_BLUE} !important;
        background: transparent !important;
        border: none !important;
        border-radius: 0 !important;
        box-shadow: none !important;
        padding: 0.65rem 1.25rem !important;
    }}

    [data-testid="stSegmentedControl"] button:hover,
    [data-testid="stSegmentedControl"] button[aria-checked="true"] {{
        color: {LUND_BROWN} !important;
        background: transparent !important;
    }}

    [data-testid="stSegmentedControl"] button[aria-checked="true"] {{
        position: relative;
        border-bottom: 0 !important;
    }}

    [data-testid="stSegmentedControl"] button[aria-checked="true"]::after {{
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        bottom: -1px;
        height: 2px;
        background: linear-gradient(
            90deg,
            {PALETTE_BEIGE},
            {LUND_BROWN}
        );
    }}

    [data-testid="stSegmentedControl"] * {{
        border-top: none !important;
        border-left: none !important;
        border-right: none !important;
    }}

    [data-testid="stCaptionContainer"] {{
        color: {PALETTE_INK};
    }}

    [data-testid="stIFrame"] {{
        border: 1px solid {PALETTE_SAGE};
        border-radius: 3px;
        overflow: hidden;
    }}

    h1 {{
        color: {LUND_BROWN};
        font-weight: 600;
    }}

    h2, h3 {{
        color: {LUND_BROWN};
    }}

    [data-testid="stSidebar"] {{
        background-color: {LUND_BACKGROUND};
        border-right: none;
        box-shadow: 5px 0 0 rgba(40, 26, 11, 0.16);
        position: relative;
        overflow: hidden;
    }}

    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        inset: 0;
        background-image: url("https://gislinkweb.blob.core.windows.net/$web/Geosolutions/streamlit/elephants.png");
        background-size: cover;
        background-position: 58% center;
        background-repeat: no-repeat;
        filter: grayscale(1) sepia(0.35) contrast(0.8);
        opacity: 0.13;
        pointer-events: none;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        position: relative;
        z-index: 1;
    }}

    .identity-panel {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 320px;
        box-sizing: border-box;
        overflow: hidden;
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 0;
        margin: 0;
        box-shadow: none;
    }}

    .identity-panel::before {{
        display: none;
    }}

    .identity-panel > div {{
        position: relative;
        z-index: 1;
        background: transparent;
        border-radius: 5px;
        padding: 14px;
        width: 100%;
        box-sizing: border-box;
    }}

    [data-testid="stSidebar"] hr {{
        display: none;
    }}

    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > section {{
        scrollbar-width: none;
    }}

    [data-testid="stAppViewContainer"]::-webkit-scrollbar,
    [data-testid="stAppViewContainer"] > section::-webkit-scrollbar {{
        display: none;
        width: 0;
    }}
    .identity-panel p {{
        margin: 0 0 10px 0;
    }}

    .identity-title {{
        color: {LUND_BROWN};
        font-size: 16px;
        font-weight: 400;
        line-height: 1.25;
    }}

    .thesis-label {{
        color: {LUND_BROWN} !important;
        font-weight: 700 !important;
    }}
    .identity-copy {{
        color: {LUND_BLUE};
        font-size: 13px;
        line-height: 1.45;
    }}

    .identity-details {{
        color: {PALETTE_INK};
        font-size: 13px;
        line-height: 1.45;
    }}

    .elephant-panel {{
        margin: 2px 0 18px 0;
        border: 3px solid {PALETTE_INK};
        border-radius: 14px;
        box-shadow: 5px 5px 0 rgba(40, 26, 11, 0.18);
        overflow: hidden;
        background: {PALETTE_GOLD};
    }}

    .elephant-panel img {{
        display: block;
        width: 100%;
        height: 128px;
        object-fit: cover;
        object-position: center;
    }}

    .sidebar-copy {{
        background: transparent;
        border: none;
        border-radius: 0;
        padding: 8px 10px;
        position: relative;
        left: -8px;
        margin: 0 -8px 10px -8px;
        box-shadow: none;
        width: calc(100% + 40px);
        box-sizing: border-box;
    }}

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {{
        color: {LUND_BROWN};
    }}

    [data-testid="stRadio"] label {{
        color: {LUND_BLUE};
    }}

    [data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {{
        color: {LUND_BLUE};
    }}

    [data-testid="stRadio"] input[type="radio"],
    input[type="radio"] {{
        accent-color: {LUND_BROWN};
    }}

    [data-testid="stRadio"] [role="radio"][aria-checked="true"] {{
        background-color: {LUND_BROWN} !important;
        border-color: {LUND_BROWN} !important;
    }}

    [data-testid="stRadio"] [role="radio"][aria-checked="true"] *,
    [data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) > div:first-child,
    [data-testid="stRadio"] [data-baseweb="radio"]:has(input:checked) > div:first-child > div {{
        background-color: {LUND_BROWN} !important;
        border-color: {LUND_BROWN} !important;
    }}

    [data-testid="stRadio"] [data-baseweb="radio"]:hover > div:first-child,
    [data-testid="stRadio"] [data-baseweb="radio"]:focus-within > div:first-child {{
        border-color: {LUND_BROWN} !important;
    }}

    [data-testid="stSlider"] {{
        color: {LUND_BLUE};
    }}

    [data-testid="stSlider"] input[type="range"] {{
        accent-color: {LUND_BROWN};
    }}

    [data-testid="stSlider"] [role="slider"] {{
        background-color: {LUND_BROWN} !important;
        border-color: {LUND_BROWN} !important;
    }}

    [data-testid="stSlider"] [data-baseweb="slider"] div {{
        background-color: {LUND_BROWN} !important;
    }}

    [data-testid="stSlider"] [data-baseweb="slider"] div[style] {{
        background: {LUND_BROWN} !important;
        background-color: {LUND_BROWN} !important;
    }}

    [data-testid="stSlider"] [data-baseweb="slider"]:hover [role="slider"],
    [data-testid="stSlider"] [data-baseweb="slider"]:focus-within [role="slider"] {{
        background-color: {LUND_BROWN} !important;
        border-color: {LUND_BROWN} !important;
        box-shadow: 0 0 0 2px {LUND_BROWN} !important;
    }}

    .lund-info {{
        background-color: {PALETTE_BEIGE};
        border-left: 4px solid {LUND_BLUE};
        padding: 12px 14px;
        margin-top: 15px;
        margin-bottom: 15px;
        border-radius: 3px;
    }}

    .lund-supervisor {{
        background-color: {PALETTE_BEIGE};
        border-left: 4px solid {LUND_BROWN};
        padding: 12px 14px;
        margin-top: 15px;
        margin-bottom: 15px;
        border-radius: 3px;
    }}

    .map-year {{
        color: {LUND_BROWN};
        font-size: 1.35rem;
        font-weight: 600;
        margin-bottom: 0px;
    }}

    .map-description {{
        color: {PALETTE_INK};
        font-size: 0.9rem;
        margin-top: 0px;
        margin-bottom: 8px;
    }}

    hr {{
        border: none;
        border-top: 1px solid {PALETTE_SAGE};
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LUND SIDEBAR
# =========================================================

active_view = st.segmented_control(
    "Map section",
    ["Suitability", "Connectivity"],
    default="Suitability",
    key="active_view",
    label_visibility="collapsed",
)

with st.sidebar:

    st.markdown(
        """
        <div style="
            text-align:left;
            padding:10px 5px 15px 5px;
        ">
            <img
                src="https://www.lunduniversity.lu.se/sites/www.lunduniversity.lu.se/files/Lund_university_L_CMYK.svg"
                style="width:190px;"
            >
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="sidebar-copy">
            <p class="identity-copy thesis-label">Master's Thesis</p>
            <p class="identity-title">
                Forecasting Habitat Suitability for African Savanna Elephants in a Changing World
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # SCENARIO
    # -----------------------------------------------------

    st.markdown("### Climate scenario")

    if active_view == "Connectivity":
        scenario = st.radio(
            "Select scenario",
            [
                "SSP1-2.6",
                "SSP5-8.5",
            ],
            index=1,
            disabled=True,
            label_visibility="collapsed",
        )
    else:
        scenario = st.radio(
            "Select scenario",
            [
                "SSP1-2.6",
                "SSP5-8.5",
            ],
            index=0,
            label_visibility="collapsed",
        )


    # -----------------------------------------------------
    # SEASON
    # -----------------------------------------------------

    st.markdown("### Season")

    season = st.radio(
        "Select season",
        [
            "Wet",
            "Dry",
        ],
        index=0,
        label_visibility="collapsed",
    )


    st.markdown(
        """
        <div class="identity-panel">
            <div>
                <p class="identity-details">
                    <b>Author</b><br>
                    Isabelle Breton<br>
                    <br>
                    <b>Supervisor</b><br>
                    Lanhui Wang<br>
                    <br>
                    Master of Science in Geographical Information Science<br>
                    Department of Earth and Environmental Sciences <br>
                    <b>Lund University</b>
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


opacity = 0.7


# =========================================================
# COG BASE URL
# =========================================================

BASE_URL = (
    "https://gislinkweb.blob.core.windows.net/"
    "$web/Geosolutions/streamlit/"
)

KAZA_BOUNDARY_URL = (
    "https://services5.arcgis.com/diea3OfTcCeAWfEO/"
    "arcgis/rest/services/SADC_TFCA_Boundaries_20250903/FeatureServer/0/query"
    "?where=ABBR%3D%27KAZA%20TFCA%27&outFields=ABBR"
    "&returnGeometry=true&outSR=4326&maxAllowableOffset=0.01&f=geojson"
)

KAZA_BOUNDARY_GEOJSON = requests.get(
    KAZA_BOUNDARY_URL,
    timeout=30,
).json()

LANDCOVER_SERVICE_URL = (
    "https://ic.imagery1.arcgis.com/arcgis/rest/services/"
    "Sentinel2_10m_LandCover/ImageServer/exportImage"
)

SATELLITE_BASEMAP_URL = (
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/tile/{z}/{y}/{x}"
)


KAZA_GEOMETRY = KAZA_BOUNDARY_GEOJSON["features"][0]["geometry"]


def coordinate_pairs(coordinates):

    if coordinates and isinstance(coordinates[0], (int, float)):
        yield coordinates
        return

    for coordinate_group in coordinates:
        yield from coordinate_pairs(coordinate_group)


kaza_coordinates = list(coordinate_pairs(KAZA_GEOMETRY["coordinates"]))
kaza_lons = [coordinate[0] for coordinate in kaza_coordinates]
kaza_lats = [coordinate[1] for coordinate in kaza_coordinates]
kaza_bbox = [
    min(kaza_lons),
    min(kaza_lats),
    max(kaza_lons),
    max(kaza_lats),
]


if KAZA_GEOMETRY["type"] == "Polygon":
    kaza_rings = KAZA_GEOMETRY["coordinates"]
else:
    kaza_rings = [
        ring
        for polygon in KAZA_GEOMETRY["coordinates"]
        for ring in polygon
    ]


LANDCOVER_IMAGE_URL = LANDCOVER_SERVICE_URL + "?" + urlencode({
    "bbox": ",".join(str(value) for value in kaza_bbox),
    "bboxSR": "4326",
    "imageSR": "4326",
    "size": "1200,1200",
    "format": "png32",
    "pixelType": "U8",
    "noData": "0",
    "noDataInterpretation": "esriNoDataMatchAny",
    "geometry": json.dumps({
        "rings": kaza_rings,
        "spatialReference": {"wkid": 4326}
    }, separators=(",", ":")),
    "geometryType": "esriGeometryPolygon",
    "geometrySR": "4326",
    "clip": "true",
    "renderingRule": json.dumps({
        "rasterFunction": "Cartographic Renderer for Visualization and Analysis"
    }, separators=(",", ":")),
    "f": "image",
})


@st.cache_data(show_spinner=False)
def clipped_landcover_data_url(image_url, geometry_json, bounds):

    response = requests.get(
        image_url,
        timeout=60,
    )
    response.raise_for_status()

    image = Image.open(
        BytesIO(response.content)
    ).convert("RGBA")

    width, height = image.size
    west, south, east, north = bounds

    mask = rasterize(
        [(json.loads(geometry_json), 1)],
        out_shape=(height, width),
        transform=from_bounds(
            west,
            south,
            east,
            north,
            width,
            height,
        ),
        fill=0,
        dtype="uint8",
    )

    rgba = np.asarray(image).copy()
    rgba[:, :, 3] = rgba[:, :, 3] * mask

    clipped_image = Image.fromarray(rgba, mode="RGBA")
    output = BytesIO()
    clipped_image.save(output, format="PNG")

    encoded_image = base64.b64encode(
        output.getvalue()
    ).decode("ascii")

    return "data:image/png;base64," + encoded_image


@st.cache_data(show_spinner=False)
def core_habitat_overlay_data(cog_url):

    response = requests.get(cog_url, timeout=60)
    response.raise_for_status()

    with MemoryFile(response.content) as memory_file:
        with memory_file.open() as dataset:
            values = dataset.read(1)
            bounds = transform_bounds(
                dataset.crs,
                "EPSG:4326",
                *dataset.bounds,
            )
            nodata = dataset.nodata

    habitat_mask = values > 0
    if nodata is not None:
        habitat_mask &= values != nodata

    rgba = np.zeros((*values.shape, 4), dtype=np.uint8)
    rgba[habitat_mask] = [84, 58, 39, 255]

    image = Image.fromarray(rgba, mode="RGBA")
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)

    encoded_image = base64.b64encode(
        output.getvalue()
    ).decode("ascii")

    return (
        "data:image/png;base64," + encoded_image,
        [
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]],
        ],
    )


@st.cache_data(show_spinner=False)
def connectivity_overlay_data(cog_url, color=None):

    response = requests.get(cog_url, timeout=60)
    response.raise_for_status()

    with MemoryFile(response.content) as memory_file:
        with memory_file.open() as dataset:
            values = dataset.read(1)
            bounds = transform_bounds(
                dataset.crs,
                "EPSG:4326",
                *dataset.bounds,
            )
            nodata = dataset.nodata
            try:
                native_colormap = dataset.colormap(1)
            except ValueError:
                native_colormap = None

    mask = values > 0
    if nodata is not None:
        mask &= values != nodata

    rgba = np.zeros((*values.shape, 4), dtype=np.uint8)

    if native_colormap:
        color_table = np.array(
            [native_colormap.get(index, (0, 0, 0, 0)) for index in range(256)],
            dtype=np.uint8,
        )
        rgba[mask] = color_table[values[mask]]
    elif color:
        rgba[mask] = [*color, 255]

    image = Image.fromarray(rgba, mode="RGBA")
    output = BytesIO()
    image.save(output, format="PNG", optimize=True)
    encoded_image = base64.b64encode(output.getvalue()).decode("ascii")

    return (
        "data:image/png;base64," + encoded_image,
        [
            [bounds[1], bounds[0]],
            [bounds[3], bounds[2]],
        ],
    )


LANDCOVER_CLIPPED_DATA_URL = clipped_landcover_data_url(
    LANDCOVER_IMAGE_URL,
    json.dumps(KAZA_GEOMETRY, separators=(",", ":")),
    tuple(kaza_bbox),
)


def add_kaza_boundary(m):

    folium.GeoJson(
        KAZA_BOUNDARY_GEOJSON,
        name="KAZA TFCA boundary",
        style_function=lambda feature: {
            "color": LUND_BROWN,
            "weight": 3,
                "fill": False,
                "fillColor": "transparent",
                "fillOpacity": 0,
        },
    ).add_to(m)


def add_suitability_extent_box(m):

    folium.Rectangle(
        bounds=[
            [kaza_bbox[1], kaza_bbox[0]],
            [kaza_bbox[3], kaza_bbox[2]],
        ],
        name="Suitability map extent",
        color="#543A27",
        weight=1,
        opacity=0.45,
        fill=False,
        dash_array="4 5",
        interactive=False,
    ).add_to(m)


def add_landcover_layer(m, layer_opacity):

    folium.raster_layers.ImageOverlay(
        image=LANDCOVER_CLIPPED_DATA_URL,
        bounds=[[kaza_bbox[1], kaza_bbox[0]], [kaza_bbox[3], kaza_bbox[2]]],
        name="Sentinel-2 land cover",
        attribution="Impact Observatory, Microsoft, and Esri",
        show=False,
        opacity=layer_opacity,
    ).add_to(m)


def add_map_controls(m, with_opacity=False, base_opacity=0.8):

    add_metric_scale_control(m)

    folium.TileLayer(
        tiles=SATELLITE_BASEMAP_URL,
        name="Satellite imagery",
        attr="Esri, Maxar, Earthstar Geographics",
        overlay=False,
        control=True,
        show=False,
        max_zoom=19,
        opacity=base_opacity,
    ).add_to(m)

    m.add_layer_control()

    if with_opacity:
        add_integrated_opacity_controls(m, base_opacity)

    add_reorderable_layer_list(m)


def add_reorderable_layer_list(m):

    map_variable = m.get_name()

    reorder_js = f"""
    <style>
        .leaflet-control-layers {{
            width: 360px;
            height: 30px;
            max-width: 30px;
            border: 1px solid #D7C6A0 !important;
            border-radius: 2px !important;
            background: #FFFDF5 !important;
            box-shadow: 0 5px 18px rgba(40, 26, 11, 0.22) !important;
            color: #281A0B;
        }}

        .leaflet-control-container,
        .leaflet-control-container .leaflet-control {{
            position: relative;
            z-index: 2000 !important;
        }}

        .leaflet-control-layers:not(.leaflet-control-layers-expanded) .leaflet-control-layers-list {{
            display: none;
        }}

        .leaflet-control-layers-toggle {{
            width: 30px !important;
            height: 30px !important;
            border: 1px solid #D7C6A0 !important;
            border-radius: 2px !important;
            background-color: #FFFDF5 !important;
            background-image: none !important;
            box-shadow: 0 1px 5px rgba(40, 26, 11, 0.24);
            position: relative;
        }}

        .leaflet-control-layers-toggle::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: url("https://cdn.jsdelivr.net/npm/leaflet@1.9.3/dist/images/layers-2x.png") center / 18px 18px no-repeat;
        }}

        .leaflet-control-layers-toggle:hover {{
            background-color: #E2D0A2 !important;
        }}

        .leaflet-control-layers-expanded {{
            width: 360px !important;
            height: auto !important;
            max-width: 360px !important;
            border-radius: 10px !important;
        }}

        .leaflet-control-layers-list {{
            margin: 0;
            padding: 8px 10px 10px;
            height: auto;
            min-height: 0;
            max-height: 360px;
            box-sizing: border-box;
            overflow-y: auto;
        }}

        .leaflet-control-layers-overlays input[type="checkbox"] {{
            accent-color: #543A27;
        }}

        .leaflet-control-layers-base input[type="radio"] {{
            accent-color: #543A27;
        }}

        .leaflet-control-layers-overlays label {{
            cursor: default;
            display: grid;
            grid-template-columns: minmax(0, 1fr) 92px;
            align-items: center;
            column-gap: 6px;
            min-height: 30px;
            margin: 2px 0;
            padding: 3px 4px;
            border-radius: 3px;
            color: #543A27;
            font-size: 12px;
        }}

        .leaflet-control-layers-overlays label:hover {{
            background: #E2D0A2;
        }}

        .leafmap-layer-drag-handle {{
            display: inline-flex !important;
            align-items: center;
            justify-content: center;
            flex: 0 0 28px;
            width: 28px;
            height: 18px;
            margin-right: 3px;
            color: transparent;
            cursor: grab;
            background-image: radial-gradient(circle, #543A27 1.6px, transparent 2px);
            background: none;
            touch-action: none;
            user-select: none;
            position: relative;
            grid-column: 1;
        }}

        .leafmap-layer-drag-handle::before {{
            content: "";
            position: absolute;
            width: 3px;
            height: 3px;
            left: 6px;
            top: 1px;
            border-radius: 50%;
            background: #543A27;
            box-shadow:
                6px 0 #543A27,
                0 6px #543A27,
                6px 6px #543A27,
                0 12px #543A27,
                6px 12px #543A27;
        }}

        .leafmap-layer-drag-handle:active {{
            cursor: grabbing;
        }}

        .leaflet-control-layers-overlays label.layer-drop-target {{
            outline: 1px dashed #AE873B;
            outline-offset: -1px;
            background: #F3E8CC;
        }}

        .leaflet-control-layers-overlays label[draggable="true"] {{
            cursor: grab;
        }}

        .leaflet-control-layers-overlays label.layer-dragging {{
            cursor: grabbing;
        }}

        .leaflet-control-layers-overlays label > span:nth-child(1) {{
            min-width: 0;
            overflow: visible;
            white-space: normal;
            line-height: 1.25;
        }}

        .leaflet-control-layers-overlays label > span:nth-child(1) > span {{
            white-space: normal;
            overflow-wrap: anywhere;
        }}

        .leafmap-layer-order-button {{
            margin-left: 1px;
            padding: 0 4px;
            color: #543A27;
            border: 0;
            border-radius: 3px;
            background: transparent;
            cursor: pointer;
            font-weight: 700;
        }}

        .leafmap-layer-order-button:hover {{
            background: #AE873B;
            color: #FFFDF5;
        }}

        .leafmap-layer-opacity {{
            display: flex;
            align-items: center;
            gap: 4px;
            justify-content: end;
            width: 92px;
            grid-column: 2;
            color: #5D6414;
            font-size: 10px;
            white-space: nowrap;
        }}

        .leafmap-layer-opacity input {{
            width: 52px;
            flex: 0 0 52px;
            accent-color: #543A27;
            cursor: ew-resize;
        }}

        .leafmap-layer-opacity span {{
            width: 28px;
            text-align: right;
        }}

        .leaflet-control-layers-overlays label > span:nth-child(1) {{
            grid-column: 1;
            min-width: 0;
            width: auto;
        }}

        .leaflet-control-layers-overlays label.layer-dragging {{
            opacity: 0.45;
            background: #E2D0A2;
        }}
    </style>
    <script>
    (function() {{
        function enableLayerReordering() {{
            if (typeof {map_variable} === 'undefined') {{
                setTimeout(enableLayerReordering, 300);
                return;
            }}

            const map = {map_variable};
            const overlayList = document.querySelector(
                '.leaflet-control-layers-overlays'
            );

            if (!overlayList || overlayList.dataset.reorderReady) {{
                return;
            }}

            overlayList.dataset.reorderReady = 'true';
            return;

            let draggedLabel = null;

            function findLayerByName(layerName){{
                let found = null;
                Object.values(map._layers).some(function(layer) {{
                    const options = layer.options || {{}};
                    const name = options.name || layer._layerControlName;
                    if (name === layerName) {{
                        found = layer;
                        return true;
                    }}
                    return false;
                }});

                if (found) {{
                    return found;
                }}

                Object.values(window).some(function(candidate){{
                    if (candidate && candidate.overlays && candidate.overlays[layerName]) {{
                        found = candidate.overlays[layerName];
                        return true;
                    }}
                    return false;
                }});

                return found;
            }}

            function applyLayerOrder() {{
                Array.from(overlayList.querySelectorAll('label')).forEach(function(item, index){{
                    const layer = findLayerByName(item.dataset.layerName);
                    if (!layer) {{
                        return;
                    }}

                    const zIndex = 1000 - index;
                    if (layer.setZIndex) {{
                        layer.setZIndex(zIndex);
                    }}
                    if (layer.eachLayer) {{
                        layer.eachLayer(function(child){{
                            if (child.setZIndex) {{
                                child.setZIndex(zIndex);
                            }}
                        }});
                    }}
                }});
            }}

            function reorderLabel(label, direction) {{
                const labels = Array.from(overlayList.querySelectorAll('label'));
                const index = labels.indexOf(label);
                const target = index + direction;

                if (target < 0 || target >= labels.length) {{
                    return;
                }}

                if (direction < 0) {{
                    overlayList.insertBefore(label, labels[target]);
                }} else {{
                    overlayList.insertBefore(label, labels[target].nextSibling);
                }}

                Array.from(overlayList.querySelectorAll('label')).forEach(function(item, itemIndex) {{
                    const layer = findLayerByName(item.dataset.layerName);
                    if (layer && layer.setZIndex) {{
                        layer.setZIndex(1000 - itemIndex);
                    }}
                    if (layer && layer.eachLayer) {{
                        layer.eachLayer(function(child) {{
                            if (child.setZIndex) {{
                                child.setZIndex(1000 - itemIndex);
                            }}
                        }});
                    }}
                }});
            }}

            overlayList.querySelectorAll('label').forEach(function(label){{
                label.dataset.layerName = label.dataset.layerName || label.textContent.trim();
                label.draggable = true;

                const handle = document.createElement('span');
                handle.className = 'leafmap-layer-drag-handle';
                handle.textContent = '';
                handle.title = 'Drag to change layer order';
                handle.draggable = true;
                label.insertBefore(handle, label.firstChild);

                let pointerDragging = false;
                let pointerId = null;

                handle.addEventListener('pointerdown', function(event){{
                    event.preventDefault();
                    event.stopPropagation();
                    pointerDragging = true;
                    pointerId = event.pointerId;
                    draggedLabel = label;
                    label.classList.add('layer-dragging');
                    handle.setPointerCapture(pointerId);
                }});

                handle.addEventListener('pointermove', function(event){{
                    if (!pointerDragging || event.pointerId !== pointerId) {{
                        return;
                    }}

                    event.preventDefault();
                    const target = document.elementFromPoint(
                        event.clientX,
                        event.clientY
                    );
                    const targetLabel = target && target.closest(
                        '.leaflet-control-layers-overlays label'
                    );

                    if (!targetLabel || targetLabel === draggedLabel) {{
                        return;
                    }}

                    const midpoint = targetLabel.getBoundingClientRect().top
                        + targetLabel.offsetHeight / 2;

                    if (event.clientY < midpoint) {{
                        overlayList.insertBefore(draggedLabel, targetLabel);
                    }} else {{
                        overlayList.insertBefore(
                            draggedLabel,
                            targetLabel.nextSibling
                        );
                    }}

                    applyLayerOrder();
                }});

                handle.addEventListener('pointerup', function(event){{
                    if (event.pointerId !== pointerId) {{
                        return;
                    }}

                    pointerDragging = false;
                    pointerId = null;
                    label.classList.remove('layer-dragging');
                    draggedLabel = null;
                    handle.releasePointerCapture(event.pointerId);
                }});

                handle.addEventListener('pointercancel', function(){{
                    pointerDragging = false;
                    pointerId = null;
                    label.classList.remove('layer-dragging');
                    draggedLabel = null;
                }});

                handle.addEventListener('dragstart', function(event){{
                    draggedLabel = label;
                    label.classList.add('layer-dragging');
                    event.dataTransfer.setData('text/plain', label.dataset.layerName);
                    event.dataTransfer.effectAllowed = 'move';
                }});

                    const labels = Array.from(overlayList.querySelectorAll('label'));
                    if (labels.indexOf(draggedLabel) < labels.indexOf(label)) {{
                        overlayList.insertBefore(draggedLabel, label.nextSibling);
                    }} else {{
                        overlayList.insertBefore(draggedLabel, label);
                    }}

                    applyLayerOrder();
                }});
            }});

            map.on('overlayadd', applyLayerOrder);
            map.on('overlayremove', applyLayerOrder);
            setTimeout(applyLayerOrder, 300);
        }}

        setTimeout(enableLayerReordering, 500);
    }})();
    </script>
    """

    m.get_root().html.add_child(
        folium.Element(reorder_js)
    )


def add_metric_scale_control(m):

    map_variable = m.get_name()

    scale_js = f"""
    <style>
        .leaflet-control-scale {{
            margin-bottom: 28px !important;
        }}

        .leaflet-control-attribution {{
            z-index: 1000;
        }}
    </style>
    <script>
    (function() {{
        function addMetricScale() {{
            if (typeof {map_variable} === 'undefined') {{
                setTimeout(addMetricScale, 300);
                return;
            }}

            L.control.scale({{
                metric: true,
                imperial: false,
                position: 'bottomleft'
            }}).addTo({map_variable});
        }}

        addMetricScale();
    }})();
    </script>
    """

    m.get_root().html.add_child(
        folium.Element(scale_js)
    )


def add_integrated_opacity_controls(m, base_opacity=0.8):

    map_variable = m.get_name()

    opacity_js = f"""
    <script>
    (function() {{
        function setLayerOpacity(layer, value) {{
            if (!layer) {{
                return;
            }}

            if (layer.options) {{
                layer.options.opacity = value;
                layer.options.fillOpacity = value;
            }}

            if (layer.setOpacity) {{
                layer.setOpacity(value);
            }} else if (layer.eachLayer) {{
                layer.eachLayer(function(child) {{
                    setLayerOpacity(child, value);
                }});
            }} else if (layer.setStyle) {{
                layer.setStyle({{
                    opacity: value,
                    fillOpacity: value
                }});
            }}
        }}

        function addOpacitySliders() {{
            if (typeof {map_variable} === 'undefined') {{
                setTimeout(addOpacitySliders, 300);
                return;
            }}

            const map = {map_variable};
            const overlayList = document.querySelector(
                '.leaflet-control-layers-overlays'
            );

            if (!overlayList || overlayList.dataset.opacityReady) {{
                return;
            }}

            overlayList.dataset.opacityReady = 'true';

            function findLayerByName(layerName, layerIndex) {{
                const requestedName = String(layerName).trim();
                let found = null;

                Object.values(window).some(function(candidate){{
                    if (candidate && candidate.overlays && candidate.overlays[requestedName]) {{
                        found = candidate.overlays[requestedName];
                        return true;
                    }}

                    if (!candidate || !Array.isArray(candidate._layers)) {{
                        return false;
                    }}

                    const entry = candidate._layers.find(function(item){{
                        return item && String(item.name || '').trim() === requestedName;
                    }});

                    if (entry && entry.layer) {{
                        found = entry.layer;
                        return true;
                    }}

                    return false;
                }});

                if (found) {{
                    return found;
                }}

                Object.values(map._layers).some(function(layer) {{
                    const options = layer.options || {{}};
                    const names = [
                        options.name,
                        layer._layerControlName,
                        options.layerName
                    ].filter(Boolean).map(function(name) {{
                        return String(name).trim();
                    }});

                    if (names.includes(requestedName)) {{
                        found = layer;
                        return true;
                    }}

                    return false;
                }});

                if (found) {{
                    return found;
                }}

                return null;
            }}

            function keepBasemapsOpaque() {{
                Object.values(window).forEach(function(candidate){{
                    if (!candidate || !candidate.base_layers) {{
                        return;
                    }}

                    Object.values(candidate.base_layers).forEach(function(layer){{
                        if (layer && layer.setOpacity) {{
                            layer.setOpacity({base_opacity});
                        }}
                    }});
                }});

                document.querySelectorAll(
                    '.leaflet-tile-pane > .leaflet-layer'
                ).forEach(function(tileLayer) {{
                    const tile = tileLayer.querySelector('img');
                    if (!tile || !tile.src.includes('titiler.xyz')) {{
                        tileLayer.style.opacity = '{base_opacity}';
                    }}
                }});
            }}

            keepBasemapsOpaque();

            overlayList.querySelectorAll('label').forEach(function(label) {{
                if (label.dataset.layerReorderReady) {{
                    return;
                }}

                label.dataset.layerReorderReady = 'true';
                label.dataset.layerName = label.dataset.layerName || label.textContent.trim();
                const slider = document.createElement('input');
                const layerName = label.dataset.layerName || label.textContent.trim();
                const opacityValue = document.createElement('span');
                const opacityWrap = document.createElement('span');
                const layerIndex = Array.from(
                    overlayList.querySelectorAll('label')
                ).indexOf(label);
                const initialLayer = findLayerByName(layerName, layerIndex);
                label._layerReference = initialLayer;
                const initialOpacity = initialLayer?.options?.opacity ?? 1.0;

                slider.type = 'range';
                slider.min = '0';
                slider.max = '1';
                slider.step = '0.05';
                slider.value = String(initialOpacity);
                slider.title = 'Set layer transparency';
                opacityValue.textContent = Math.round(initialOpacity * 100) + '%';
                opacityWrap.className = 'leafmap-layer-opacity';
                opacityWrap.title = 'Layer opacity';
                opacityWrap.appendChild(slider);
                opacityWrap.appendChild(opacityValue);
                label.appendChild(opacityWrap);

                slider.addEventListener('input', function(event){{
                    event.stopPropagation();
                    const value = Number(event.target.value);
                    const targetLayer = label._layerReference;
                    setLayerOpacity(targetLayer, value);
                    keepBasemapsOpaque();

                    if (targetLayer && targetLayer._image) {{
                        targetLayer._image.style.opacity = value;
                    }}

                    opacityValue.textContent = Math.round(value * 100) + '%';
                }});

                slider.addEventListener('change', function(){{
                    slider.dispatchEvent(new Event('input', {{ bubbles: false }}));
                }});

                slider.addEventListener('click', function(event){{
                    event.stopPropagation();
                }});

                label.addEventListener('dragstart', function(event) {{
                    draggedLabel = label;
                    label.classList.add('layer-dragging');
                    event.dataTransfer.setData('text/plain', layerName);
                    event.dataTransfer.effectAllowed = 'move';
                }});

                label.addEventListener('dragend', function() {{
                    label.classList.remove('layer-dragging');
                    draggedLabel = null;
                }});

                label.addEventListener('dragover', function(event) {{
                    event.preventDefault();
                    event.dataTransfer.dropEffect = 'move';
                }});

                label.addEventListener('drop', function(event) {{
                    event.preventDefault();

                    if (!draggedLabel || draggedLabel === label) {{
                        return;
                    }}

                    if (draggedLabel.compareDocumentPosition(label) & Node.DOCUMENT_POSITION_FOLLOWING) {{
                        overlayList.insertBefore(draggedLabel, label.nextSibling);
                    }} else {{
                        overlayList.insertBefore(draggedLabel, label);
                    }}

                    const orderedLabels = Array.from(
                        overlayList.querySelectorAll('label')
                    );

                    orderedLabels.forEach(function(item, index) {{
                        const layer = findLayerByName(item.textContent.trim());

                        if (!layer) {{
                            return;
                        }}

                        const zIndex = 1000 - index;

                        if (layer.setZIndex) {{
                            layer.setZIndex(zIndex);
                        }}

                        if (layer.eachLayer) {{
                            layer.eachLayer(function(child) {{
                                if (child.setZIndex) {{
                                    child.setZIndex(zIndex);
                                }}

                                if (child.bringToFront) {{
                                    child.bringToFront();
                                }}
                            }});
                        }}

                        if (layer.bringToFront) {{
                            layer.bringToFront();
                        }}
                    }});
                }});
            }});
        }}

        setTimeout(addOpacitySliders, 350);
    }})();
    </script>
    """

    m.get_root().html.add_child(
        folium.Element(opacity_js)
    )


def add_tile_retry(m, url_fragment):

    map_variable = m.get_name()

    retry_js = f"""
    <script>
    (function() {{
        function configureTileRetry() {{
            if (typeof {map_variable} === "undefined") {{
                setTimeout(configureTileRetry, 300);
                return;
            }}

            const map = {map_variable};
            const style = document.createElement("style");
            style.textContent = ".leaflet-tile-pane .leaflet-tile {{ transition: none !important; }}";
            document.head.appendChild(style);
            const layers = Object.values(map._layers).filter(function(layer) {{
                return layer._url && layer._url.includes("{url_fragment}");
            }});

            if (!layers.length) {{
                setTimeout(configureTileRetry, 300);
                return;
            }}

            layers.forEach(function(layer) {{
                if (layer._retryReady) {{
                    return;
                }}

                layer.on("tileerror", function(event){{
                    const tile = event.tile;
                    const coords = event.coords;
                    const retryCount = tile._connectivityRetryCount || 0;

                    if (retryCount >= 3 || !coords) {{
                        return;
                    }}

                    tile._connectivityRetryCount = retryCount + 1;
                    setTimeout(function(){{
                        const tileUrl = layer.getTileUrl(coords);
                        const separator = tileUrl.includes("?") ? "&" : "?";
                        tile.src = tileUrl + separator + "retry=" + Date.now();
                    }}, 500 * (retryCount + 1));
                }});

                layer._retryReady = true;
                layer.options.keepBuffer = 4;
                layer.options.updateWhenIdle = true;
                layer.options.updateWhenZooming = false;

                const container = layer.getContainer();
                if (container) {{
                    container.querySelectorAll('.leaflet-tile').forEach(function(tile) {{
                        tile.style.transition = 'none';
                    }});
                }}
            }});
        }}

        configureTileRetry();
    }})();
    </script>
    """

    m.get_root().html.add_child(
        folium.Element(retry_js)
    )


def add_connectivity_tile_stability(m):

    map_variable = m.get_name()

    stability_js = f"""
    <script>
    (function() {{
        function configureConnectivityTiles() {{
            if (typeof {map_variable} === "undefined") {{
                setTimeout(configureConnectivityTiles, 300);
                return;
            }}

            const map = {map_variable};
            const layers = Object.values(map._layers).filter(function(layer) {{
                return layer._url && layer._url.includes("titiler.xyz");
            }});

            if (!layers.length) {{
                setTimeout(configureConnectivityTiles, 300);
                return;
            }}

            layers.forEach(function(layer) {{
                layer.options.keepBuffer = 4;
                layer.options.updateWhenIdle = true;
                layer.options.updateWhenZooming = false;
            }});
        }}

        configureConnectivityTiles();
    }})();
    </script>
    """

    m.get_root().html.add_child(
        folium.Element(stability_js)
    )


# =========================================================
# COG FILES
# =========================================================

COGS = {

    "Present": {

        "Wet":
            BASE_URL +
            "Present_IUCN_18h_Wet.tif",

        "Dry":
            BASE_URL +
            "Present_IUCN_18h_Dry.tif",
    },


    "2050": {

        "SSP1-2.6": {

            "Wet":
                BASE_URL +
                "Future_Suitability_2050_SSP126_CONSERVATIVE_WET.tif",

            "Dry":
                BASE_URL +
                "Future_Suitability_2050_SSP126_CONSERVATIVE_DRY.tif",
        },


        "SSP5-8.5": {

            "Wet":
                BASE_URL +
                "Future_Suitability_2050_SSP585_CONSERVATIVE_WET.tif",

            "Dry":
                BASE_URL +
                "Future_Suitability_2050_SSP585_CONSERVATIVE_DRY.tif",
        },
    },


    "2100": {

        "SSP1-2.6": {

            "Wet":
                BASE_URL +
                "Future_Suitability_2100_SSP126_CONSERVATIVE_WET.tif",

            "Dry":
                BASE_URL +
                "Future_Suitability_2100_SSP126_CONSERVATIVE_DRY.tif",
        },


        "SSP5-8.5": {

            "Wet":
                BASE_URL +
                "Future_Suitability_2100_SSP585_CONSERVATIVE_WET.tif",

            "Dry":
                BASE_URL +
                "Future_Suitability_2100_SSP585_CONSERVATIVE_DRY.tif",
        },
    },
}


# =========================================================
# GAIN AND LOSS RASTERS
# =========================================================

DIFFERENCE_COGS = {

    "SSP1-2.6": {

        "Wet": BASE_URL + "Difference_2100_Present_SSP126_Wet.tif",

        "Dry": BASE_URL + "Difference_2100_Present_SSP126_Dry.tif",
    },

    "SSP5-8.5": {

        "Wet": BASE_URL + "Difference_2100_Present_SSP585_Wet.tif",

        "Dry": BASE_URL + "Difference_2100_Present_SSP585_Dry.tif",
    },
}


# =========================================================
# TITILER
# =========================================================

def titiler_tile_url(cog_url):

    encoded = quote(
        cog_url,
        safe=""
    )

    return (
        "https://titiler.xyz/cog/tiles/"
        "WebMercatorQuad/{z}/{x}/{y}"
        f"?url={encoded}"
        "&tilesize=512"
    )


# =========================================================
# SELECT RASTERS
# =========================================================

present_cog = COGS["Present"][season]

future_2050_cog = COGS["2050"][scenario][season]

future_2100_cog = COGS["2100"][scenario][season]

difference_cog = DIFFERENCE_COGS[scenario][season]


# =========================================================
# TILE URLS
# =========================================================

present_tile_url = titiler_tile_url(
    present_cog
)

future_2050_tile_url = titiler_tile_url(
    future_2050_cog
)

future_2100_tile_url = titiler_tile_url(
    future_2100_cog
)

difference_tile_url = titiler_tile_url(
    difference_cog
)

# =========================================================
# MAP SETTINGS
# =========================================================

MAP_CENTER = [
    -17.2526,
    23.9368
]

MAP_ZOOM = 5


def add_shared_map_sync(m, map_name):

    map_variable = m.get_name()

    sync_js = f"""
    <script>
    (function() {{
        function initializeSharedSync() {{
            if (typeof {map_variable} === "undefined") {{
                setTimeout(initializeSharedSync, 300);
                return;
            }}

            const map = {map_variable};
            const channel = new BroadcastChannel("elephant_habitat_connectivity_sync");
            let updatingFromSync = false;

            channel.onmessage = function(event) {{
                const data = event.data;
                if (!data || data.source === "{map_name}") {{
                    return;
                }}

                updatingFromSync = true;
                map.setView(
                    [data.lat, data.lng],
                    data.zoom,
                    {{ animate: false }}
                );

                setTimeout(function() {{
                    updatingFromSync = false;
                }}, 150);
            }};

            map.on("moveend", function() {{
                if (updatingFromSync) {{
                    return;
                }}

                const center = map.getCenter();
                channel.postMessage({{
                    source: "{map_name}",
                    lat: center.lat,
                    lng: center.lng,
                    zoom: map.getZoom()
                }});
            }});
        }}

        initializeSharedSync();
    }})();
    </script>
    """

    m.get_root().html.add_child(
        folium.Element(sync_js)
    )


def render_connectivity_legend(title, colors, labels):

    legend_cmap = LinearSegmentedColormap.from_list(
        "connectivity_legend",
        colors,
    )
    legend_fig, legend_ax = plt.subplots(figsize=(14, 0.9))
    legend_fig.subplots_adjust(
        bottom=0.48,
        left=0.02,
        right=0.98,
        top=0.82,
    )
    legend_bar = plt.colorbar(
        plt.cm.ScalarMappable(
            norm=Normalize(vmin=0, vmax=1),
            cmap=legend_cmap,
        ),
        cax=legend_ax,
        orientation="horizontal",
    )
    legend_bar.set_label(title, fontsize=10)
    legend_bar.set_ticks(np.linspace(0, 1, len(labels)))
    legend_bar.set_ticklabels(labels)
    legend_bar.ax.tick_params(labelsize=9)
    st.pyplot(legend_fig, use_container_width=True)


def render_categorical_connectivity_legend(title, colors, labels):

    handles = [
        Patch(facecolor=color, edgecolor="none", label=label)
        for color, label in zip(colors, labels)
    ]
    legend_fig, legend_ax = plt.subplots(figsize=(14, 0.7))
    legend_fig.subplots_adjust(left=0.02, right=0.98, top=0.9, bottom=0.08)
    legend_ax.axis("off")
    legend_ax.legend(
        handles=handles,
        title=title,
        loc="center",
        ncol=len(handles),
        frameon=False,
        fontsize=10,
        title_fontsize=10,
    )
    st.pyplot(legend_fig, use_container_width=True)


if active_view == "Suitability":

    scenario_explanation = (
        "Lower-emission climate pathway"
        if scenario == "SSP1-2.6"
        else "Higher-emission climate pathway"
    )

# =========================================================
    # MAP SECTION
    # =========================================================
    
    st.markdown(
        "### Habitat suitability through time"
    )
    
    st.caption(
        "Zoom or pan any map to explore all three time periods together."
    )

    st.markdown(
        f"""
        <div class="lund-info">
            <b>Selected scenario:</b> {scenario}
            ({scenario_explanation})
            &nbsp;&nbsp; | &nbsp;&nbsp;
            <b>Season:</b> {season}
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    
    # =========================================================
    # MAP SYNCHRONIZATION FUNCTION
    # =========================================================
    
    def add_sync_to_map(m, map_name):
    
        map_variable = m.get_name()
    
        sync_js = f"""
        <script>
    
        (function() {{
    
            /*
             * Wait until Leaflet and the map variable exist.
             *
             * This is important because Folium generates the
             * JavaScript map variable separately from the HTML.
             */
    
            function initializeSynchronization() {{
    
                if (typeof {map_variable} === "undefined") {{
    
                    setTimeout(
                        initializeSynchronization,
                        300
                    );
    
                    return;
                }}
    
    
                const map = {map_variable};

                let suitabilityExtentBox = null;

                if ("{map_name}" === "difference") {{
                    suitabilityExtentBox = L.rectangle(
                        map.getBounds(),
                        {{
                            color: "#543A27",
                            weight: 1.5,
                            opacity: 0.8,
                            fill: false,
                            interactive: false
                        }}
                    ).addTo(map);
                }}

                function updateSuitabilityExtentBox(bounds) {{
                    if (!suitabilityExtentBox || !bounds) {{
                        return;
                    }}

                    suitabilityExtentBox.setBounds([
                        [bounds.south, bounds.west],
                        [bounds.north, bounds.east]
                    ]);
                }}
    
    
                /*
                 * Create a shared BroadcastChannel.
                 *
                 * All three map iframes use exactly the same
                 * channel name.
                 */
    
                const channel = new BroadcastChannel(
                    "elephant_habitat_map_sync"
                );
    
    
                /*
                 * Prevent a received synchronization event from
                 * immediately being broadcast again.
                 */
    
                let updatingFromSync = false;

                const viewStorageKey = "elephant_habitat_view_{map_name}";
                const sharedViewStorageKey = "elephant_habitat_shared_view";

                function saveView() {{

                    const center = map.getCenter();
                    const bounds = map.getBounds();

                    localStorage.setItem(
                        viewStorageKey,
                        JSON.stringify({{
                            lat: center.lat,
                            lng: center.lng,
                            zoom: map.getZoom(),
                            bounds: {{
                                north: bounds.getNorth(),
                                south: bounds.getSouth(),
                                east: bounds.getEast(),
                                west: bounds.getWest()
                            }}
                        }})
                    );
                }}

                function restoreSharedExtent() {{
                    if ("{map_name}" !== "difference") {{
                        return;
                    }}

                    const sharedView = localStorage.getItem(
                        sharedViewStorageKey
                    );

                    if (!sharedView) {{
                        return;
                    }}

                    const view = JSON.parse(sharedView);
                    map.setView(
                        [view.lat, view.lng],
                        view.zoom,
                        {{ animate: false }}
                    );
                    updateSuitabilityExtentBox(view.bounds);
                }}

                function restoreView() {{

                    const savedView = localStorage.getItem(viewStorageKey);

                    if (!savedView) {{
                        return;
                    }}

                    const view = JSON.parse(savedView);

                    map.setView(
                        [view.lat, view.lng],
                        view.zoom,
                        {{ animate: false }}
                    );

                }}
    
    
                /*
                 * ------------------------------------------------
                 * SEND POSITION
                 * ------------------------------------------------
                 */
    
                function sendPosition() {{
    
                    if (updatingFromSync) {{
                        return;
                    }}
    
                    const center = map.getCenter();
                    const bounds = map.getBounds();

                    const message = {{
    
                        source: "{map_name}",
    
                        lat: center.lat,
    
                        lng: center.lng,
    
                        zoom: map.getZoom(),
                        bounds: {{
                            north: bounds.getNorth(),
                            south: bounds.getSouth(),
                            east: bounds.getEast(),
                            west: bounds.getWest()
                        }}
    
                    }};
    
    
                    localStorage.setItem(
                        sharedViewStorageKey,
                        JSON.stringify(message)
                    );

                    channel.postMessage(message);

                }}

    
                /*
                 * ------------------------------------------------
                 * RECEIVE POSITION
                 * ------------------------------------------------
                 */
    
                channel.onmessage = function(event) {{
    
                    const data = event.data;
    
    
                    if (!data) {{
                        return;
                    }}
    
    
                    /*
                     * Ignore our own messages.
                     */
    
                    if (data.source === "{map_name}") {{
                        return;
                    }}
    
    
                    updatingFromSync = true;
    
    
                    /*
                     * Set the exact same center and zoom.
                     *
                     * animate:false is important because it
                     * prevents the maps from drifting apart.
                     */
    
                    map.setView(
    
                        [
                            data.lat,
                            data.lng
                        ],
    
                        data.zoom,
    
                        {{
                            animate: false
                        }}
    
                    );

                    updateSuitabilityExtentBox(data.bounds);

                    saveView();
    
    
                    /*
                     * Allow this map to broadcast again after
                     * Leaflet has finished updating.
                     */
    
                    setTimeout(
                        function() {{
                            updatingFromSync = false;

                            if (
                                "{map_name}" !== "difference"
                                && data.source === "difference"
                            ) {{
                                sendPosition();
                            }}
                        }},
                        150
                    );
    
                }};
    
    
                /*
                 * ------------------------------------------------
                 * MAP MOVEMENT
                 * ------------------------------------------------
                 *
                 * moveend fires after BOTH:
                 *
                 *   - panning
                 *   - zooming
                 *
                 * Therefore the entire map view is synchronized.
                 */
    
                map.on(
                    "moveend",
                    function() {{
                        saveView();
                        sendPosition();
                    }}
                );
    
    
                /*
                 * ------------------------------------------------
                 * INITIAL POSITION
                 * ------------------------------------------------
                 *
                 * Give the other maps the initial position.
                 */
    
                restoreView();
                restoreSharedExtent();

                setTimeout(
                    function() {{
                        sendPosition();
                    }},
                    1000
                );
    
            }}
    
    
            /*
             * Start synchronization.
             */
    
            initializeSynchronization();
    
        }})();
    
        </script>
        """
    
    
        m.get_root().html.add_child(
            folium.Element(sync_js)
        )
    
    
    # =========================================================
    # THREE MAP COLUMNS
    # =========================================================
    
    map_col1, map_col2, map_col3 = st.columns(
        3
    )
    
    
    # =========================================================
    # PRESENT MAP
    # =========================================================
    
    with map_col1:
    
        st.markdown(
            '<div class="map-year">Present</div>',
            unsafe_allow_html=True,
        )
    
        st.markdown(
            f"""
            <div class="map-description">
                Present-day — {season} season
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    
        m_present = leafmap.Map(
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            scale_control=False,
        )
    
    
        m_present.add_tile_layer(
            url=present_tile_url,
            name=f"Present – {season} Season",
            attribution="TiTiler / Azure Blob Storage",
            opacity=opacity,
            min_zoom=0,
            max_zoom=30,
            max_native_zoom=30,
            no_wrap=True,
        )
    
        add_landcover_layer(m_present, opacity)
        add_kaza_boundary(m_present)
    
    
        add_map_controls(m_present, with_opacity=True)
    
    
        # -----------------------------------------------------
        # SYNCHRONIZATION
        # -----------------------------------------------------
    
        add_sync_to_map(
            m_present,
            "present"
        )
    
    
        m_present.to_streamlit(
            height=500
        )
    
    
    # =========================================================
    # 2050 MAP
    # =========================================================
    
    with map_col2:
    
        st.markdown(
            '<div class="map-year">2050</div>',
            unsafe_allow_html=True,
        )
    
        st.markdown(
            f"""
            <div class="map-description">
                {scenario} — {season} season
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    
        m_2050 = leafmap.Map(
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            scale_control=False,
        )
    
    
        m_2050.add_tile_layer(
            url=future_2050_tile_url,
            name=f"2050 – {scenario} – {season}",
            attribution="TiTiler / Azure Blob Storage",
            opacity=opacity,
            min_zoom=0,
            max_zoom=30,
            max_native_zoom=30,
            no_wrap=True,
        )
    
        add_landcover_layer(m_2050, opacity)
        add_kaza_boundary(m_2050)
    
    
        add_map_controls(m_2050, with_opacity=True)
    
    
        # -----------------------------------------------------
        # SYNCHRONIZATION
        # -----------------------------------------------------
    
        add_sync_to_map(
            m_2050,
            "2050"
        )
    
    
        m_2050.to_streamlit(
            height=500
        )
    
    
    # =========================================================
    # 2100 MAP
    # =========================================================
    
    with map_col3:
    
        st.markdown(
            '<div class="map-year">2100</div>',
            unsafe_allow_html=True,
        )
    
        st.markdown(
            f"""
            <div class="map-description">
                {scenario} — {season} season
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    
        m_2100 = leafmap.Map(
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            scale_control=False,
        )
    
    
        m_2100.add_tile_layer(
            url=future_2100_tile_url,
            name=f"2100 – {scenario} – {season}",
            attribution="TiTiler / Azure Blob Storage",
            opacity=opacity,
            min_zoom=0,
            max_zoom=30,
            max_native_zoom=30,
            no_wrap=True,
        )
    
        add_landcover_layer(m_2100, opacity)
        add_kaza_boundary(m_2100)
    
    
        add_map_controls(m_2100, with_opacity=True)
    
    
        # -----------------------------------------------------
        # SYNCHRONIZATION
        # -----------------------------------------------------
    
        add_sync_to_map(
            m_2100,
            "2100"
        )
    
    
        m_2100.to_streamlit(
            height=500
        )
    
    
    # =========================================================
    # SUITABILITY LEGEND
    # =========================================================

    color_values = [
        0.00,
        0.25,
        0.50,
        0.75,
        1.00
    ]

    colors = [
        (0.85, 0.85, 0.85),
        (0.40, 0.60, 0.80),
        (0.60, 0.45, 0.30),
        (0.95, 0.70, 0.40),
        (0.35, 0.20, 0.10)
    ]

    cmap = LinearSegmentedColormap.from_list(
        "elephant_cmap",
        list(zip(color_values, colors))
    )

    norm = Normalize(
        vmin=0,
        vmax=1
    )

    fig, ax = plt.subplots(
        figsize=(14, 1.25)
    )

    fig.subplots_adjust(
        bottom=0.45,
        left=0.02,
        right=0.98,
        top=0.85
    )

    cbar = plt.colorbar(
        plt.cm.ScalarMappable(
            norm=norm,
            cmap=cmap
        ),
        cax=ax,
        orientation="horizontal"
    )

    cbar.set_label(
        "Habitat suitability",
        fontsize=11
    )

    cbar.set_ticks([
        0.0,
        0.2,
        0.4,
        0.6,
        0.8,
        1.0
    ])

    cbar.ax.tick_params(
        labelsize=10
    )

    cbar.set_ticklabels([
        "0.0",
        "0.2",
        "0.4",
        "0.6",
        "0.8",
        "1.0"
    ])

    st.pyplot(
        fig,
        use_container_width=True
    )


    # =========================================================
    # GAIN AND LOSS OVERVIEW MAP
    # =========================================================
    
    st.markdown(
        "### Habitat gain and loss overview"
    )
    
    st.markdown(
        f"""
        <div class="lund-info">
            <b>Selected scenario:</b> {scenario} ({scenario_explanation})
            &nbsp;&nbsp; | &nbsp;&nbsp;
            <b>Season:</b> {season}<br>
            Gain and loss in 2100 compared with present.
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    
    m_difference = leafmap.Map(
        center=MAP_CENTER,
        zoom=MAP_ZOOM,
        scale_control=False,
    )
    
    
    m_difference.add_tile_layer(
        url=difference_tile_url,
        name=f"Gain and loss – 2100 – {scenario} – {season}",
        attribution="TiTiler / Azure Blob Storage",
        opacity=1.0,
        min_zoom=0,
        max_zoom=30,
        max_native_zoom=30,
        no_wrap=True,
        bounds=[
            [kaza_bbox[1], kaza_bbox[0]],
            [kaza_bbox[3], kaza_bbox[2]],
        ],
    )

    add_tile_retry(
        m_difference,
        "Difference_2100_Present"
    )
    
    add_landcover_layer(m_difference, opacity)
    add_kaza_boundary(m_difference)
    
    
    add_map_controls(m_difference, with_opacity=True)
    
    
    add_sync_to_map(
        m_difference,
        "difference"
    )
    
    
    m_difference.to_streamlit(
        height=650
    )


    difference_fig, difference_ax = plt.subplots(
        figsize=(14, 1.25)
    )

    difference_fig.subplots_adjust(
        bottom=0.45,
        left=0.02,
        right=0.98,
        top=0.85
    )

    difference_norm = Normalize(
        vmin=-1,
        vmax=1
    )

    diff_cmap = plt.get_cmap("RdBu")

    difference_cbar = plt.colorbar(
        plt.cm.ScalarMappable(
            norm=difference_norm,
            cmap=diff_cmap
        ),
        cax=difference_ax,
        orientation="horizontal"
    )

    difference_cbar.set_label(
        "Habitat change",
        fontsize=11
    )

    difference_cbar.set_ticks([
        -1.0,
        0.0,
        1.0
    ])

    difference_cbar.set_ticklabels([
        "Loss",
        "No change",
        "Gain"
    ])

    difference_cbar.ax.tick_params(
        labelsize=10
    )

    st.pyplot(
        difference_fig,
        use_container_width=True
    )
if active_view == "Connectivity":

    connectivity_sources = {
        "Present Wet corridors": BASE_URL + "Present_Wet_Corridors.tif",
        "Future Wet corridors": BASE_URL + "Future_Wet_Corridors.tif",
        "Present Dry corridors": BASE_URL + "Present_Dry_Corridors.tif",
        "Future Dry corridors": BASE_URL + "Future_Dry_Corridors.tif",
        "Quality corridors – Present Wet": BASE_URL + "Quality_Corridors_Wet_Present.tif",
        "Quality corridors – Future Wet": BASE_URL + "Quality_Corridors_Wet_Future.tif",
        "Quality corridors – Present Dry": BASE_URL + "Quality_Corridors_Dry_Present.tif",
        "Quality corridors – Future Dry": BASE_URL + "Quality_Corridors_Dry_Future.tif",
        "No-regret corridors – Moderate": BASE_URL + "No_Regret_Moderate.tif",
        "No-regret corridors – Strong": BASE_URL + "No_Regret_Strong.tif",
        "Core habitats": BASE_URL + "Core_Habitats_070.tif",
    }

    core_overlay_url, core_overlay_bounds = core_habitat_overlay_data(
        connectivity_sources["Core habitats"]
    )

    def add_connectivity_layer(connectivity_map, layer_name, show=False):

        if layer_name == "Core habitats":
            overlay_url = core_overlay_url
            overlay_bounds = core_overlay_bounds
        else:
            overlay_url, overlay_bounds = connectivity_overlay_data(
                connectivity_sources[layer_name],
            )

        folium.raster_layers.ImageOverlay(
            image=overlay_url,
            bounds=overlay_bounds,
            name=layer_name,
            attribution="Azure Blob Storage",
            show=show,
            opacity=1.0,
            interactive=False,
        ).add_to(connectivity_map)

    def build_connectivity_map(
        map_title,
        primary_layer,
        map_name,
        extra_layers=None,
        show_core=False,
        height=430,
    ):

        connectivity_map = leafmap.Map(
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            scale_control=False,
        )

        add_connectivity_layer(
            connectivity_map,
            primary_layer,
            show=True,
        )

        for layer_name in extra_layers or []:
            add_connectivity_layer(
                connectivity_map,
                layer_name,
                show=layer_name == "Core habitats" and show_core,
            )

        if "Core habitats" not in (extra_layers or []) and primary_layer != "Core habitats":
            add_connectivity_layer(
                connectivity_map,
                "Core habitats",
                show=show_core,
            )

        add_kaza_boundary(connectivity_map)
        add_map_controls(connectivity_map, with_opacity=True, base_opacity=0.65)
        add_shared_map_sync(connectivity_map, map_name)

        st.markdown(
            f'<div class="map-year">{map_title}</div>',
            unsafe_allow_html=True,
        )
        connectivity_map.to_streamlit(height=height)

    def render_connectivity_grid(map_specs, key_prefix):

        for row_start in range(0, len(map_specs), 2):
            columns = st.columns(2)
            for column, spec in zip(columns, map_specs[row_start:row_start + 2]):
                with column:
                    build_connectivity_map(
                        map_title=spec[0],
                        primary_layer=spec[1],
                        map_name=f"{key_prefix}_{row_start}_{spec[2]}",
                        extra_layers=spec[3],
                    )

    st.markdown("### Corridor layers through time and seasons")
    st.caption(
        "Compare present and future corridor availability in wet and dry seasons. "
        "Core habitats are available in the layer list."
    )
    render_connectivity_grid(
        [
            ("Present Wet", "Present Wet corridors", "present_wet", []),
            ("Future Wet", "Future Wet corridors", "future_wet", []),
            ("Present Dry", "Present Dry corridors", "present_dry", []),
            ("Future Dry", "Future Dry corridors", "future_dry", []),
        ],
        "corridors",
    )
    render_connectivity_legend(
        "Corridor resistance",
        ["#4D9221", "#E5B957", "#D73027"],
        ["Low resistance", "Medium resistance", "High resistance"],
    )
    render_categorical_connectivity_legend(
        "",
        ["#543A27"],
        ["Core habitat"],
    )

    st.markdown("### Quality layers through time and seasons")
    st.caption(
        "Each map shows corridor quality for a present or future condition "
        "in the wet or dry season. Core habitats are available in the layer list."
    )
    render_connectivity_grid(
        [
            ("Present Wet", "Quality corridors – Present Wet", "quality_present_wet", []),
            ("Future Wet", "Quality corridors – Future Wet", "quality_future_wet", []),
            ("Present Dry", "Quality corridors – Present Dry", "quality_present_dry", []),
            ("Future Dry", "Quality corridors – Future Dry", "quality_future_dry", []),
        ],
        "quality",
    )
    render_categorical_connectivity_legend(
        "Corridor quality",
        ["#F28E2B", "#4D9221", "#543A27"],
        ["Moderate", "Strong", "Core habitat"],
    )

    st.markdown("### No-regret corridors")
    st.caption(
        "Explore no-regret corridor candidates and core habitats across seasonal "
        "and future conditions. Quality corridors and core habitats are available "
        "in the layer list."
    )

    no_regret_map = leafmap.Map(
        center=MAP_CENTER,
        zoom=MAP_ZOOM,
        scale_control=False,
    )

    add_connectivity_layer(no_regret_map, "No-regret corridors – Moderate", show=True)
    add_connectivity_layer(no_regret_map, "No-regret corridors – Strong", show=True)
    add_connectivity_layer(no_regret_map, "Core habitats", show=False)

    for quality_layer in [
        "Quality corridors – Present Wet",
        "Quality corridors – Future Wet",
        "Quality corridors – Present Dry",
        "Quality corridors – Future Dry",
    ]:
        add_connectivity_layer(no_regret_map, quality_layer, show=False)

    add_kaza_boundary(no_regret_map)
    add_map_controls(no_regret_map, with_opacity=True, base_opacity=0.65)
    add_shared_map_sync(no_regret_map, "no_regret")

    no_regret_map.to_streamlit(height=560)
    render_categorical_connectivity_legend(
        "No-regret corridors",
        ["#F28E2B", "#4D9221", "#543A27"],
        ["Moderate", "Strong", "Core habitat"],
    )
    

