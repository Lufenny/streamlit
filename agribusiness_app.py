
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Agribusiness Expansion Dashboard", layout="wide")

# --- Load data ---
@st.cache_data
def load_data():
    df = pd.read_csv("FAOSTAT_data_en_2-20-2024.csv")
    df.rename(columns={
        'Area': 'Country',
        'Item': 'Product',
        'Element': 'Metric',
        'Value': 'Amount'
    }, inplace=True)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df = df.dropna(subset=['Amount'])
    return df

df = load_data()

# --- Sidebar filters ---
st.sidebar.header("Filters")
years = df['Year'].unique()
products = df['Product'].unique()
countries = df['Country'].unique()

selected_metric = st.sidebar.selectbox("Select Metric", ["Production", "Yield", "Area harvested"])
selected_years = st.sidebar.slider(
    "Select Year Range",
    min_value=int(df['Year'].min()),
    max_value=int(df['Year'].max()),
    value=(2016, 2022)
)

# Safe default: only select if country is in the data
default_countries = ["India", "Brazil", "Indonesia"]
valid_defaults = [c for c in default_countries if c in countries]

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=sorted(countries),
    default=valid_defaults
)

# --- Filtered data ---
filtered_df = df[
    (df['Metric'] == selected_metric) &
    (df['Year'] >= selected_years[0]) &
    (df['Year'] <= selected_years[1]) &
    (df['Country'].isin(selected_countries))
]

# --- Title ---
st.title("🌾 Agribusiness Expansion Analysis")

# --- Line chart: Production over time ---
st.subheader(f"{selected_metric} Trend Over Time")
line_df = filtered_df.groupby(['Year', 'Country'])['Amount'].sum().reset_index()
fig_line = px.line(
    line_df,
    x="Year", y="Amount", color="Country", markers=True,
    title=f"{selected_metric} Trend (Selected Countries)"
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Bar chart: Total by country ---
st.subheader(f"Total {selected_metric} by Country")
bar_df = filtered_df.groupby('Country')['Amount'].sum().sort_values(ascending=False).reset_index()
fig_bar = px.bar(
    bar_df,
    x='Country', y='Amount', color='Country',
    title=f"Total {selected_metric} ({selected_years[0]}–{selected_years[1]})"
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Optional: Choropleth Map ---
if selected_metric == "Production":
    st.subheader("🌍 Average Production Map")
    avg_df = df[
        (df['Metric'] == "Production") &
        (df['Year'] >= selected_years[0]) &
        (df['Year'] <= selected_years[1])
    ]
    avg_prod = avg_df.groupby('Country')['Amount'].mean().reset_index()
    fig_map = px.choropleth(
        avg_prod,
        locations="Country", locationmode="country names",
        color="Amount", title="Average Production by Country",
        color_continuous_scale="Greens"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# --- Data table ---
st.subheader("📊 Raw Data Table")
st.dataframe(filtered_df)

# --- Footer ---
st.markdown("Created for Agribusiness Expansion Strategy using FAOSTAT data.")
