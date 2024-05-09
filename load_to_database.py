from sqlalchemy import create_engine, VARCHAR, Float, Date
import os
import pandas as pd

# Replace 'your_username', 'your_password', and 'your_database' with your actual credentials
username = 'lucca_brandao'
password = os.environ['spy_db_password']
database = 'spy_dpdh'
host = 'dpg-coq36rkf7o1s73ea52eg-a.ohio-postgres.render.com'

# Create a connection string
connection_string = f'postgresql://{username}:{password}@{host}/{database}'

# Create the engine
engine = create_engine(connection_string)

# Test the connection
try:
    connection = engine.connect()
    print("Connection successful!")
except Exception as e:
    print(f"Connection failed! Error: {e}")

df = pd.read_csv('data.csv')

dtype = {
    'created_at': Date,
    'product': VARCHAR(length=255),
    'store_name': VARCHAR(length=255),
    'price': Float,
    'percentage_discount': Float,
    'total_discount': Float
}

df.to_sql('test', engine, if_exists='replace', index=False, dtype=dtype)

# Close the connection
engine.dispose()

print("Data loaded successfully!")