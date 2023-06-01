from database import Base
from sqlalchemy import DateTime, String, Integer, Column, Float

class Item(Base):
    __tablename__ = "moduller"
    id = Column(Integer, primary_key = True)
    name = Column(String(255), nullable = False, unique = True)
    zone = Column(String(255), nullable = False)
    enlem = Column(Float, nullable = False)
    boylam = Column(Float, nullable = False)


    def __repr__(self):
        return f"<Item name = {self.name} zone = {self.zone}>"
    

# olaylar için veritabanı yapıyorum....
class Event(Base):
    __tablename__ = "olaylar"
    id = Column(Integer, primary_key = True)
    modul_name = Column(String(255), nullable = False)
    fire_zone = Column(String(255), nullable = False)
    fire_date = Column(DateTime)
    enlem = Column(Float, nullable = False)
    boylam = Column(Float, nullable = False)

# sensor verileri icin veritabani daha sonra...