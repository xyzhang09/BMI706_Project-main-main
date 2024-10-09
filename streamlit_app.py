import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# Load data from the URL
url = 'https://raw.githubusercontent.com/xyzhang09/BMI706_Project/main/clean_Life_Expectancy_Data.csv'
df = pd.read_csv(url)

# Renaming columns for clarity
df.rename(columns={
    'infant deaths': 'Infant Deaths',
    'Life expectancy ': 'Life Expectancy',
    'percentage expenditure': 'GDP Expenditure on Health %', 
    ' BMI ': 'BMI',
    'Hepatitis B': 'Hepatitis B Immunization Coverage %',
    'Diphtheria': 'Diphtheria Immunization Coverage %',
    'Measles ': 'Measles',
    'under-five deaths ':'Under-Five Deaths',
    'Total expenditure': 'Government Expenditure on Health %',
    'Diphtheria ':'Diphtheria',
    ' HIV/AIDS': 'HIV/AIDS',
    ' thinness  1-19 years': 'Thinness 1-19 Years',
    ' thinness 5-9 years': 'Thinness 5-9 Years',
    'Income composition of resources': 'Income Composition of Resources'
}, inplace=True)

# Streamlit app title
st.title("Task 1: Spatial Relationship Between Life Expectancy and Selected Factor")

# Remove rows without a country code
df_clean = df.dropna(subset=['country-code'])

# Task 1: Map Visualization

# Year selection
year = st.slider('Select Year', int(df_clean['Year'].min()), int(df_clean['Year'].max()), 2014, key='year_slider')

# Factor selection with a unique key
factor = st.selectbox('Select a factor to compare with Life Expectancy', 
                      ['Adult Mortality', 'Population', 'GDP', 'Infant Deaths', 'Alcohol', 
                       'GDP Expenditure on Health %', 'Hepatitis B Immunization Coverage %', 'BMI',
                        'Government Expenditure on Health %', 'Diphtheria Immunization Coverage %', 'Schooling'],
                      key='factor_selection_1')

# Country selection with unique key
country_options = df_clean['Country'].unique()
selected_countries = st.multiselect('Select countries to visualize', 
                                    options=country_options, 
                                    default=['Australia', 'China', 'Canada', 'France', 'India', 'Brazil'],
                                    key='country_selection_1')

# Filter the data for the selected year and countries
df2 = df_clean[(df_clean['Year'] == year) & (df_clean['Country'].isin(selected_countries))]

# Check for missing data in the selected factor
missing_data_countries = df2[df2[factor].isna()]['Country'].unique()

# Display warning for missing data
if len(missing_data_countries) > 0:
    st.warning(f"Warning: The following countries have missing data for {factor}: {', '.join(missing_data_countries)}")

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
    from_=alt.LookupData(df2, "country-code", ["Life Expectancy", 'Country', factor, 'Year']),
)

# Life Expectancy Chart
le_scale = alt.Scale(domain=[df2['Life Expectancy'].min(), df2['Life Expectancy'].max()], scheme='oranges')
le_color = alt.Color(field="Life Expectancy", type="quantitative", scale=le_scale)

chart_le = chart_base.mark_geoshape().encode(
    color=le_color,
    tooltip=[alt.Tooltip('Country:N', title='Country'),
             alt.Tooltip('Life Expectancy:Q', title='Life Expectancy')]
).transform_filter(
    selector
).properties(
    title=f'Life Expectancy Worldwide in {year}'
)

# Selected Factor Chart
factor_scale = alt.Scale(domain=[df2[factor].min(), df2[factor].max()], scheme='yellowgreenblue')
chart_factor = chart_base.mark_geoshape().encode(
    color=alt.Color(field=factor, type="quantitative", scale=factor_scale,
                    legend=alt.Legend(
                        title=factor,  
                        labelLimit=200, 
                        titleLimit=250,  
                        labelFontSize=12,  
                        titleFontSize=14,  
                        labelOverlap="greedy", 
                        orient="right" 
                    )),
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

# Task 2: Time-Series Trends Comparison

st.title("Task 2: Temporal Trends of Life Expectancy and Selected Factor")

# Year range selection with unique key
years = st.slider('Select a range of years', int(df_clean['Year'].min()), int(df_clean['Year'].max()), (2000, 2015), key='year_range_slider')

# Factor selection with a unique key
factor2 = st.selectbox('Select a factor to compare with Life Expectancy', 
                      ['Adult Mortality', 'Population', 'GDP', 'Infant Deaths', 'Alcohol', 
                       'GDP Expenditure on Health %', 'Hepatitis B Immunization Coverage %', 'BMI',
                        'Government Expenditure on Health %',  'Diphtheria Immunization Coverage %', 'Schooling'],
                      key='factor_selection_2')

# Country selection with unique key
selected_countries2 = st.multiselect('Select countries to visualize', 
                                    options=country_options, 
                                    default=['Australia', 'China', 'Canada'],
                                    key='country_selection_2')

# Filter the data for the selected range of years and countries
df_filtered = df_clean[(df_clean['Year'] >= years[0]) & (df_clean['Year'] <= years[1]) & (df_clean['Country'].isin(selected_countries2))]

# Check for missing data in the selected factor
missing_data_countries2 = df_filtered[df_filtered[factor2].isna()]['Country'].unique()

# Display warning for missing data
if len(missing_data_countries2) > 0:
    st.warning(f"Warning: The following countries have missing data for {factor2}: {', '.join(missing_data_countries2)}")

# Create a line chart for Life Expectancy
life_expectancy_line = alt.Chart(df_filtered).mark_line().encode(
    x='Year:O',
    y='Life Expectancy:Q',
    color='Country:N',
    tooltip=[alt.Tooltip('Year:O'), alt.Tooltip('Life Expectancy:Q'), alt.Tooltip('Country:N')],
).properties(
    width=600,
    height=300,
    title='Life Expectancy Over Time'
)

# Create a line chart for the selected factor
factor_line_chart = alt.Chart(df_filtered).mark_line().encode(
    x='Year:O',
    y=alt.Y(f'{factor2}:Q', title=factor2),
    color='Country:N',
    tooltip=[alt.Tooltip('Year:O'), alt.Tooltip(f'{factor2}:Q'), alt.Tooltip('Country:N')],
).properties(
    width=600,
    height=300,
    title=f'{factor2} Over Time'
)

# Combine the two charts vertically
combined_chart = alt.vconcat(life_expectancy_line, factor_line_chart).resolve_scale(
    color='independent'
)

# Display the charts in Streamlit
st.altair_chart(combined_chart, use_container_width=True)
