import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import calendar
import os
from utils import load_data, save_data, initialize_data_files

# Set page config
st.set_page_config(
    page_title="Tea Leaf Collection Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 20px;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Ensure data files exist
initialize_data_files()

# Load data
customers_df = load_data('customers.csv')
collections_df = load_data('collections.csv')

# Sidebar navigation with icons
st.sidebar.title('🍃 Navigation')
page = st.sidebar.radio(
    "",
    ['🏠 Home', '➕ Add Customer', '📝 Daily Collection', '📊 Collection History', '📈 Statistics']
)

# Home page
if '🏠 Home' in page:
    st.title('🍃 LP Green Leaf Collection')

    # Quick stats in columns
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Customers", len(customers_df))
    with col2:
        today_weight = collections_df[
            pd.to_datetime(collections_df['date']).dt.date == datetime.now().date()
        ]['weight'].sum()
        st.metric("Today's Collection (kg)", f"{today_weight:.2f}")
    with col3:
        total_weight = collections_df['weight'].sum()
        st.metric("Total Collection (kg)", f"{total_weight:.2f}")

    # Today's collections in an expander
    with st.expander("📋 Today's Collections", expanded=True):
        today_collections = collections_df[
            pd.to_datetime(collections_df['date']).dt.date == datetime.now().date()
        ]
        if not today_collections.empty:
            st.dataframe(today_collections, use_container_width=True)
        else:
            st.info("No collections recorded today")

# Add Customer page
elif '➕ Add Customer' in page:
    st.title('Add New Customer')

    with st.form('add_customer_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input('Customer Name')
        with col2:
            contact = st.text_input('Contact Number (Optional)')
        address = st.text_area('Address (Optional)')

        submit = st.form_submit_button('Add Customer')

        if submit and name:
            new_customer = pd.DataFrame({
                'customer_id': [len(customers_df) + 1],
                'name': [name],
                'contact': [contact],
                'address': [address]
            })
            customers_df = pd.concat([customers_df, new_customer], ignore_index=True)
            save_data(customers_df, 'customers.csv')
            st.success('✅ Customer added successfully!')

    with st.expander("📋 Existing Customers", expanded=True):
        st.dataframe(customers_df, use_container_width=True)

# Daily Collection page
elif '📝 Daily Collection' in page:
    st.title('Record Daily Collection')

    with st.form('collection_form', clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input('Collection Date', datetime.now())
        with col2:
            customer = st.selectbox(
                'Select Customer',
                options=customers_df['name'].tolist()
            )
        weight = st.number_input('Weight (kg)', min_value=0.0, step=0.1)

        submit = st.form_submit_button('Record Collection')

        if submit:
            if weight <= 0:
                st.error('⚠️ Please enter a valid weight')
            else:
                customer_id = customers_df[customers_df['name'] == customer]['customer_id'].iloc[0]
                new_collection = pd.DataFrame({
                    'date': [date],
                    'customer_id': [customer_id],
                    'customer_name': [customer],
                    'weight': [weight]
                })
                collections_df = pd.concat([collections_df, new_collection], ignore_index=True)
                save_data(collections_df, 'collections.csv')
                st.success('✅ Collection recorded successfully!')

# Collection History page
elif '📊 Collection History' in page:
    st.title('Collection History')

    # Filters in columns
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        customer_filter = st.multiselect(
            'Filter by Customer',
            options=['All'] + customers_df['name'].tolist(),
            default='All'
        )
    with col2:
        date_filter_type = st.radio('Date Filter Type', ['Single Date', 'Date Range'], horizontal=True)
    with col3:
        st.write("")  # Empty space for alignment

    # Date filter based on selection
    if date_filter_type == 'Single Date':
        selected_date = st.date_input('Select Date', datetime.now())
        filtered_df = collections_df[pd.to_datetime(collections_df['date']).dt.date == selected_date]
    else:
        date_range = st.date_input(
            'Date Range',
            value=(collections_df['date'].min() if not collections_df.empty else datetime.now(),
                   datetime.now()),
            key='date_range'
        )
        filtered_df = collections_df[
            (pd.to_datetime(collections_df['date']) >= pd.to_datetime(date_range[0])) &
            (pd.to_datetime(collections_df['date']) <= pd.to_datetime(date_range[1]))
        ]

    # Apply customer filter
    if 'All' not in customer_filter and customer_filter:
        filtered_df = filtered_df[filtered_df['customer_name'].isin(customer_filter)]

    # Display results
    if not filtered_df.empty:
        st.dataframe(filtered_df.sort_values('date', ascending=False), use_container_width=True)

        # Summary metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Collections", len(filtered_df))
        with col2:
            st.metric("Total Weight (kg)", f"{filtered_df['weight'].sum():.2f}")
    else:
        st.info("No collections found for the selected filters")

# Statistics page
elif '📈 Statistics' in page:
        st.header('Collection Statistics')

        if not collections_df.empty:
            # Total collections by customer
            st.subheader('Total Collections by Customer')
            customer_totals = collections_df.groupby('customer_name')['weight'].sum().reset_index()
            fig1 = px.bar(customer_totals, x='customer_name', y='weight',
                          title='Total Collections by Customer')
            st.plotly_chart(fig1)

            # Daily collections trend
            st.subheader('Daily Collections Trend')
            daily_totals = collections_df.groupby('date')['weight'].sum().reset_index()
            fig2 = px.line(daily_totals, x='date', y='weight',
                           title='Daily Collections Trend')
            st.plotly_chart(fig2)

            # Summary statistics
            st.subheader('Summary Statistics')
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric('Total Customers', len(customers_df))
            with col2:
                st.metric('Total Collections (kg)', f"{collections_df['weight'].sum():.2f}")
            with col3:
                st.metric('Average Daily Collection (kg)',
                         f"{collections_df.groupby('date')['weight'].sum().mean():.2f}")
        else:
            st.info('No collection data available yet.')
