import streamlit as st
import plotly.express as px
import pandas as pd
import json

# Load Data
df_externaldebt = pd.read_csv("externaldebt_enhanced.csv")

#Convert Value column to Millions
df_externaldebt['Value (Millions)'] = df_externaldebt['Value'] / 1e6

indicator_codes = df_externaldebt['Indicator Code'].unique()

df_externaldebt['Year'] = df_externaldebt['refPeriod'].astype(int)

years = sorted(df_externaldebt["Year"].unique())

selected_indicators = {
    'PPG, official creditors (NFL, US$)': 'Official Creditors (PPG)',
    'PPG, bonds (NFL, current US$)': 'Bonds (PPG)',
    'PPG, commercial banks (NFL, current US$)': 'Commercial Banks (PPG)',
    'Commercial banks and other lending (PPG + PNG) (NFL, current US$)': 'Banks & Lending (PPG+PNG)',
    'PNG, bonds (NFL, current US$)': 'Bonds (PNG)',
    'PNG, commercial banks and other creditors (NFL, current US$)': 'Banks & Creditors (PNG)',
    'PPG, other private creditors (NFL, current US$)': 'Other Private (PPG)',
    'PPG, private creditors (NFL, US$)': 'Private Creditors (PPG)'
}


# Interactivity Controls
st.sidebar.header("🔎 Filters")
# 1. Multi-select categories
selected_cats = st.sidebar.multiselect(
    "Filter by Creditor Type:", options=df_externaldebt['IndicatorDescription'], default=df_externaldebt['IndicatorDescription'].unique()
)

# 2. Year range slider
year_min, year_max = int(df_externaldebt['Year'].min()), int(df_externaldebt['Year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range:", min_value=year_min, max_value=year_max,
    value=(year_min, year_max)
)

# Filter Data
filtered_df = df_externaldebt[
    (df_externaldebt["IndicatorDescription"].isin(selected_cats)) &
    (df_externaldebt["Year"] >= selected_years[0]) &
    (df_externaldebt["Year"] <= selected_years[1])
]
# Define and shorten indicator names
selected_indicators = {
    'PPG, official creditors (NFL, US$)': 'Official Creditors (PPG)',
    'PPG, bonds (NFL, current US$)': 'Bonds (PPG)',
    'PPG, commercial banks (NFL, current US$)': 'Commercial Banks (PPG)',
    'Commercial banks and other lending (PPG + PNG) (NFL, current US$)': 'Banks & Lending (PPG+PNG)',
    'PNG, bonds (NFL, current US$)': 'Bonds (PNG)',
    'PNG, commercial banks and other creditors (NFL, current US$)': 'Banks & Creditors (PNG)',
    'PPG, other private creditors (NFL, current US$)': 'Other Private (PPG)',
    'PPG, private creditors (NFL, US$)': 'Private Creditors (PPG)'
}

# Filter and rename
filtered_df = df_externaldebt[df_externaldebt['IndicatorDescription'].isin(selected_indicators.keys())].copy()
filtered_df['CreditorType'] = filtered_df['IndicatorDescription'].replace(selected_indicators)


# Pivot and normalize values per year
pivot_df = filtered_df.pivot_table(
    index=['Year', 'CreditorType'],
    values='Value (Millions)',
    aggfunc='sum'
).reset_index()

pivot_df['TotalPerYear'] = pivot_df.groupby('Year')['Value (Millions)'].transform('sum')
pivot_df['Share (%)'] = (pivot_df['Value (Millions)'] / pivot_df['TotalPerYear']) * 100

# Visualization 1: Stacked Bar Chart Across Years by Category
fig1 = px.box(
    filtered_df,
    x="IndicatorDescription", y="Value (Millions)", color="IndicatorDescription",
    title="Value Distribution by Creditor Type",
    labels={"IndicatorDescription": "Creditor Type", "Value (Millions)": "Value (in Millions USD)"}
)

# Visualization 2: Line Chart of Sum of Debt Across Years
fig2 = px.line(
    pivot_df,
    x="Year", y="Value (Millions)", color="CreditorType",
    markers=True,
    title="Total External Debt Over Time"
)

# Layout on Streamlit Page

with st.container():
    st.subheader("Category Distributions")
    st.plotly_chart(fig1, use_container_width=True)

with st.container():
    st.subheader("Trends Across Years")
    st.plotly_chart(fig2, use_container_width=True)













