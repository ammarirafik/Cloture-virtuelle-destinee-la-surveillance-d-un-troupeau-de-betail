import time
import random
import threading
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db
import json
import math

# Configuration MQTT
broker = "test.mosquitto.org"
port = 1883
topic = "lorasim/vaches"

# Initialiser Firebase Admin SDK
cred = credentials.Certificate('C:/Users/ASUS/Desktop/firebase/mouton-67334-firebase-adminsdk-tinvp-261814ffc1.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://mouton-67334-default-rtdb.firebaseio.com/'
})

# Positions des passerelles (en mètres, par exemple)
gateways = {
    "gateway_1": (0, 0),
    "gateway_2": (100, 0),
    "gateway_3": (50, 100)
}

# Fonction de simulation des moutons
def simulate_mouton(mouton_id):
    client = mqtt.Client()
    client.connect(broker, port, 60)
    while True:
        # Simuler les données de signal pour chaque passerelle
        for gateway_id in gateways.keys():
            rssi = random.randint(-120, -40)
            data = {
                "mouton_id": mouton_id,
                "gateway_id": gateway_id,
                "rssi": rssi,
                "timestamp": time.time()
            }
            client.publish(topic, json.dumps(data))
            time.sleep(random.randint(1, 5))

# Fonction de calcul de la distance basée sur le RSSI
def rssi_to_distance(rssi):
    # Modèle simple pour convertir RSSI en distance (en mètres)
    tx_power = -59  # Puissance d'émission (dBm)
    if rssi == 0:
        return -1.0  # Valeur invalide
    ratio = rssi / tx_power
    if ratio < 1.0:
        return pow(ratio, 10)
    else:
        return (0.89976 * pow(ratio, 7.7095)) + 0.111

# Fonction de trilatération pour estimer la position
def trilateration(distances):
    (x1, y1), (x2, y2), (x3, y3) = gateways.values()
    r1, r2, r3 = distances

    A = 2 * x2 - 2 * x1
    B = 2 * y2 - 2 * y1
    C = r1 ** 2 - r2 ** 2 - x1 ** 2 + x2 ** 2 - y1 ** 2 + y2 ** 2
    D = 2 * x3 - 2 * x2
    E = 2 * y3 - 2 * y2
    F = r2 ** 2 - r3 ** 2 - x2 ** 2 + x3 ** 2 - y2 ** 2 + y3 ** 2

    x = (C * E - F * B) / (E * A - B * D)
    y = (C * D - A * F) / (B * D - A * E)

    return (x, y)

# Fonction de traitement des messages MQTT (passerelle)
def on_message(client, userdata, msg):
    print(f"Message reçu: {msg.payload}")
    data = json.loads(msg.payload)

    mouton_id = data["mouton_id"]
    gateway_id = data["gateway_id"]
    rssi = data["rssi"]

    distance = rssi_to_distance(rssi)

    if mouton_id not in mouton_positions:
        mouton_positions[mouton_id] = {}

    mouton_positions[mouton_id][gateway_id] = distance

    if len(mouton_positions[mouton_id]) == 3:  # Si les trois distances sont disponibles
        distances = [mouton_positions[mouton_id][gw_id] for gw_id in gateways.keys()]
        position = trilateration(distances)
        print(f"Position estimée de le mouton {mouton_id}: {position}")

        # Envoi des données à Firebase Realtime Database
        data_to_send = {
            "mouton_id": mouton_id,
            "position": position,
            "timestamp": time.time()
        }
        ref = db.reference()  # Référence racine
        ref.child('moutons').child(str(mouton_id)).set(data_to_send)  # Utilisation de str(mouton_id)
        print("Données envoyées à Firebase Realtime Database")

# Configuration du client MQTT (passerelle)
gateway_client = mqtt.Client()
gateway_client.connect(broker, port, 60)
gateway_client.subscribe(topic)
gateway_client.on_message = on_message

# Dictionnaire pour stocker les positions des moutons
mouton_positions = {}

# Démarrage des simulations de moutons dans des threads séparés
mouton_threads = []
for mouton_id in range(1, 6):
    thread = threading.Thread(target=simulate_mouton, args=(mouton_id,))
    thread.start()
    mouton_threads.append(thread)

# Démarrage de la boucle principale du client MQTT (passerelle)
gateway_client.loop_forever()
