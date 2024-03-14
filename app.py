import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import requests

# Set page config
st.set_page_config(layout="wide")

# Page selector
page = st.sidebar.radio('Navigate', ['Categorizing Lyrics', 'Rap Generator GPT2', 'Rap Generator RNN'])

if page == 'Categorizing Lyrics':
    new_title = '''
    <p style="font-family:futura; color:#cc0000; font-size: 80px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: -50px;">Categorizing Lyrics</p>
    <hr style="border: 1px solid #cc0000; width: 35%; margin: auto;"/>
    <p style="font-family:futura; color:#cc0000; font-size: 30px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: 20px;">Song lyrics</p>
    '''
    st.markdown(new_title, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        lyrics = st.text_area('', placeholder="Enter lyrics here...", height=150)
        submit = st.button('Predict Region', use_container_width=True)

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
        accuracy_column, progress_bar_col, percentage_text_col = st.columns([0.4, 1.4, 0.1])

        with accuracy_column:
            if st.session_state['highest_percentage_value'] > 0:
                st.markdown(f"Accuracy of Prediction", unsafe_allow_html=True)

        with progress_bar_col:
            if st.session_state['highest_percentage_value'] > 0:
                st.progress(st.session_state['highest_percentage_value'])

        with percentage_text_col:
            if st.session_state['highest_percentage_value'] > 0:
                st.markdown(f"**{st.session_state['highest_percentage_value'] * 100:.0f}%**", unsafe_allow_html=True)

        m = folium.Map(location=[37.0902, -95.7129], zoom_start=4)
        if st.session_state['predicted_region'] and st.session_state['predicted_region'] in regions_geojson_paths:
            m = add_geojson_from_file(m, regions_geojson_paths[st.session_state['predicted_region']])
        st_folium(m, width=900, height=500)

elif page == 'Rap Generator GPT2':
    new_title = '''
    <p style="font-family:futura; color:#cc0000; font-size: 80px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: -50px;">Rap Generator GPT2</p>
    <hr style="border: 1px solid #cc0000; width: 35%; margin: auto;"/>
    <p style="font-family:futura; color:#cc0000; font-size: 30px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: 20px;">Start of Rap</p>
    '''
    st.markdown(new_title, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        lyrics = st.text_area('', placeholder="Enter lyrics here...", height=50)
        max_length = st.slider("Max Length", min_value=20, max_value=100, value=50)
        submit = st.button('Start Generating bars!', use_container_width=True)

        if submit:
            encoded_lyrics = requests.utils.quote(lyrics)
            # Prepare the API request URL
            api_url = f"https://hip-hop-symphony-gen-fmjczwc3wq-ew.a.run.app/predict_gen_gpt?lyrics={encoded_lyrics}&max_length={max_length}"
            # Make a GET request to the API
            response = requests.get(api_url)

            if response.status_code == 200:
                # Extract the generated lyrics from the response
                generated_lyrics = response.json().get('lyrics', 'No lyrics generated.')
                st.markdown(f'''
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
                        <p style="font-size: 20px; margin: 0;">{generated_lyrics}</p>
                    </div>
                    ''', unsafe_allow_html=True)
            else:
                st.error("Failed to generate lyrics. Please try again.")

elif page == 'Rap Generator RNN':
    new_title = '''
    <p style="font-family:futura; color:#cc0000; font-size: 80px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: -50px;">Rap Generator RNN</p>
    <hr style="border: 1px solid #cc0000; width: 35%; margin: auto;"/>
    <p style="font-family:futura; color:#cc0000; font-size: 30px; font-weight: bold; text-align: center; white-space: nowrap; margin-top: 20px;">Generate Rap</p>
    '''
    st.markdown(new_title, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        submit = st.button('Start Generating bars!', use_container_width=True)

        if submit:
            try:
                response = requests.get('https://hip-hop-symphony-gen-fmjczwc3wq-ew.a.run.app/predict_gen_RNN')
                data = response.json()

                lyrics = data.get('lyrics', 'No lyrics generated')
                lyrics_html = lyrics.replace("\n", "<br>")
                st.markdown(f'''
                    <div style="background-color: #f0f0f0; padding: 10px; border-radius: 10px;">
                        <p style="font-size: 20px; margin: 0;">{lyrics_html}</p>
                    </div>
                    ''', unsafe_allow_html=True)


            except Exception as e:
                st.error(f"An error occurred: {e}")
