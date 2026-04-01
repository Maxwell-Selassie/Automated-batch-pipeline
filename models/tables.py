from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import (Column, Integer, String, Boolean,
                        DECIMAL, DateTime, ForeignKey, CheckConstraint, Text)


class Base(DeclarativeBase):
    pass


class Branch(Base):
    __tablename__ = 'branch'

    branch_id   = Column(Integer, primary_key=True)
    branch_name = Column(Text, nullable=False)
    city        = Column(Text, nullable=False)


class Address(Base):
    __tablename__ = 'address'

    address_id      = Column(Integer, primary_key=True)
    street_name     = Column(Text)
    city_name       = Column(Text)
    region          = Column(Text)
    digital_address = Column(Text)


class Customer(Base):
    __tablename__ = 'customer'

    customer_id   = Column(Integer, primary_key=True)
    first_name    = Column(Text, nullable=False)
    last_name     = Column(Text, nullable=False)
    email         = Column(Text, unique=True, nullable=False)
    primary_phone = Column(Text)
    created_at    = Column(DateTime)


class CustomerAddress(Base):
    __tablename__ = 'customer_address'

    customer_id = Column(Integer, ForeignKey('customer.customer_id'), primary_key=True)
    address_id  = Column(Integer, ForeignKey('address.address_id'),  primary_key=True)
    is_active   = Column(Boolean, default=True)


class Employee(Base):
    __tablename__ = 'employee'

    employee_id   = Column(Integer, primary_key=True)
    first_name    = Column(Text)
    last_name     = Column(Text)
    email         = Column(Text, unique=True)
    primary_phone = Column(Text)
    branch_id     = Column(Integer, ForeignKey('branch.branch_id'))


class EmployeeAddress(Base):
    __tablename__ = 'employee_address'

    employee_id = Column(Integer, ForeignKey('employee.employee_id'), primary_key=True)
    address_id  = Column(Integer, ForeignKey('address.address_id'),  primary_key=True)
    is_active   = Column(Boolean, default=True)


class Account(Base):
    __tablename__ = 'account'

    account_id        = Column(Integer, primary_key=True)
    customer_id       = Column(Integer, ForeignKey('customer.customer_id'))
    account_type      = Column(Text, CheckConstraint("account_type IN ('savings', 'checking')"))
    account_open_date = Column(DateTime)
    account_closed_date = Column(DateTime)
    is_active         = Column(Boolean, default=True)
    branch_id         = Column(Integer, ForeignKey('branch.branch_id'))


class Transaction(Base):
    __tablename__ = 'transaction'

    transaction_id     = Column(Integer, primary_key=True)
    transaction_type   = Column(String(20), CheckConstraint("transaction_type IN ('deposit', 'withdrawal', 'transfer')"), nullable=False)
    transaction_status = Column(String(20), CheckConstraint("transaction_status IN ('completed', 'pending', 'failed')"), nullable=False)
    created_at         = Column(DateTime, nullable=False)
    created_by         = Column(Integer, ForeignKey('employee.employee_id'), nullable=False)


class TransactionEntry(Base):
    __tablename__ = 'transaction_entry'

    entry_id       = Column(Integer, primary_key=True)
    transaction_id = Column(Integer, ForeignKey('transaction.transaction_id'), nullable=False)
    account_id     = Column(Integer, ForeignKey('account.account_id'), nullable=False)
    amount         = Column(DECIMAL(15, 2), nullable=False)
    entry_type     = Column(String(10), CheckConstraint("entry_type IN ('debit', 'credit')"), nullable=False)
    created_at     = Column(DateTime, nullable=False)