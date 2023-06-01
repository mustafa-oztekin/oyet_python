from database import Base, engine
from models_oyet import Item, Event

print("creating database ...")

Base.metadata.create_all(engine)