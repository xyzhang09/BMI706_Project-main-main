import streamlit as st
import pandas as pd
import altair as alt
import json
import urllib.request

# Load data from the URL
url = 'https://raw.githubusercontent.com/xyzhang09/BMI706_Project/main/clean_Life_Expectancy_Data.csv'
df = pd.read_csv(url)

# Load the world topojson data from a local file or URL
topojson_url = 'https://raw.githubusercontent.com/xyzhang09/BMI706_Project/main/world_110m_topo.json'
world_topojson = urllib.request.urlopen(topojson_url).read()
world_topojson = json.loads(world_topojson)


source = alt.InlineData(values=world_topojson, format=alt.DataFormat(type="json", property="objects.countries.geometries"))

# Minimal map example
chart = alt.Chart(source).mark_geoshape(
    fill='#aaa',
    stroke='white'
).project('equirectangular').properties(
    width=600,
    height=300
)

st.altair_chart(chart)  
