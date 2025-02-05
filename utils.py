import pandas as pd
import os

def initialize_data_files():
    """Initialize data files if they don't exist."""
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Initialize customers.csv if it doesn't exist
    if not os.path.exists('data/customers.csv'):
        customers_df = pd.DataFrame(columns=['customer_id', 'name', 'contact', 'address'])
        customers_df.to_csv('data/customers.csv', index=False)
    
    # Initialize collections.csv if it doesn't exist
    if not os.path.exists('data/collections.csv'):
        collections_df = pd.DataFrame(columns=['date', 'customer_id', 'customer_name', 'weight'])
        collections_df.to_csv('data/collections.csv', index=False)

def load_data(filename):
    """Load data from CSV file."""
    try:
        return pd.read_csv(f'data/{filename}')
    except pd.errors.EmptyDataError:
        if filename == 'customers.csv':
            return pd.DataFrame(columns=['customer_id', 'name', 'contact', 'address'])
        else:
            return pd.DataFrame(columns=['date', 'customer_id', 'customer_name', 'weight'])

def save_data(df, filename):
    """Save data to CSV file."""
    df.to_csv(f'data/{filename}', index=False)
