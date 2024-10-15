import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

url = 'https://raw.githubusercontent.com/xyzhang09/BMI706_Project/main/clean_Life_Expectancy_Data.csv'
df = pd.read_csv(url)

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

st.title("Task 1: Spatial Relationship Between Life Expectancy and Selected Factor")


df_clean = df.dropna(subset=['country-code'])

# Task 1

# year slider
year = st.slider('Select Year', int(df_clean['Year'].min()), int(df_clean['Year'].max()), 2014, key='year_slider')

# factor selector
factor = st.selectbox('Select a factor to compare with Life Expectancy', 
                      ['Adult Mortality', 'Population', 'GDP', 'Infant Deaths', 'Alcohol', 
                       'GDP Expenditure on Health %', 'Hepatitis B Immunization Coverage %', 'BMI',
                        'Government Expenditure on Health %', 'Diphtheria Immunization Coverage %', 'Schooling'],
                      key='factor_selection_1')

# country selector
country_options = df_clean['Country'].unique()
selected_countries = st.multiselect('Select countries to visualize', 
                                    options=country_options, 
                                    default=['Australia', 'China', 'Canada', 'France', 'India', 'Brazil'],
                                    key='country_selection_1')

df2 = df_clean[(df_clean['Year'] == year) & (df_clean['Country'].isin(selected_countries))]

# check for missing data in the selected factor and countries
missing_data_countries = df2[df2[factor].isna()]['Country'].unique()
if len(missing_data_countries) > 0:
    st.warning(f"Warning: The following countries have missing data for {factor}: {', '.join(missing_data_countries)}")

source = alt.topo_feature(data.world_110m.url, 'countries')
width = 600
height = 300
project = 'equirectangular'

background = alt.Chart(source).mark_geoshape(
    fill='#aaa',
    stroke='white'
).properties(
    width=width,
    height=height
).project(project)

selector = alt.selection_multi(fields=['Country'])

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

# chart 1
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

# chart 2
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

chart_combined = alt.vconcat(background + chart_le, background + chart_factor).resolve_scale(
    color='independent'
)

st.altair_chart(chart_combined, use_container_width=True)

# Task 2

st.title("Task 2: Temporal Trends of Life Expectancy and Selected Factor")
years = st.slider('Select a range of years', int(df_clean['Year'].min()), int(df_clean['Year'].max()), (2000, 2015), key='year_range_slider')

factor2 = st.selectbox('Select a factor to compare with Life Expectancy', 
                      ['Adult Mortality', 'Population', 'GDP', 'Infant Deaths', 'Alcohol', 
                       'GDP Expenditure on Health %', 'Hepatitis B Immunization Coverage %', 'BMI',
                        'Government Expenditure on Health %',  'Diphtheria Immunization Coverage %', 'Schooling'],
                      key='factor_selection_2')

selected_countries2 = st.multiselect('Select countries to visualize', 
                                    options=country_options, 
                                    default=['Australia', 'China', 'Canada'],
                                    key='country_selection_2')

df_filtered = df_clean[(df_clean['Year'] >= years[0]) & (df_clean['Year'] <= years[1]) & (df_clean['Country'].isin(selected_countries2))]

missing_data_countries2 = df_filtered[df_filtered[factor2].isna()]['Country'].unique()
if len(missing_data_countries2) > 0:
    st.warning(f"Warning: The following countries have missing data for {factor2}: {', '.join(missing_data_countries2)}")

# line chart for Life Expectancy
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

# line chart for the selected factor
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

combined_chart = alt.vconcat(life_expectancy_line, factor_line_chart).resolve_scale(
    color='independent'
)
st.altair_chart(combined_chart, use_container_width=True)

# Task 3:
feature_aggregation = {
    'Adult Mortality': 'mean',
    'Population': 'sum',  
    'GDP': 'mean',
    'Infant Deaths': 'sum',  
    'Alcohol': 'mean',
    'GDP Expenditure on Health %': 'mean',
    'Hepatitis B Immunization Coverage %': 'mean',
    'BMI': 'mean',
    'Government Expenditure on Health %': 'mean',
    'Diphtheria': 'mean',
    'Schooling': 'mean',
    'Life Expectancy': 'mean'
}



aggregated_data = pd.DataFrame()


for feature, agg_func in feature_aggregation.items():
    feature_data = df.groupby('Year').agg({feature: agg_func}).reset_index()
    feature_data['Feature'] = feature  
    feature_data = feature_data.rename(columns={feature: 'Value'})  
    aggregated_data = pd.concat([aggregated_data, feature_data], ignore_index=True)


life_expectancy_data = aggregated_data[aggregated_data['Feature'] == 'Life Expectancy']


feature_list = [feature for feature in aggregated_data['Feature'].unique() if feature != 'Life Expectancy']
selected_feature = st.selectbox('Select a feature to compare with Life Expectancy', feature_list)


selected_feature_data = aggregated_data[(aggregated_data['Feature'] == selected_feature)]


# Left chart: Selected Feature 
selected_feature_chart = alt.Chart(selected_feature_data).mark_bar(color='black').encode(
    x=alt.X('Value:Q', axis=alt.Axis(title=selected_feature), scale=alt.Scale(reverse=True)),
    y=alt.Y('Year:O', sort='-x', axis=alt.Axis(labels=False, ticks=False))
).properties(
    width=300,
    height=400
)

# Right chart: Life Expectancy
life_expectancy_chart = alt.Chart(life_expectancy_data).mark_bar(color='green').encode(
    x=alt.X('Value:Q', title='Life Expectancy'),
    y=alt.Y('Year:O', sort='-x', title= None)  # Only one chart will have the y-axis title
).properties(
    width=300,
    height=400
)


# Combine two charts 
mirrored_chart = alt.hconcat(
    selected_feature_chart,
    life_expectancy_chart,
    spacing=10
).resolve_scale(
    y='shared'
).properties(
    title=f"Diverging Bar Chart: Life Expectancy vs {selected_feature} (2000-2015)"
)


st.altair_chart(mirrored_chart, use_container_width=True)
