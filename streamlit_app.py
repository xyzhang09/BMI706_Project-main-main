import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# Load data from the URL
url = 'https://raw.githubusercontent.com/xyzhang09/BMI706_Project/main/clean_Life_Expectancy_Data.csv'
df = pd.read_csv(url)

df.rename(columns={
    'infant deaths': 'Infant Deaths',
    'Life expectancy ': 'Life Expectancy',
    'percentage expenditure': 'Percentage Expenditure', 
    ' BMI ': 'BMI',
    'Measles ': 'Measles',
    'under-five deaths ':'Under-Five Deaths',
    'Total expenditure': 'Total Expenditure',
    'Diphtheria ':'Diphtheria',
    ' HIV/AIDS': 'HIV/AIDS',
    ' thinness  1-19 years': 'Thinness 1-19 Years',
    ' thinness 5-9 years': 'Thinness 5-9 Years',
    'Income composition of resources': 'Income Composition of Resources'
}, inplace=True)

# Streamlit app title
st.title("Life Expectancy Comparison Dashboard")

# Remove rows without a country code
df_clean = df.dropna(subset=['country-code'])

# Proceed with the cleaned data (df_clean instead of df)
year = st.slider('Select Year', int(df_clean['Year'].min()), int(df_clean['Year'].max()), 2014)

# User input: Select the factor to compare with Life Expectancy
factor = st.selectbox('Select a factor to compare with Life Expectancy', 
                      ['Adult Mortality', 'Population', 'GDP', 'Infant Deaths', 'Alcohol'])


# User input: Select countries (multi-select)
country_options = df_clean['Country'].unique()
selected_countries = st.multiselect('Select countries to visualize', 
                                    options=country_options, 
                                    default=['Australia', 'China', 'Canada', 'France', 'India', 'Brazil'])

# Filter the data for the selected year and countries
df2 = df_clean[(df_clean['Year'] == year) & (df_clean['Country'].isin(selected_countries))]

# Check for missing data in the selected factor
missing_data_countries = df2[df2[factor].isna()]['Country'].unique()

# If there are any countries with missing data, display a warning
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
