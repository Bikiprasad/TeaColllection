from datetime import datetime
from models import Customer, Collection, get_db, init_db
import pandas as pd
import os

def initialize_database():
    """Initialize the database and migrate existing data if needed."""
    init_db()

    # Migrate existing data if CSV files exist
    if os.path.exists('data/customers.csv') and os.path.exists('data/collections.csv'):
        migrate_data_to_db()

def migrate_data_to_db():
    """Migrate data from CSV files to database."""
    db = next(get_db())

    # Migrate customers
    if os.path.exists('data/customers.csv'):
        customers_df = pd.read_csv('data/customers.csv')
        for _, row in customers_df.iterrows():
            customer = Customer(
                customer_id=row['customer_id'],
                name=row['name'],
                contact=row['contact'],
                address=row['address']
            )
            db.merge(customer)

    # Migrate collections
    if os.path.exists('data/collections.csv'):
        collections_df = pd.read_csv('data/collections.csv')
        for _, row in collections_df.iterrows():
            collection = Collection(
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                customer_id=row['customer_id'],
                weight=row['weight']
            )
            db.add(collection)

    db.commit()

def get_customers():
    """Get all customers from database."""
    db = next(get_db())
    return db.query(Customer).all()

def get_collections():
    """Get all collections from database."""
    db = next(get_db())
    return db.query(Collection).all()

def add_customer(name, contact, address):
    """Add a new customer to database."""
    db = next(get_db())
    customer = Customer(name=name, contact=contact, address=address)
    db.add(customer)
    db.commit()
    return customer

def add_collection(date, customer_id, weight):
    """Add a new collection to database."""
    db = next(get_db())
    collection = Collection(date=date, customer_id=customer_id, weight=weight)
    db.add(collection)
    db.commit()
    return collection

def update_collection(collection_id, date, weight):
    """Update an existing collection."""
    db = next(get_db())
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if collection:
        collection.date = date
        collection.weight = weight
        db.commit()
        return collection
    return None

def delete_collection(collection_id):
    """Delete a collection."""
    db = next(get_db())
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if collection:
        db.delete(collection)
        db.commit()
        return True
    return False