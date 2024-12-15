import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Sales Dashboard", page_icon="📊", layout="wide")

# Function to load and clean the dataset
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data = data.dropna()  # Remove missing values

    # Ensure required columns exist
    required_columns = ['Date', 'Price', 'Quantity', 'Country', 'ProductName']
    if not all(col in data.columns for col in required_columns):
        st.error("The dataset is missing required columns.")
        st.stop()

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
st.markdown("""
    <h1 style="text-align: center; font-size: 3em; color: #4CAF50;">
    📊 Sales Dashboard</h1>
    <p style="text-align: center; font-size: 1.2em; color: #555;">
    Analyze your sales data with interactive visualizations and insights</p>
""", unsafe_allow_html=True)

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date Filter
with st.sidebar.expander("📅 Date Range", expanded=True):
    date_range = st.date_input("Select Date Range", [data['Date'].min(), data['Date'].max()])
    if len(date_range) == 2:
        filtered_data = data[(data['Date'] >= pd.Timestamp(date_range[0])) & (data['Date'] <= pd.Timestamp(date_range[1]))]
    else:
        filtered_data = data

# Country and Product Filters with Default Logic
with st.sidebar.expander("🌍 Country & Product Filters", expanded=False):
    # Country Filter: Default shows all; user can choose one
    selected_country = st.selectbox(
        "Select Country", options=["All"] + list(data['Country'].unique()), index=0
    )
    if selected_country != "All":
        filtered_data = filtered_data[filtered_data['Country'] == selected_country]

    # Product Filter: Default shows all; user can choose one
    selected_product = st.selectbox(
        "Select Product", options=["All"] + list(data['ProductName'].unique()), index=0
    )
    if selected_product != "All":
        filtered_data = filtered_data[filtered_data['ProductName'] == selected_product]

# Advanced Filters
with st.sidebar.expander("⚙️ Advanced Filters", expanded=False):
    # Price Range Filter
    price_range = st.slider(
        "Price Range", float(data['Price'].min()), float(data['Price'].max()),
        (float(data['Price'].min()), float(data['Price'].max()))
    )
    filtered_data = filtered_data[
        (filtered_data['Price'] >= price_range[0]) & (filtered_data['Price'] <= price_range[1])
    ]

    # Quantity Range Filter
    quantity_range = st.slider(
        "Quantity Range", int(data['Quantity'].min()), int(data['Quantity'].max()),
        (int(data['Quantity'].min()), int(data['Quantity'].max()))
    )
    filtered_data = filtered_data[
        (filtered_data['Quantity'] >= quantity_range[0]) & (filtered_data['Quantity'] <= quantity_range[1])
    ]

# Main Dashboard
tab1, tab2, tab3 = st.tabs(["📈 Summary Metrics", "📊 Visualizations", "📥 Data Download"])

# Tab 1: Summary Metrics
with tab1:
    st.markdown("## 🧾 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Sales", f"${filtered_data['Sales'].sum():,.2f}")
    col2.metric("🛒 Total Transactions", f"{len(filtered_data):,}")
    col3.metric("📦 Total Quantity Sold", f"{filtered_data['Quantity'].sum():,}")

    st.markdown("---")
    st.markdown("### Sales Over Time")
    st.line_chart(filtered_data.set_index('Date')['Sales'])

# Tab 2: Visualizations
with tab2:
    st.markdown("## 📊 Visualizations")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 10 Products by Sales")
        top_products = filtered_data.groupby('ProductName')['Sales'].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(top_products, x='Sales', y='ProductName', orientation='h', title="Top 10 Products by Sales")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Sales by Country")
        sales_by_country = filtered_data.groupby('Country')['Sales'].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(sales_by_country, x='Sales', y='Country', orientation='h', title="Sales by Country", color='Sales')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Seasonal Trends Heatmap")
    heatmap_data = filtered_data.groupby([filtered_data['Date'].dt.year.rename("Year"), filtered_data['Date'].dt.month.rename("Month")])['Sales'].sum().reset_index(name="Total Sales")
    fig = px.density_heatmap(heatmap_data, x='Month', y='Year', z='Total Sales', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Quantity vs Sales")
    fig = px.scatter(filtered_data, x='Quantity', y='Sales', color='Country', size='Price', hover_data=['ProductName'], title="Quantity vs Sales")
    st.plotly_chart(fig, use_container_width=True)

# Tab 3: Data Download
with tab3:
    st.markdown("## 📥 Download Filtered Data")
    @st.cache_data
    def convert_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')

    csv_data = convert_to_csv(filtered_data)
    st.download_button(label="Download Filtered Data as CSV", data=csv_data, file_name="filtered_data.csv", mime="text/csv")

    st.dataframe(filtered_data)

# Predictive Sales Calculator (Sidebar)
st.sidebar.markdown("---")
st.sidebar.header("🔮 Predictive Sales Calculator")
price_input = st.sidebar.number_input("Enter Product Price", min_value=0.0, value=10.0, step=1.0)
quantity_input = st.sidebar.number_input("Enter Quantity Sold", min_value=0, value=1, step=1)
predicted_sales = price_input * quantity_input
st.sidebar.write(f"Predicted Sales: **${predicted_sales:,.2f}**")
