# extraction_module.py

from sqlalchemy import create_engine
import pandas as pd

def run_extraction(query, connection_string):
    """
    Extract data from the given database using the provided query.

    Parameters:
    - query (str): SQL query for data extraction
    - connection_string (str): SQLAlchemy connection string

    Returns:
    - pd.DataFrame: Extracted data
    """
    
    engine = create_engine(connection_string)
    
    # Use chunksize for memory efficiency
    chunks = []
    for chunk in pd.read_sql(query, engine, chunksize=10000):
        chunks.append(chunk)

    # Concatenate chunks
    data = pd.concat(chunks, axis=0)
    
    return data

