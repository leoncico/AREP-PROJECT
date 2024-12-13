import time
import urequests
from machine import Pin, Timer, ADC
import time

led_tiempo = Pin(5, Pin.OUT)  # LED de parpadeo
led_boton = Pin(12, Pin.OUT)  # LED de indicación del botón
boton = Pin(15, Pin.IN)        # Botón de entrada con resistencia pull-down
mq4_sensor = ADC(0)           # Sensor de gas MQ-4
ky026_sensor = Pin(4, Pin.IN)  # Sensor de flama KY-026

# Umbral para la detección de gas
UMBRAL_GAS = 240

def leer_sensores():
    gas_value = to_ppm(mq4_sensor.read())             # Leer valor del sensor de gas
    flama_value = ky026_sensor.value()                # Leer valor del sensor de flama

    # Verificar si hay fuego
    if flama_value == 0:
        print("!=========== ALERTA POR FUEGO ===========!")
    else:
        print("Lectura de sensor de flama KY-026: No hay fuego")

    # Verificar si el nivel de gas excede el umbral
    if gas_value >= UMBRAL_GAS:
        print("!=========== ALERTA POR ALTO NIVEL DE GAS ===========!")

    # Imprimir lecturas
    print("Lectura de sensor de gas MQ-4(ppm):", gas_value)

    enviar_datos(gas_value, flama_value)

def to_ppm(value):
    voltaje = (value / 1023) * 3.3                      # Convertir valor a voltaje
    ppm = (voltaje / 0.0048)                            # Calcular PPM (ajustar según calibración)
    return ppm

def funcion_timer(timer):
    led_tiempo.on()                                     # Encender LED
    time.sleep(1)                                       # Esperar 1 segundo
    led_tiempo.off()                                    # Apagar LED
    leer_sensores()                                     # Llamar a la función para leer los sensores

# Configuración del Timer para que se active cada 5 segundos
timer = Timer(0)
timer.init(period=5000, mode=Timer.PERIODIC, callback=funcion_timer)

# Función de interrupción que se ejecuta al presionar el botón
def manejar_boton(pin):
    led_boton.on()
    print("------------------------------")             # Encender LED al presionar el botón
    leer_sensores()                                     # Leer sensores inmediatamente
    print("------------------------------")
    time.sleep(0.5)                                     # Retardo para visualizar el LED encendido
    led_boton.off()                                     # Apagar LED después del retardo

# Configurar la interrupción para el botón (detección de flanco ascendente)
boton.irq(trigger=Pin.IRQ_RISING, handler=manejar_boton)

def enviar_datos(gas_value, flama_value):
    try:
        response = urequests.post(f"https://5iz4y69iek.execute-api.us-east-2.amazonaws.com/staging/api/v1/data?gas_value={gas_value}&flama_value={flama_value}")
        print("Respuesta del servidor:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos:", e)

# Bucle principal vacío, el programa funciona con timer e interrupciones
while True:
    pass