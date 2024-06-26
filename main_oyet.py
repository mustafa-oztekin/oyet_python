# ilk önce bu python kodu çalıştırılmalı
# satır 24'te kod client'tan bağlantı bekler
# client'tan bağlantı onaylanırsa kod alt satırlara devam eder.

from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database import SessionLocal
import models_oyet
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import socket
import asyncio

# socket bağlantı için ip ve port
ip_address = socket.gethostname()
port = 5000
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((ip_address, port))
serversocket.listen(0)
print("Server is running now...")

clientsocket, address = serversocket.accept()
print(f"Connection from {address} has been established!")


app = FastAPI()

# CORS izinlerini belirtmek için middleware ekleme
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm kaynaklara erişime izin vermek için "*" kullanabilirsiniz
    allow_methods=["GET", "POST"],  # Sadece GET işlemine izin vermek isterseniz burada belirtebilirsiniz
    allow_headers=["*"],  # Tüm başlıklara izin vermek için "*" kullanabilirsiniz
)

class Item(BaseModel):
    id:int
    name:str
    zone:str
    enlem:float
    boylam:float

    class Config:
        orm_mode=True

class Event(BaseModel):
    id:int
    modul_name:str
    fire_zone:str
    fire_date:datetime
    enlem:float
    boylam:float

    class Config:
        orm_mode=True

db = SessionLocal()

liste = ["hello world"]
@app.get("/home")
async def get_liste():
    return liste

@app.post("/server")
async def add_liste(veriler: dict):
    liste.append(veriler)
    return {"message": "Liste güncellendi", "list": liste}


# tum modulleri dondurur
@app.get("/items", response_model=List[Item], status_code=200)
async def get_all_items():
    items = db.query(models_oyet.Item).all()
    return items

# tum olaylari dondurur
@app.get("/events", response_model=List[Event], status_code=200)
async def get_all_events():
    events = db.query(models_oyet.Event).all()
    return events

# bir tane modul dondurur
@app.get("/items/{item_name}", response_model=Item, status_code=status.HTTP_200_OK)
async def get_an_item(item_name:str):
    item = db.query(models_oyet.Item).filter(models_oyet.Item.name == item_name).first()
    return item


# baslangic sorgulari
sorgu_event = db.query(models_oyet.Event).all()
sonuc_id = sorgu_event[-1].id
#for event_sonuc in sorgu_event:
#    pass
#sonuc_id = event_sonuc.id

#sonuc_id1 = sorgu_event[-1].id
#print(sonuc_id1)

#sorgu_event1 = db.query(models_oyet.Event).all()
#for event_sonuc1 in sorgu_event1:
#    pass
#sonuc_id1 = event_sonuc1.id
#print(sonuc_id1)


# frontend ile olan baglanti
@app.get("/sse")
async def sse_endpoint():
    async def event_generator():
        global sonuc_id
        #global sonuc_id1
        global event_sonuc1
        # await kullanabilirsin
        sorgu_event = db.query(models_oyet.Event).all()
        sonuc_id1 = sorgu_event[-1].id
        #for event_sonuc1 in sorgu_event1:
        #    pass
        #sonuc_id1 = event_sonuc1.id
        if (sonuc_id1 > sonuc_id):
            print(sonuc_id1)
            yield sorgu_event[-1].modul_name # frontent'e veri basar
            olay_zaman1 = datetime.now()
            if (olay_zaman1.minute >= olay_zaman.minute + 1):
                sonuc_id = sonuc_id1
                print("id'ler eşitlendi.")
    return EventSourceResponse(event_generator())


#yukarısı için async ve await örnek
#@app.get("/users")
#async def get_users():
#    users = await fetch_users_from_database()
#    return {"users": users}



# çemberlere tıklandığında gerçekleşen endpoint
@app.post("/tcp")
def listen_to_the_modul(data: dict):
    try:
        sayac = 0
        #veri = data.get('id')
        result = ""
        for key, value in data.items():
            sayac += 1
            result += str(value) + "|"
            if sayac == 7:
                result += "\r"
                break
        print(result)
        clientsocket.send(result.encode())


        #print(veri)
        clientsocket.settimeout(5)  # 10 saniye süreyle socket'ten veri bekliyoruz
        msg = clientsocket.recv(58)
        #msg = msg.replace(b'\r', b'')
        msg = msg.decode('utf-8')
        print(msg)
        #liste_msg = msg.split("|")
        #print(liste_msg)
        return {"success": True, "data": msg}

    except socket.timeout:
        print("Timeout Hatası")
        return {"success": False, "data": "Timeout: Veri alınamadı"}
    except Exception as e:
        print("Beklenmeyen bir hata oluştu:", str(e))
        return {"success": False, "data": "Beklenmeyen bir hata oluştu"}


# yeni bir olay kaydeder
@app.post("/events/{modul_id}", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_an_event(modul_id:str):
    global sonuc_id
    global olay_zaman
    sorgu = db.query(models_oyet.Item).filter(models_oyet.Item.name == modul_id).first()
    sorgu_event = db.query(models_oyet.Event).all()
    sonuc_id = sorgu_event[-1].id
    #for event_sonuc in sorgu_event:
    #    pass
    #sonuc_id = event_sonuc.id

    new_event = models_oyet.Event(
        modul_name = sorgu.name,
        fire_zone = sorgu.zone, 
        fire_date = datetime.now(),
        enlem = sorgu.enlem,
        boylam = sorgu.boylam
    )
    olay_zaman = datetime.now()
    db.add(new_event)
    db.commit()
    return new_event



# yeni bir modul kaydeder
@app.post("/items", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_an_item(item:Item):
    db_item = db.query(models_oyet.Item).filter(models_oyet.Item.name == item.name).first()
    if db_item is not None:
        raise HTTPException(status_code=400, detail="Item already exists")

    new_item = models_oyet.Item(
        name = item.name,
        zone = item.zone,
        enlem = item.enlem,
        boylam = item.boylam
    )

    db.add(new_item)
    db.commit()
    return new_item


@app.put("/item/{item_id}", response_model=Item, status_code=status.HTTP_200_OK)
async def update_an_item(item_id:int, item:Item):
    item_to_update = db.query(models_oyet.Item).filter(models_oyet.Item.id == item_id).first()
    item_to_update.name = item.name
    item_to_update.zone = item.zone
    item_to_update.enlem = item.enlem
    item_to_update.boylam = item.boylam

    db.commit()
    return item_to_update


@app.delete("/item/{item_id}")
async def delete_an_item(item_id:int):
    item_to_delete = db.query(models_oyet.Item).filter(models_oyet.Item.id == item_id).first()

    if item_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    db.delete(item_to_delete)
    db.commit()
    return item_to_delete


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host = "0.0.0.0", port = 8000)