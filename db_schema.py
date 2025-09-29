import os
import argparse
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Numeric,
    ForeignKey,
    PrimaryKeyConstraint,
    Enum as SAEnum,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


# Enums (use native PostgreSQL enums)
EmployeeRole = SAEnum('Cashier', 'Manager', name='employee_role', native_enum=True)
ModificationType = SAEnum('ADD', 'REMOVE', 'LESS', 'EXTRA', name='modification_type', native_enum=True)


class Employee(Base):
    __tablename__ = 'employees'

    employee_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    # "role" is a common identifier in SQL (Postgres has ROLE in role management),
    # but it's fine as a column name; SQLAlchemy will quote as needed for dialects.
    role = Column('role', EmployeeRole, nullable=False)

    orders = relationship('Order', back_populates='employee')


class Order(Base):
    __tablename__ = 'orders'

    order_id = Column(Integer, primary_key=True)
    order_date = Column(DateTime, nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    employee_id = Column(Integer, ForeignKey('employees.employee_id'), nullable=False)

    employee = relationship('Employee', back_populates='orders')
    items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    recipe = relationship('ProductRecipe', back_populates='product')
    order_items = relationship('OrderItem', back_populates='product')


class Inventory(Base):
    __tablename__ = 'inventory'

    ingredient_id = Column(Integer, primary_key=True)
    ingredient_name = Column(String, nullable=False)
    on_hand_quantity = Column(Numeric(10, 1), nullable=False)

    recipe_entries = relationship('ProductRecipe', back_populates='ingredient')
    modifications = relationship('Modification', back_populates='ingredient')


class ProductRecipe(Base):
    __tablename__ = 'product_recipe'

    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('inventory.ingredient_id'), nullable=False)
    quantity_per_unit = Column(Numeric(10, 1), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('product_id', 'ingredient_id', name='pk_product_recipe'),
    )

    product = relationship('Product', back_populates='recipe')
    ingredient = relationship('Inventory', back_populates='recipe_entries')


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price_at_sale = Column(Numeric(10, 2), nullable=False)

    order = relationship('Order', back_populates='items')
    product = relationship('Product', back_populates='order_items')
    modifications = relationship('Modification', back_populates='order_item', cascade='all, delete-orphan')


class Modification(Base):
    __tablename__ = 'modifications'

    modification_id = Column(Integer, primary_key=True)
    order_item_id = Column(Integer, ForeignKey('order_items.order_item_id'), nullable=False)
    ingredient_id = Column(Integer, ForeignKey('inventory.ingredient_id'), nullable=False)
    modification_type = Column(ModificationType, nullable=False)
    quantity_change = Column(Numeric(10, 1), nullable=True)
    price_change = Column(Numeric(10, 2), nullable=True)

    order_item = relationship('OrderItem', back_populates='modifications')
    ingredient = relationship('Inventory', back_populates='modifications')


def create_db(url: str):
    """Create database schema at the provided SQLAlchemy URL."""
    # echo=True prints the generated SQL statements; set to False to silence
    engine = create_engine(url, echo=True)

    print("Creating all tables on:", engine.url)
    Base.metadata.create_all(engine)
    print("Done.")


def parse_args():
    p = argparse.ArgumentParser(description='Create Postgres schema for project')
    p.add_argument('--url', help='SQLAlchemy database URL (overrides DATABASE_URL env)')
    p.add_argument('--create', action='store_true', help='Create tables')
    p.add_argument('--drop', action='store_true', help='Drop tables before create (USE WITH CAUTION)')
    return p.parse_args()


def main():
    args = parse_args()
    # load .env if present, so DATABASE_URL can be stored there
    load_dotenv()
    db_url = args.url or os.environ.get('DATABASE_URL')
    if not db_url:
        print('ERROR: no database URL provided. Set DATABASE_URL or pass --url')
        return

    engine = create_engine(db_url, echo=False)
    if args.drop:
        confirm = input('Drop all tables? This is destructive. Type DROP to continue: ')
        if confirm == 'DROP':
            Base.metadata.drop_all(engine)
            print('Dropped all tables.')
        else:
            print('Aborted drop.')

    if args.create:
        create_db(db_url)


if __name__ == '__main__':
    main()
