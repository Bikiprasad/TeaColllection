import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from utils import (
    initialize_database,
    get_customers,
    get_collections,
    add_customer,
    add_collection,
    update_collection,
    delete_collection
)

# Initialize database
initialize_database()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'date_filter_type' not in st.session_state:
    st.session_state.date_filter_type = 'range'

# Page title and navigation
st.title('Green Tea Leaf Collection Tracker')

# Sidebar navigation
page = st.sidebar.radio(
    "Navigation",
    ['Home', 'Add Customer', 'Daily Collection', 'Collection History', 'Statistics']
)

# Convert SQLAlchemy results to DataFrames
def customers_to_df(customers):
    return pd.DataFrame([
        {
            'customer_id': c.customer_id,
            'name': c.name,
            'contact': c.contact,
            'address': c.address
        } for c in customers
    ])

def collections_to_df(collections):
    return pd.DataFrame([
        {
            'id': c.id,
            'date': c.date,
            'customer_id': c.customer_id,
            'customer_name': c.customer.name,
            'weight': c.weight
        } for c in collections
    ])

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
    collections = collections_to_df(get_collections())
    if not collections.empty:
        today_collections = collections[
            pd.to_datetime(collections['date']).dt.date == today
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
            add_customer(name, contact, address)
            st.success('Customer added successfully!')

    st.subheader('Existing Customers')
    customers = customers_to_df(get_customers())
    st.dataframe(customers)

# Daily Collection page
elif page == 'Daily Collection':
    st.header('Record Daily Collection')

    customers = get_customers()
    with st.form('collection_form'):
        date = st.date_input('Collection Date', datetime.now())
        customer = st.selectbox(
            'Select Customer',
            options=[c.name for c in customers],
        )
        weight = st.number_input('Weight (kg)', min_value=0.0, step=0.1)

        submit = st.form_submit_button('Record Collection')

        if submit:
            if weight <= 0:
                st.error('Please enter a valid weight')
            else:
                customer_id = next(c.customer_id for c in customers if c.name == customer)
                add_collection(date, customer_id, weight)
                st.success('Collection recorded successfully!')

# Collection History page
elif page == 'Collection History':
    st.header('Collection History')

    customers = get_customers()
    collections = get_collections()
    collections_df = collections_to_df(collections)

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        customer_filter = st.multiselect(
            'Filter by Customer',
            options=['All'] + [c.name for c in customers],
            default='All'
        )
    with col2:
        date_filter_type = st.radio(
            'Date Filter Type',
            options=['Single Date', 'Date Range'],
            key='date_filter_type'
        )
    with col3:
        if date_filter_type == 'Single Date':
            selected_date = st.date_input(
                'Select Date',
                value=datetime.now(),
                key='single_date'
            )
        else:
            start_date, end_date = st.date_input(
                'Date Range',
                value=(
                    collections_df['date'].min() if not collections_df.empty else datetime.now(),
                    datetime.now()
                ),
                key='date_range'
            )

    # Apply filters
    filtered_df = collections_df.copy()
    if 'All' not in customer_filter and customer_filter:
        filtered_df = filtered_df[filtered_df['customer_name'].isin(customer_filter)]

    if date_filter_type == 'Single Date':
        filtered_df = filtered_df[
            pd.to_datetime(filtered_df['date']).dt.date == selected_date
        ]
    else:
        filtered_df = filtered_df[
            (pd.to_datetime(filtered_df['date']).dt.date >= start_date) &
            (pd.to_datetime(filtered_df['date']).dt.date <= end_date)
        ]

    # Display collections with edit/delete options
    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            with st.expander(f"{row['customer_name']} - {row['date']} - {row['weight']}kg"):
                col1, col2 = st.columns(2)
                with col1:
                    new_date = st.date_input('Date', value=row['date'], key=f"date_{row['id']}")
                    new_weight = st.number_input('Weight (kg)', 
                                               value=float(row['weight']), 
                                               min_value=0.0, 
                                               step=0.1,
                                               key=f"weight_{row['id']}")
                    if st.button('Update', key=f"update_{row['id']}"):
                        if update_collection(row['id'], new_date, new_weight):
                            st.success('Collection updated successfully!')
                            st.rerun()
                with col2:
                    if st.button('Delete', key=f"delete_{row['id']}"):
                        if delete_collection(row['id']):
                            st.success('Collection deleted successfully!')
                            st.rerun()
    else:
        st.info('No collections found for the selected filters.')

# Statistics page
elif page == 'Statistics':
    st.header('Collection Statistics')

    collections = get_collections()
    collections_df = collections_to_df(collections)

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
            st.metric('Total Customers', len(get_customers()))
        with col2:
            st.metric('Total Collections (kg)', f"{collections_df['weight'].sum():.2f}")
        with col3:
            st.metric('Average Daily Collection (kg)',
                     f"{collections_df.groupby('date')['weight'].sum().mean():.2f}")
    else:
        st.info('No collection data available yet.')