# See https://docs.pycom.io for more information regarding library specifics
import ujson
import pycom
from pysense import Pysense
# seule la librairie pour la température est importée pour ce modèle
from SI7006A20 import SI7006A20

# acceleromètre
from LIS2HH12 import LIS2HH12

from wifi import WiFi
from mqtt import MQTTClient
import time

IBMorgID='5rg1a4' # Identifiant de l'instance 'IoT PLatform' sur 6 caractères
deviceType='pycom' # Nom du 'Device Type' défini dans le IoT Platform
deviceID='1181' # ID du device (4 dernieres caractères du SSID)
deviceToken='Ct-g!TpOwL86V)(a*X' # Token (mot de passe) défini pour le device dans le Iot Platform

wifiSSID="Redmi" # ID du WiFi
wifiPSW="inprogress" # Mot de Passe du WiFi

py = Pysense() # Instance de l'objet py de la class Pysense
si = SI7006A20(py) # Instance de l'objet si de la class SI7006A20 ayant pour parametre py

wifi = WiFi() # Initialisation de l'objet wifi de la class WiFi

acc = LIS2HH12() # Initialisation de l'objet acc de la class LIS2HH12 ayant pour but de récupérer les données de la carte

# print("Temperature: " + str(si.temperature())+ " deg C and Relative Humidity: " + str(si.humidity()) + " %RH")
# print("Dew point: "+ str(si.dew_point()) + " deg C")
print("Connecting wifi")

print (WiFi.connectwifi(wifiSSID,wifiPSW)) # Connection WiFi, affiche quelque chose s'il y a une erreur

# Syntaxe pour envoyer un paquet MQTT à IBM Cloud

client = MQTTClient("d:"+IBMorgID+":"+deviceType+":"+deviceID, IBMorgID +".messaging.internetofthings.ibmcloud.com", user="use-token-auth", password=deviceToken, port=8883, ssl=True)
print(client.connect())

pycom.heartbeat(False) # Permet de désactiver le clignotement de la led, permettant ainsi de choisir la couleur de la led

accjson = ujson.loads('{ "pitch": 0, "roll" : 0, "acceleration": 0 }')  # Définition de accjson

active = False # Définition de active, définis si l'alarme est active ou non
pressed = False # Définition de pressed, définit si le bouton d'activation à déjà été appuyé

hasMoved = False # Définition de hasMoved, définit si la carte a bougé

seuil = 0.1 # Définition de seuil

sendTiming = 1 # Délai entre chaque envois (en secondes)

isDateUpdated = False # Vérifie si la date de début est à jour
dateStart = 0 # Déclaration de la date de début du timer

# Envoi du status au serveur
print("Sending Has Pressed")
mqttMsg = '{'
mqttMsg = mqttMsg + '"active":' + str(active)
mqttMsg = mqttMsg + '}'
client.publish(topic="iot-2/evt/data/fmt/json", msg=mqttMsg)

# BOUCLE PRINCIPAL
while True:

    # Si on appuye sur le bouton
    if py.button_pressed() and not pressed:
        pressed = True
        # L'alarme s'active / se désactive
        active = not active

        # Envoi du status au serveur
        print("Sending Has Pressed")
        mqttMsg = '{'
        mqttMsg = mqttMsg + '"active":' + str(active)
        mqttMsg = mqttMsg + '}'
        client.publish(topic="iot-2/evt/data/fmt/json", msg=mqttMsg)
    elif not py.button_pressed() and pressed:
        # Quand le bouton est relaché
        pressed = False
    
    # Si l'alarme est active
    if active:
        # Mise à jour de la date de début
        if not isDateUpdated:
            isDateUpdated = True
            dateStart = time.time()

        # Définition d'une couleur pour la led (ici vert)
        pycom.rgbled(0x00ff00)
        # Récupération des données de la carte (tanguage, roulis et accelération)
        accjson["pitch"] = acc.pitch()
        accjson["roll"] = acc.roll()
        accjson["acceleration"] = acc.acceleration()

        # Détection d'un mouvement
        isMoving = abs(accjson["acceleration"][0]) > seuil or abs(accjson["acceleration"][1]) > seuil

        # print("X : " + str(accjson["acceleration"][0]) + " Y : " + str(accjson["acceleration"][1]))
        
        # print("Pitch : " + str(accjson["pitch"]) + " Roll : " + str(accjson["roll"]) + " Acceleration : " + str(accjson["acceleration"]))
        # print(str(accjson["pitch"]) + ";" + str(accjson["roll"]) + ";" + str(accjson["acceleration"])

        # S'il y a déplacement
        if isMoving and not hasMoved:
            # Envoi du status au serveur
            print("Sending Has Moved")
            hasMoved = True
            mqttMsg = '{'
            mqttMsg = mqttMsg + '"isMoving": true'
            mqttMsg = mqttMsg + '}'
            client.publish(topic="iot-2/evt/data/fmt/json", msg=mqttMsg)

        # Lorsque le temps écoulé est supérieur ou égal au temps d'attente
        if (time.time() - dateStart >= sendTiming):
            print("Sending Auto")
            print("Acceleration X : " + str(accjson["acceleration"][0]) + " / Acceleration Y : " + str(accjson["acceleration"][1]) + " / Acceleration Z : " + str(accjson["acceleration"][2]))
            print("Pitch : " + str(accjson["pitch"]) + " / Roll : " + str(accjson["roll"]))
            isDateUpdated = False
            mqttMsg = '{'
            mqttMsg = mqttMsg + '"accX": ' + str(accjson["acceleration"][0]) + ', '
            mqttMsg = mqttMsg + '"accY": ' + str(accjson["acceleration"][1]) + ', '
            mqttMsg = mqttMsg + '"accZ": ' + str(accjson["acceleration"][2]) + ', '
            mqttMsg = mqttMsg + '"pitch": ' + str(accjson["pitch"]) + ', '
            mqttMsg = mqttMsg + '"roll": ' + str(accjson["roll"])
            mqttMsg = mqttMsg + '}'
            client.publish(topic="iot-2/evt/data/fmt/json", msg=mqttMsg)
    else:
        # Définition d'une couleur pour la led (ici rouge - orange)
        pycom.rgbled(0xff2001)
        # Réinitialisation de hasMoved
        hasMoved = False
        # Réinitialisation du timer
        isDateUpdated = False