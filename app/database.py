from sqlalchemy import (create_engine, String, Column,
                        Integer, Text, JSON, Float, BigInteger, TIMESTAMP)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = (f"postgresql://{os.getenv('POSTGRES_USER')}:"
                f"{os.getenv('POSTGRES_PASSWORD')}@postgres:{int(os.getenv('POSTGRES_PORT'))}"
                f"/{os.getenv('POSTGRES_DATABASE_NAME')}")

Base = declarative_base()


class SKU(Base):
    __tablename__ = 'sku'

    uuid = Column(String, primary_key=True)
    marketplace_id = Column(Integer)
    product_id = Column(BigInteger, unique=True)
    title = Column(Text)
    description = Column(Text)
    brand = Column(Text)
    seller_id = Column(Integer)
    seller_name = Column(Text)
    first_image_url = Column(Text)
    category_id = Column(Integer)
    category_lvl_1 = Column(Text)
    category_lvl_2 = Column(Text)
    category_lvl_3 = Column(Text)
    category_remaining = Column(Text)
    features = Column(JSON)
    rating_count = Column(Integer)
    rating_value = Column(Float)
    price_before_discounts = Column(Float)
    discount = Column(Float)
    price_after_discounts = Column(Float)
    bonuses = Column(Integer)
    sales = Column(Integer)
    inserted_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    currency = Column(Text)
    barcode = Column(Text)
    similar_sku = Column(Text)


engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def create_tables():
    Base.metadata.create_all(engine)
