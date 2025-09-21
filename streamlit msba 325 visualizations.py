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

df_externaldebt = df_externaldebt[df_externaldebt['Year']>=2000]

years = sorted(df_externaldebt["Year"].unique())

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


# Interactivity Controls
st.sidebar.header("🔎 Filters")

# 1. Year range slider
year_min, year_max = int(filtered_df['Year'].min()), int(filtered_df['Year'].max())
selected_years = st.sidebar.slider(
    "Select Year Range:", min_value=year_min, max_value=year_max,
    value=(year_min, year_max)
)

# 2. Multi-select categories
selected_cats = st.sidebar.multiselect(
    "Filter by Creditor Type:", options=filtered_df['CreditorType'].unique(), default=filtered_df['CreditorType'].unique()
)

# Filter Data
filtered_df = filtered_df[
    (filtered_df["CreditorType"].isin(selected_cats)) &
    (filtered_df["Year"] >= selected_years[0]) &
    (filtered_df["Year"] <= selected_years[1])
]

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
    x="CreditorType", y="Value (Millions)", color="CreditorType",
    title="Value Distribution by Creditor Type",
    labels={"IndicatorDescription": "Creditor Type","Year":"Year", "Value (Millions)": "Value (in Millions USD)"}
)

fig1.update_traces(
    hovertemplate='Creditor: %{x}<br>Value: %{y:.2f}M'
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
    st.subheader("Lebanon Gov. Debt Distributions by Creditor")
    st.plotly_chart(fig1, use_container_width=True)

with st.container():
    st.subheader("Lebnanon Gov. Debt Trends Across Years by Debt Type")
    st.plotly_chart(fig2, use_container_width=True)






















