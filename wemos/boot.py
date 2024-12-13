import gc
import socket
import network

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect('_PICO_', 'caleopico')

    while not wlan.isconnected():
        machine.idle() 
        time.sleep(0.5)

    print('Conectado a WiFi')
    print('IP address:', wlan.ifconfig()[0])

def check_internet():
    try:
        addr = socket.getaddrinfo('8.8.8.8', 53)
        addr = addr[0][-1]
        s = socket.socket()
        s.connect(addr)
        print("Conexión a Internet exitosa")
        s.close()
    except Exception as e:
        print("No se pudo conectar a Internet:", e)

def init_garbage_collector():
    gc.enable()
    print("Garbage collector habilitado")
    gc.collect()  
    print("Recolección de basura inicializada")

init_garbage_collector()