# load_module.py

from sqlalchemy import create_engine
import pandas as pd

def load(data, connection_string, table_name):
    """
    Load data into the destination database.

    Parameters:
    - data (pd.DataFrame): Data to be loaded
    - connection_string (str): SQLAlchemy connection string
    - table_name (str): Table name where data should be loaded
    """
    
    engine = create_engine(connection_string)
    
    # Use 'multi' method for efficient loading
    data.to_sql(table_name, engine, if_exists='append', index=False, method='multi')

