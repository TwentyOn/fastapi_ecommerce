from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///ecommerce.db', echo=True)
session_local = sessionmaker(bind=engine)
