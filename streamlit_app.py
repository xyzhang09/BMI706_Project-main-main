import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# Load data from the URL
url = 'https://raw.githubusercontent.com/xyzhang09/BMI706_Project/main/clean_Life_Expectancy_Data.csv'
df = pd.read_csv(url)

# Streamlit app title
st.title("Life Expectancy Comparison Dashboard")

# User input: Select year
year = st.slider('Select Year', int(df['Year'].min()), int(df['Year'].max()), 2014)

# User input: Select the factor to compare with Life Expectancy
factor = st.selectbox('Select a factor to compare with Life Expectancy', 
                      ['Adult Mortality', 'Population', 'GDP', 'infant deaths', 'Alcohol'])

# User input: Select countries (multi-select)
country_options = df['Country'].unique()
selected_countries = st.multiselect('Select countries to visualize', options=country_options, default=country_options)

# Filter the data for the selected year and countries
df2 = df[(df['Year'] == year) & (df['Country'].isin(selected_countries))]

# Load the world topojson data from vega_datasets
source = alt.topo_feature(data.world_110m.url, 'countries')

# Map configuration
width = 600
height = 300
project = 'equirectangular'

# Background map
background = alt.Chart(source).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

# Multi-selector for interactivity
selector = alt.selection_multi(fields=['Country'])

# Base chart for the Life Expectancy and selected factor
chart_base = alt.Chart(source).properties(
    width=width,
    height=height
).project(
    project
).add_selection(
    selector
).transform_lookup(
    lookup="id",
    from_=alt.LookupData(df2, "country-code", ["Life expectancy ", 'Country', factor, 'Year']),
)

# Life Expectancy Chart
le_scale = alt.Scale(domain=[df2['Life expectancy '].min(), df2['Life expectancy '].max()], scheme='oranges')
le_color = alt.Color(field="Life expectancy ", type="quantitative", scale=le_scale)

chart_le = chart_base.mark_geoshape().encode(
    color=le_color,
    tooltip=[alt.Tooltip('Country:N', title='Country'),
             alt.Tooltip('Life expectancy :Q', title='Life Expectancy')]
).transform_filter(
    selector
).properties(
    title=f'Life Expectancy Worldwide in {year}'
)

# Selected Factor Chart
factor_scale = alt.Scale(domain=[df2[factor].min(), df2[factor].max()], scheme='yellowgreenblue')
chart_factor = chart_base.mark_geoshape().encode(
    color=alt.Color(field=factor, type="quantitative", scale=factor_scale),
    tooltip=[alt.Tooltip('Country:N', title='Country'),
             alt.Tooltip(f'{factor}:Q', title=f'{factor}')]
).transform_filter(
    selector
).properties(
    title=f'World {factor} in {year}'
)

# Combine the two charts vertically
chart_combined = alt.vconcat(background + chart_le, background + chart_factor).resolve_scale(
    color='independent'
)

# Display the charts in Streamlit
st.altair_chart(chart_combined, use_container_width=True)
