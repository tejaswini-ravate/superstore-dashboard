import streamlit as st
import pandas as pd
import plotly.express as px
import us

# Set page config
st.set_page_config(page_title="Superstore Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load data
df = pd.read_csv("Sample - Superstore.csv",encoding='latin1')

# Convert Order Date to datetime and extract year
df['Order Date'] = pd.to_datetime(df['Order Date'])
df['Year'] = df['Order Date'].dt.year

# Sidebar filters
st.sidebar.header("Filter Options")

# Date filter
min_date = df['Order Date'].min()
max_date = df['Order Date'].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Multiselect filters
states = st.sidebar.multiselect("Select States", df['State'].unique(), default=df['State'].unique())
categories = st.sidebar.multiselect("Select Categories", df['Category'].unique(), default=df['Category'].unique())
segments = st.sidebar.multiselect("Select Segments", df['Segment'].unique(), default=df['Segment'].unique())
years = st.sidebar.multiselect("Select Years", sorted(df['Year'].unique()), default=sorted(df['Year'].unique()))

# Filter the dataframe based on selections
filtered_df = df[
    (df['Order Date'] >= pd.to_datetime(date_range[0])) &
    (df['Order Date'] <= pd.to_datetime(date_range[1])) &
    (df['State'].isin(states)) &
    (df['Category'].isin(categories)) &
    (df['Segment'].isin(segments)) &
    (df['Year'].isin(years))
]

# Dashboard Title
st.markdown("<h1 style='color: white; padding-top: 10px;'>Superstore Analytics Dashboard</h1>", unsafe_allow_html=True)

# Display Data Table
st.dataframe(filtered_df)

# Key Metrics
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
avg_discount = filtered_df['Discount'].mean() * 100
total_orders = filtered_df['Order ID'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${total_sales:,.2f}")
col2.metric("Total Profit", f"${total_profit:,.2f}")
col3.metric("Avg. Discount", f"{avg_discount:.2f}%")
col4.metric("Total Orders", f"{total_orders}")

# Visual Insights Section
st.markdown("## Visual Insights")

# Sales by Category
category_sales = filtered_df.groupby('Category')['Sales'].sum().reset_index()
fig1 = px.bar(category_sales, x='Category', y='Sales', title="Sales by Category", color='Category')
st.plotly_chart(fig1, use_container_width=True)

# Top 10 States by Profit
state_profit = filtered_df.groupby('State')['Profit'].sum().reset_index().sort_values(by='Profit', ascending=False).head(10)
fig2 = px.bar(state_profit, x='Profit', y='State', orientation='h', title="Top 10 States by Profit", color='Profit')
st.plotly_chart(fig2, use_container_width=True)

# Sales over Time
sales_trend = filtered_df.groupby('Order Date')['Sales'].sum().reset_index()
fig3 = px.line(sales_trend, x='Order Date', y='Sales', title="Sales Trend Over Time")
st.plotly_chart(fig3, use_container_width=True)

# Make sure state abbreviations are used
state_data = filtered_df.groupby('State')['Profit'].sum().reset_index()
state_data['State Code'] = state_data['State'].apply(lambda x: us.states.lookup(x).abbr if us.states.lookup(x) else None)

# Drop rows where state code couldn't be found
state_data.dropna(subset=['State Code'], inplace=True)

fig_map = px.choropleth(
    state_data,
    locations="State Code",
    locationmode="USA-states",
    color="Profit",
    scope="usa",
    color_continuous_scale="RdBu",
    title="Profit by State (USA)"
)
st.plotly_chart(fig_map, use_container_width=True)
