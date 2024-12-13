import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Sales Dashboard", page_icon=":bar_chart:", layout="wide")

# Function to load and clean the dataset
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data = data.dropna()  # Remove missing values
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')  # Convert to datetime
    data['Sales'] = data['Price'] * data['Quantity']  # Add Sales column
    return data

# Load the dataset
data_file = 'Sales Transaction v.4a.csv'
try:
    data = load_data(data_file)
except FileNotFoundError:
    st.error(f"File not found: {data_file}")
    st.stop()

# Dashboard Header
st.markdown("<h1 style='text-align: center; color: #FFA500;'>Sales Dashboard</h1>", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.title("Filters")
date_range = st.sidebar.date_input("Select Date Range", [data['Date'].min(), data['Date'].max()])
if len(date_range) == 2:
    filtered_data = data[(data['Date'] >= pd.Timestamp(date_range[0])) & (data['Date'] <= pd.Timestamp(date_range[1]))]
else:
    filtered_data = data

selected_country = st.sidebar.multiselect("Select Country", options=data['Country'].unique(), default=data['Country'].unique())
selected_product = st.sidebar.multiselect("Select Product", options=data['ProductName'].unique(), default=data['ProductName'].unique())
filtered_data = filtered_data[(filtered_data['Country'].isin(selected_country)) & (filtered_data['ProductName'].isin(selected_product))]

# Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Sales", f"${filtered_data['Sales'].sum():,.2f}")
col2.metric("Total Transactions", len(filtered_data))
col3.metric("Total Quantity Sold", filtered_data['Quantity'].sum())

# Sales Over Time Visualization
st.write("### Sales Over Time")
st.line_chart(filtered_data.set_index('Date')['Sales'])

# Top Products with Plotly
st.write("### Top 10 Products by Sales")
top_products = filtered_data.groupby('ProductName')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
fig = px.bar(top_products, x='Sales', y='ProductName', orientation='h', color='Sales', title="Top 10 Products by Sales")
st.plotly_chart(fig)

# Sales by Country with Plotly
st.write("### Sales by Country")
sales_by_country = filtered_data.groupby('Country')['Sales'].sum().sort_values(ascending=False).reset_index()
fig = px.bar(sales_by_country, x='Sales', y='Country', orientation='h', color='Sales', title="Sales by Country")
st.plotly_chart(fig)

# Heatmap for Seasonal Trends
st.write("### Seasonal Sales Heatmap")
heatmap_data = (
    filtered_data.groupby([filtered_data['Date'].dt.year.rename("Year"), filtered_data['Date'].dt.month.rename("Month")])['Sales']
    .sum()
    .reset_index(name="Total Sales")
)
fig = px.density_heatmap(heatmap_data, x='Month', y='Year', z='Total Sales', color_continuous_scale='YlGnBu', title="Seasonal Sales Heatmap")
st.plotly_chart(fig)

# Quantity vs. Sales Scatterplot
st.write("### Quantity vs. Sales")
fig = px.scatter(filtered_data, x='Quantity', y='Sales', color='Country', size='Price', hover_data=['ProductName'], title="Quantity vs. Sales")
st.plotly_chart(fig)

# Predictive Calculator
st.sidebar.write("### Predictive Sales Calculator")
price_input = st.sidebar.number_input("Enter Product Price", min_value=0.0, value=10.0, step=1.0)
quantity_input = st.sidebar.number_input("Enter Quantity Sold", min_value=0, value=1, step=1)
predicted_sales = price_input * quantity_input
st.sidebar.write(f"Predicted Sales: ${predicted_sales:,.2f}")

# Download Filtered Data
@st.cache_data
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_to_csv(filtered_data)
st.download_button(label="Download Filtered Data as CSV", data=csv_data, file_name="filtered_data.csv", mime="text/csv")