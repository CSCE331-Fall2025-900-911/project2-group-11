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
    
    print("Tables created")

def fill_baseInfo(url: str):
    """Insert initial data into the database."""
    engine = create_engine(url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # --- Employees ---
        employees = [
            Employee(employee_id=1, name="Andre Athari", role="Cashier"),
            Employee(employee_id=2, name="Raafay Hemani", role="Cashier"),
            Employee(employee_id=3, name="Liam Alme", role="Manager"),
            Employee(employee_id=4, name="Matthew Jones", role="Cashier"),
            Employee(employee_id=5, name="Sam Maharjan", role="Cashier"),
        ]
        session.add_all(employees)

        # --- Products ---
        products = [
            Product(product_id=1,  product_name="mango milk tea",          unit_price=5.80),
            Product(product_id=2,  product_name="watermelon milk tea",     unit_price=6.00),
            Product(product_id=3,  product_name="coconut milk tea",        unit_price=6.50),
            Product(product_id=4,  product_name="peach milk tea",          unit_price=6.25),
            Product(product_id=5,  product_name="passion-fruit milk tea",  unit_price=6.25),
            Product(product_id=6,  product_name="lychee milk tea",         unit_price=6.25),
            Product(product_id=7,  product_name="pineapple milk tea",      unit_price=6.50),
            Product(product_id=8,  product_name="honey milk tea",          unit_price=6.75),
            Product(product_id=9,  product_name="dragon-fruit milk tea",   unit_price=4.65),
            Product(product_id=10, product_name="pomegranate milk tea",    unit_price=4.85),
            Product(product_id=11, product_name="mango green tea",         unit_price=5.80),
            Product(product_id=12, product_name="watermelon green tea",    unit_price=6.25),
            Product(product_id=13, product_name="coconut green tea",       unit_price=6.25),
            Product(product_id=14, product_name="peach green tea",         unit_price=6.25),
            Product(product_id=15, product_name="passion-fruit green tea", unit_price=5.20),
            Product(product_id=16, product_name="lychee green tea",        unit_price=6.50),
            Product(product_id=17, product_name="pineapple green tea",     unit_price=5.80),
            Product(product_id=18, product_name="honey green tea",         unit_price=6.25),
            Product(product_id=19, product_name="dragon-fruit green tea",  unit_price=6.50),
            Product(product_id=20, product_name="pomegranate green tea",   unit_price=6.25),
        ]
        session.add_all(products)

        # --- Inventory ---
        inventory = [
            Inventory(ingredient_id=1,  ingredient_name="mango",         on_hand_quantity=0),
            Inventory(ingredient_id=2,  ingredient_name="watermelon",    on_hand_quantity=12),
            Inventory(ingredient_id=3,  ingredient_name="coconut",       on_hand_quantity=8),
            Inventory(ingredient_id=4,  ingredient_name="peach",         on_hand_quantity=4),
            Inventory(ingredient_id=5,  ingredient_name="passion-fruit", on_hand_quantity=5),
            Inventory(ingredient_id=6,  ingredient_name="lychee",        on_hand_quantity=9),
            Inventory(ingredient_id=7,  ingredient_name="pineapple",     on_hand_quantity=2),
            Inventory(ingredient_id=8,  ingredient_name="honey",         on_hand_quantity=4),
            Inventory(ingredient_id=9,  ingredient_name="dragon-fruit",  on_hand_quantity=11),
            Inventory(ingredient_id=10, ingredient_name="pomegranate",   on_hand_quantity=3),
            Inventory(ingredient_id=11, ingredient_name="milk tea",      on_hand_quantity=15),
            Inventory(ingredient_id=12, ingredient_name="green tea",     on_hand_quantity=20),
        ]
        session.add_all(inventory)

        session.commit()
        print("Base information inserted successfully.")

    except Exception as e:
        session.rollback()
        print("Error inserting base info:", e)
    finally:
        session.close()

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
        fill_baseInfo(db_url)


if __name__ == '__main__':
    main()
