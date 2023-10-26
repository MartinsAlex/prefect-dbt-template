import psycopg2
import random
from datetime import datetime, timedelta

# Database configuration
DB_NAME = "mydatabase"
DB_USER = "user"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = 5432

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Create a table for banking orders if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS banking_orders (
    order_id SERIAL PRIMARY KEY,
    account_number VARCHAR(15) NOT NULL,
    beneficiary_account VARCHAR(15),
    amount DECIMAL(20, 2) NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    order_status VARCHAR(20) NOT NULL,
    order_description TEXT,
    currency VARCHAR(5) NOT NULL,
    branch_code VARCHAR(10) NOT NULL
)
''')
conn.commit()

# Generate and insert random data
TRANSACTION_TYPES = ['deposit', 'withdraw', 'transfer']
ORDER_STATUSES = ['successful', 'failed', 'pending']
CURRENCIES = ['USD', 'EUR', 'GBP', 'INR', 'JPY']
BRANCH_CODES = ['BR' + str(i).zfill(4) for i in range(100)]

for _ in range(5_000_000):
    account_number = str(random.randint(10**14, 10**15-1))
    beneficiary_account = str(random.randint(10**14, 10**15-1)) if random.choice(TRANSACTION_TYPES) == 'transfer' else None
    amount = random.uniform(1, 10_000)
    days_ago = random.randint(0, 365*5)  # data from the last 5 years
    transaction_date = (datetime.now() - timedelta(days=days_ago)).date()
    transaction_type = random.choice(TRANSACTION_TYPES)
    order_status = random.choice(ORDER_STATUSES)
    order_description = f"{transaction_type.capitalize()} of ${amount:.2f}"
    currency = random.choice(CURRENCIES)
    branch_code = random.choice(BRANCH_CODES)
    
    cursor.execute('''
    INSERT INTO banking_orders (account_number, beneficiary_account, amount, transaction_date, transaction_type, order_status, order_description, currency, branch_code)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (account_number, beneficiary_account, amount, transaction_date, transaction_type, order_status, order_description, currency, branch_code))
    
    # Commit after every 50,000 records to avoid too much data in memory
    if _ % 50_000 == 0:
        conn.commit()

conn.commit()
cursor.close()
conn.close()
