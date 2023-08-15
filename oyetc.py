import socket
import serial
import requests
#import pickle
import time

post_counter = 0
max_post_count = 1  # İstenilen post işleminin maksimum kaç kez yapılacağını belirleyin
last_post_time = 0  # Zaman damgasını saklamak için bir değişken

modul = ""

arduino = serial.Serial(port='COM26', baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=0)

#headersize = 10

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((socket.gethostname(), 5000))
s.setblocking(False) # bu sayede s.recv() kod bloğunun beklemesini önledim.

url = "http://127.0.0.1:8000"

while True:
    # burası c modülünün arduinosunda gelen doğrudan yangın verisi için A1'de yangın var gibi.
    if arduino.in_waiting:
        arduino_veri = arduino.readline()
        cleaned_data = arduino_veri.replace(b'\r\n', b'')
        cleaned_data = cleaned_data.decode('utf')
        words = cleaned_data.split('<>')
        print(words)


        if (len(words) == 2 and len(words[0]) == 3):
            s.send(words[1].encode())
            
        elif (len(words) == 2 and len(words[0]) == 2):
            # Zaman değeri güncelleme
            current_time = time.time()

            # Belirli bir süre (örn. 2 dakika) içerisinde aynı veri gelmemişse post işlemini yapar
            if (current_time - last_post_time > 180 or words[0] != modul):
            #    if post_counter < max_post_count:  # Sayaç değeri belirtilen maksimum sayıya ulaşmadan post işlemi yapar
            #    if (words[0] != ""): # boş gelen veri durumunda post yapmasın
                response = requests.post(url + "/events/" + words[0])
                print("İstek durumu:", response.status_code)
                #    post_counter += 1  # Sayaç değerini artır
                modul = words[0]

                # Zaman damgasını günceller
                last_post_time = current_time
            #else: sadece süreyle kontrol etmek için burayı kapatmayı deniyorum
                # Zaman süresi içerisinde aynı veri gelmişse, post işlemi yapılmaz ve sayaç sıfırlanır
            #   post_counter = 0
            
    try:
        msg = s.recv(3)
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