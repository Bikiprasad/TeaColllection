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

# Page configuration
st.set_page_config(
    page_title="Tea Leaf Collection Tracker",
    page_icon="🍃",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .main-header {
        font-size: 2.5rem;
        color: #2eb886;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: white;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin: 1rem 0;
    }
    .metric-card {
        text-align: center;
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: linear-gradient(45deg, #2eb886, #34d399);
        color: white;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'date_filter_type' not in st.session_state:
    st.session_state.date_filter_type = 'range'

# Sidebar navigation with emojis
st.sidebar.markdown("### 📊 Navigation")
page = st.sidebar.radio(
    "",
    ['🏠 Home', '👥 Add Customer', '📝 Daily Collection', '📅 Collection History', '📈 Statistics']
)
page = page.split(' ', 1)[1]  # Remove emoji from selection

# Rest of your data processing functions remain the same
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
    st.markdown("<h1 class='main-header'>🍃 Tea Leaf Collection Tracker</h1>", unsafe_allow_html=True)

    # Quick stats in modern cards
    collections = collections_to_df(get_collections())
    today = datetime.now().date()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Customers</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(get_customers())), unsafe_allow_html=True)

    with col2:
        total_weight = collections['weight'].sum() if not collections.empty else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Collections</div>
            <div class="metric-value">{:.1f} kg</div>
        </div>
        """.format(total_weight), unsafe_allow_html=True)

    with col3:
        today_weight = collections[
            pd.to_datetime(collections['date']).dt.date == today
        ]['weight'].sum() if not collections.empty else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Today's Collections</div>
            <div class="metric-value">{:.1f} kg</div>
        </div>
        """.format(today_weight), unsafe_allow_html=True)

    # Features section
    st.markdown("""
    <div class="card">
        <h3>📱 Features</h3>
        <ul>
            <li>Easy customer management</li>
            <li>Daily collection tracking</li>
            <li>Detailed collection history</li>
            <li>Advanced analytics and reporting</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # Today's collections in a modern card
    if not collections.empty:
        today_collections = collections[
            pd.to_datetime(collections['date']).dt.date == today
        ]
        if not today_collections.empty:
            st.markdown("""
            <div class="card">
                <h3>📊 Today's Collections</h3>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(
                today_collections,
                column_config={
                    "customer_name": "Customer",
                    "weight": st.column_config.NumberColumn(
                        "Weight (kg)",
                        format="%.1f kg"
                    ),
                    "date": "Date"
                },
                hide_index=True
            )

elif page == 'Add Customer':
    st.markdown("<h1 class='main-header'>👥 Add New Customer</h1>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        with st.form('add_customer_form'):
            name = st.text_input('Customer Name')
            contact = st.text_input('Contact Number (Optional)')
            address = st.text_area('Address (Optional)')

            col1, col2, col3 = st.columns([1,1,1])
            with col2:
                submit = st.form_submit_button('Add Customer', use_container_width=True)

            if submit and name:
                add_customer(name, contact, address)
                st.success('✅ Customer added successfully!')
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
        <h3>📋 Existing Customers</h3>
    </div>
    """, unsafe_allow_html=True)
    customers = customers_to_df(get_customers())
    st.dataframe(
        customers,
        column_config={
            "name": "Customer Name",
            "contact": "Contact",
            "address": "Address"
        },
        hide_index=True
    )

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