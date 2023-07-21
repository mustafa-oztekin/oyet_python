import socket
import serial
import requests
#import pickle

arduino = serial.Serial(port='COM10', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

#headersize = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 1234))
s.setblocking(False) # bu sayede s.recv() kod bloğunun beklemesini önledim.

url = "http://127.0.0.1:8000"

while True:
    # burası c modülünün arduinosunda gelen doğrudan yangın verisi için A1'de yangın var gibi.
    if arduino.in_waiting:
        arduino_veri = arduino.readline()
        #print(arduino_veri)
        cleaned_data = arduino_veri.replace(b'\r\n', b'')
        #print(cleaned_data)
        cleaned_data = cleaned_data.decode('utf')
        print(cleaned_data)
        #response = requests.post(url + "/events/" + cleaned_data)
        #print("İstek durumu:", response.status_code)
    try:
        msg = s.recv(16)
        if msg:
            msg = msg.decode("utf-8")
            print("Received:", msg)
            arduino.write(msg.encode('utf-8'))
            msg = ''
            # arduino gelen veri ismindeki modüle veri basacak. A1' veri gönder ve sıcaklık çek
    except BlockingIOError:
        # Veri gelmediği durumda, BlockingIOError hatası alacaksınız
        pass
    except socket.error as e:
        # Diğer soket hatalarını yönetmek için burada da işlem yapabilirsiniz
        pass
        

"""
while True:
    full_msg = ''
    new_msg = True
    while True:
        msg = s.recv(16)
        if new_msg:
            print(f"new msg length: {msg[:headersize]}")
            msglen = int(msg[:headersize])
            new_msg = False

        full_msg += msg.decode("utf-8")
        #full_msg += msg

        if len(full_msg) - headersize == msglen:
            print("full msg received")
            print(full_msg[headersize:])
            son = full_msg[headersize:]
            new_msg = True
            full_msg = ''
            if son == "kapat":
                break
    s.close()
    break
            #data = pickle.loads(full_msg[headersize:])
            #print(data)


            #yeni_msg = f"{len(full_msg[headersize:]):<{headersize}}" + full_msg[headersize:]
            #s.send(bytes(yeni_msg, "utf-8"))
"""