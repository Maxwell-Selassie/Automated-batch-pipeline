import random
import csv
import os
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()
random.seed(42)
Faker.seed(42)

os.makedirs('banking_data', exist_ok=True)

# ── CONFIG ──────────────────────────────────────────────
NUM_CUSTOMERS    = 15000
NUM_BRANCHES     = 30
NUM_EMPLOYEES    = 500
NUM_ACCOUNTS     = 22000   # ~1.5 accounts per customer
NUM_TRANSACTIONS = 500000

# One month window: March 2025
START_DATE = datetime(2025, 3, 1)
END_DATE   = datetime(2025, 3, 31, 23, 59, 59)

def random_timestamp():
    delta = END_DATE - START_DATE
    return START_DATE + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

# ── 1. BRANCHES ─────────────────────────────────────────
cities = [
    'Accra', 'Kumasi', 'Tamale', 'Takoradi', 'Cape Coast',
    'Sunyani', 'Koforidua', 'Ho', 'Bolgatanga', 'Wa',
    'Tema', 'Ashaiman', 'Kasoa', 'Madina', 'Aflao',
    'Obuasi', 'Teshie', 'Nungua', 'Dome', 'Techiman',
    'Berekum', 'Kintampo', 'Salaga', 'Yendi', 'Bawku',
    'Navrongo', 'Lawra', 'Tumu', 'Damongo', 'Bole'
]

branches = []
for i in range(1, NUM_BRANCHES + 1):
    branches.append({
        'branch_id': i,
        'branch_name': f"{cities[i-1]} Branch",
        'city': cities[i-1]
    })

# ── 2. ADDRESSES ─────────────────────────────────────────
print("Generating addresses...")
addresses = []
total_addresses = NUM_CUSTOMERS + NUM_EMPLOYEES
for i in range(1, total_addresses + 1):
    addresses.append({
        'address_id': i,
        'street_name': fake.street_address(),
        'city_name': fake.city(),
        'region': random.choice([
            'Greater Accra', 'Ashanti', 'Northern', 'Western',
            'Central', 'Volta', 'Eastern', 'Bono', 'Upper East', 'Upper West',
            'Savannah', 'North East', 'Oti', 'Bono East', 'Ahafo', 'Western North'
        ]),
        'digital_address': f"GH-{fake.bothify(text='???-####').upper()}"
    })

# ── 3. CUSTOMERS ─────────────────────────────────────────
print("Generating customers...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        'customer_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.unique.email(),
        'primary_phone': fake.phone_number()[:10],
        'created_at': fake.date_time_between(start_date='-7y', end_date='-1m')
    })

# ── 4. CUSTOMER_ADDRESS ───────────────────────────────────
customer_address = []
for c in customers:
    customer_address.append({
        'customer_id': c['customer_id'],
        'address_id': c['customer_id'],
        'is_active': True
    })

# ── 5. EMPLOYEES ─────────────────────────────────────────
print("Generating employees...")
employees = []
for i in range(1, NUM_EMPLOYEES + 1):
    employees.append({
        'employee_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.unique.email(),
        'primary_phone': fake.phone_number()[:15],
        'branch_id': random.randint(1, NUM_BRANCHES)
    })

# ── 6. EMPLOYEE_ADDRESS ───────────────────────────────────
employee_address = []
for e in employees:
    employee_address.append({
        'employee_id': e['employee_id'],
        'address_id': NUM_CUSTOMERS + e['employee_id'],
        'is_active': True
    })

# ── 7. ACCOUNTS ───────────────────────────────────────────
print("Generating accounts...")
accounts = []
for i in range(1, NUM_ACCOUNTS + 1):
    open_date = fake.date_time_between(start_date='-6y', end_date='-2m')
    is_active = random.random() > 0.04  # 96% active
    closed_date = None if is_active else fake.date_time_between(
        start_date=open_date, end_date=START_DATE
    )
    accounts.append({
        'account_id': i,
        'customer_id': random.randint(1, NUM_CUSTOMERS),
        'account_type': random.choice(['savings', 'checking']),
        'account_open_date': open_date,
        'account_closed_date': closed_date,
        'is_active': is_active,
        'branch_id': random.randint(1, NUM_BRANCHES)
    })

# ── 8. TRANSACTIONS + ENTRIES ─────────────────────────────
print("Generating transactions and entries (this will take a moment)...")

TRANSACTION_FILE = 'banking_data/transaction.csv'
ENTRY_FILE       = 'banking_data/transaction_entry.csv'

t_fields = ['transaction_id', 'transaction_type', 'transaction_status', 'created_at', 'created_by']
e_fields = ['entry_id', 'transaction_id', 'account_id', 'amount', 'entry_type', 'created_at']

entry_id   = 1
batch_size = 10000

with open(TRANSACTION_FILE, 'w', newline='', encoding='utf-8') as tf, \
     open(ENTRY_FILE,       'w', newline='', encoding='utf-8') as ef:

    t_writer = csv.DictWriter(tf, fieldnames=t_fields)
    e_writer = csv.DictWriter(ef, fieldnames=e_fields)
    t_writer.writeheader()
    e_writer.writeheader()

    t_buffer = []
    e_buffer = []

    for t_id in range(1, NUM_TRANSACTIONS + 1):
        t_type   = random.choice(['deposit', 'withdrawal', 'transfer'])
        t_status = random.choices(
            ['completed', 'pending', 'failed'],
            weights=[82, 10, 8]
        )[0]
        created_at = random_timestamp()
        emp_id     = random.randint(1, NUM_EMPLOYEES)
        amount     = round(random.uniform(5, 50000), 2)
        acc1       = random.randint(1, NUM_ACCOUNTS)

        t_buffer.append({
            'transaction_id':     t_id,
            'transaction_type':   t_type,
            'transaction_status': t_status,
            'created_at':         created_at,
            'created_by':         emp_id
        })

        if t_type == 'deposit':
            e_buffer.append({
                'entry_id': entry_id, 'transaction_id': t_id,
                'account_id': acc1, 'amount': amount,
                'entry_type': 'credit', 'created_at': created_at
            })
            entry_id += 1

        elif t_type == 'withdrawal':
            e_buffer.append({
                'entry_id': entry_id, 'transaction_id': t_id,
                'account_id': acc1, 'amount': amount,
                'entry_type': 'debit', 'created_at': created_at
            })
            entry_id += 1

        elif t_type == 'transfer':
            acc2 = random.randint(1, NUM_ACCOUNTS)
            while acc2 == acc1:
                acc2 = random.randint(1, NUM_ACCOUNTS)
            e_buffer.append({
                'entry_id': entry_id, 'transaction_id': t_id,
                'account_id': acc1, 'amount': amount,
                'entry_type': 'debit', 'created_at': created_at
            })
            entry_id += 1
            e_buffer.append({
                'entry_id': entry_id, 'transaction_id': t_id,
                'account_id': acc2, 'amount': amount,
                'entry_type': 'credit', 'created_at': created_at
            })
            entry_id += 1

        # Flush batch to disk
        if t_id % batch_size == 0:
            t_writer.writerows(t_buffer)
            e_writer.writerows(e_buffer)
            t_buffer.clear()
            e_buffer.clear()
            print(f"   → {t_id:,} / {NUM_TRANSACTIONS:,} transactions written...")

    # Final flush
    if t_buffer:
        t_writer.writerows(t_buffer)
        e_writer.writerows(e_buffer)

# ── WRITE REMAINING CSVs ──────────────────────────────────
def write_csv(name, rows):
    path = f'banking_data/{name}.csv'
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅  {name}.csv — {len(rows):,} rows")

write_csv('branch',           branches)
write_csv('address',          addresses)
write_csv('customer',         customers)
write_csv('customer_address', customer_address)
write_csv('employee',         employees)
write_csv('employee_address', employee_address)
write_csv('account',          accounts)

print(f"\n🏦  Generation complete.")
print(f"    Customers           : {NUM_CUSTOMERS:,}")
print(f"    Accounts            : {NUM_ACCOUNTS:,}")
print(f"    Employees           : {NUM_EMPLOYEES:,}")
print(f"    Branches            : {NUM_BRANCHES:,}")
print(f"    Transactions        : {NUM_TRANSACTIONS:,}")
print(f"    Transaction entries : {entry_id - 1:,}")
print(f"    Date range          : {START_DATE.date()} → {END_DATE.date()}")
print(f"    CSVs saved in       : ./banking_data/")