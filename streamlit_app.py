import altair as alt
import json
import urllib.request

# Load the world topojson data
topojson_url = 'https://raw.githubusercontent.com/your_github_repo/world_110m_topo.json'
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

chart.show()  # or st.altair_chart(chart) in Streamlit
