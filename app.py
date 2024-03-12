import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import requests

st.set_page_config(layout="wide")

new_title = '''
<p style="font-family:futura; color:#cc0000; font-size: 80px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: -50px;">Categorizing Lyrics</p>
<hr style="border: 1px solid #cc0000; width: 35%; margin: auto;"/>
<p style="font-family:futura; color:#cc0000; font-size: 30px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: 20px;">Song lyrics</p>
'''
st.markdown(new_title, unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])

with col2:
    lyrics = st.text_area('', placeholder="Enter lyrics here...", height=150)
    submit = st.button('Predict Region', use_container_width=900)

regions_geojson_paths = {
    "East Coast": ".streamlit/east_coast.geojson",
    "Dirty South": ".streamlit/dirty_south.geojson",
    "West Coast": ".streamlit/west_coast.geojson"
}

def add_geojson_from_file(m, file_path):
    with open(file_path) as f:
        geojson_data = json.load(f)
    folium.GeoJson(geojson_data, style_function=lambda feature: {
        'fillColor': '#cc0000',
        'color': 'red',
        'weight': 2,
        'fillOpacity': 0.2,
    }).add_to(m)
    return m

def predict_region(lyrics):
    url = "https://hip-hop-symphony-dos-fmjczwc3wq-ew.a.run.app/predict"
    response = requests.get(f"{url}?lyrics={lyrics}")
    if response.status_code == 200:
        return response.json()
    else:
        return "Error: Could not retrieve predictions. Please try again."

if 'highest_percentage_value' not in st.session_state:
    st.session_state['highest_percentage_value'] = 0
if 'predicted_region' not in st.session_state:
    st.session_state['predicted_region'] = None

if submit and lyrics.strip():
    prediction_result = predict_region(lyrics)
    if prediction_result != "Error: Could not retrieve predictions. Please try again.":
        percentages = {key: value for key, value in prediction_result.items() if key.endswith('%')}
        highest_percentage_key = max(percentages, key=percentages.get)
        st.session_state['highest_percentage_value'] = percentages[highest_percentage_key]
        st.session_state['predicted_region'] = prediction_result['Region']

with col2:
    # Initialize the map here to ensure it gets refreshed each time
    m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)

    if st.session_state['predicted_region'] and st.session_state['predicted_region'] in regions_geojson_paths:
        m = add_geojson_from_file(m, regions_geojson_paths[st.session_state['predicted_region']])

    # Display the progress bar based on the stored highest percentage value in the session state
    if st.session_state['highest_percentage_value'] > 0:
        st.progress(st.session_state['highest_percentage_value'])

    # Display the map
    st_folium(m, width=900, height=500)
