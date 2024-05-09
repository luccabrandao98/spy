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

query = 'select * from test'
df = pd.read_sql(query, con=connection)

print(df)