import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from utils import load_data, save_data, initialize_data_files

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Ensure data files exist
initialize_data_files()

# Page title and navigation
st.title('Green Tea Leaf Collection Tracker')

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ['Home', 'Add Customer', 'Daily Collection', 'Collection History', 'Statistics']
)

# Load data
customers_df = load_data('customers.csv')
collections_df = load_data('collections.csv')

# Home page
if page == 'Home':
    st.header('Welcome to Tea Leaf Collection Tracker')
    st.write("""
    Use this application to:
    - Add new customers
    - Record daily tea leaf collections
    - View collection history
    - Analyze collection statistics
    """)
    
    # Display today's collections if any
    today = datetime.now().date()
    today_collections = collections_df[
        pd.to_datetime(collections_df['date']).dt.date == today
    ]
    
    if not today_collections.empty:
        st.subheader("Today's Collections")
        st.dataframe(today_collections)

# Add Customer page
elif page == 'Add Customer':
    st.header('Add New Customer')
    
    with st.form('add_customer_form'):
        name = st.text_input('Customer Name')
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
            st.success('Customer added successfully!')

    st.subheader('Existing Customers')
    st.dataframe(customers_df)

# Daily Collection page
elif page == 'Daily Collection':
    st.header('Record Daily Collection')
    
    with st.form('collection_form'):
        date = st.date_input('Collection Date', datetime.now())
        customer = st.selectbox(
            'Select Customer',
            options=customers_df['name'].tolist()
        )
        weight = st.number_input('Weight (kg)', min_value=0.0, step=0.1)
        
        submit = st.form_submit_button('Record Collection')
        
        if submit:
            if weight <= 0:
                st.error('Please enter a valid weight')
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
                st.success('Collection recorded successfully!')

# Collection History page
elif page == 'Collection History':
    st.header('Collection History')
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        customer_filter = st.multiselect(
            'Filter by Customer',
            options=['All'] + customers_df['name'].tolist(),
            default='All'
        )
    with col2:
        date_range = st.date_input(
            'Date Range',
            value=(collections_df['date'].min() if not collections_df.empty else datetime.now(),
                   datetime.now()),
            key='date_range'
        )

    # Apply filters
    filtered_df = collections_df.copy()
    if 'All' not in customer_filter and customer_filter:
        filtered_df = filtered_df[filtered_df['customer_name'].isin(customer_filter)]
    filtered_df = filtered_df[
        (pd.to_datetime(filtered_df['date']) >= pd.to_datetime(date_range[0])) &
        (pd.to_datetime(filtered_df['date']) <= pd.to_datetime(date_range[1]))
    ]
    
    st.dataframe(filtered_df)

# Statistics page
elif page == 'Statistics':
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
