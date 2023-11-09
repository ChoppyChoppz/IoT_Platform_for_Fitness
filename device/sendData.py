"""
        Device Connector for IoT platform Fitness.

"""

import random
import json
from MyMQTT import *
import time
from pathlib import Path
from WebClient import WebClient

# Global variables
P = Path(__file__).parent.absolute()
json_wave = P / 'info_wave_device.json'
json_core = P / 'info_core_device.json'
json_pulse = P / 'info_pulse_device.json'
json_gluco = P / 'info_gluco_device.json'


class Sensor():
    def __init__(self,peso,altezza):
        self.weight=float(peso)
        self.height=float(altezza)
    
    def wave(self,filename):
        jsonopen = json.load(open(filename))
        a = jsonopen['resources'][0]
        b = jsonopen['resources'][1]
        c = jsonopen['resources'][2]
        d = jsonopen['resources'][3]
        
        # 1) DURATION_demo
        duration = round(30 + (random.random()*90),0)
        a["v"] = int(duration)
        a["t"] = int(time.time())
            
        # 2) DISTANCE_demo
        velocity = random.randint(5,15)*0.01667 #speed in km/min
        km_i = velocity*duration
        if km_i > 12:
            km_i = 12
            velocity = km_i/duration
            
        b["v"] = round(km_i,2)
        b["t"] = int(time.time())

        # 3) STEP_demo
        step_length = 0.8+(random.random()*0.5)
        if km_i == 12:
            step_length = 1.2
        
        number_of_step = int(km_i*1000/step_length)
        c["v"] = number_of_step
        c["t"] = int(time.time())

        # 4) BURNED_CALORIES_demo
        if velocity < 8:
            factor_calories = 0.5
        else:
            factor_calories = 0.8
        
        burned_calories = self.weight * factor_calories *km_i
        d["v"] = int(burned_calories)
        d["t"] = int(time.time())

        lista_wave={}
        lista_wave['bn']="wave"
        lista_wave['e']=[]
        lista_wave['e'].append(a)
        lista_wave['e'].append(b)
        lista_wave['e'].append(c)
        lista_wave['e'].append(d)

        return lista_wave
    
    def core(self,filename):
        jsonopen = json.load(open(filename))
        a = jsonopen['resources'][0]
        b = jsonopen['resources'][1]
        c = jsonopen['resources'][2]
        
        # 1) weight_demo
        a["v"] = round(self.weight + (random.uniform(-1,1)*2),2)
        a["t"] = int(time.time())
            
        # 2) BMI_demo
        BMI = a["v"]/(self.height*self.height)
        b["v"] = round(BMI,2)
        b["t"] = int(time.time())

        # 3) WATER_MASS_demo
        water_mass = a["v"]*(0.55+(random.random()*0.10))
        c["v"] = round(water_mass,2)
        c["t"] = int(time.time())

        lista_core={}
        lista_core['bn']="core"
        lista_core['e']=[]
        lista_core['e'].append(a)
        lista_core['e'].append(b)
        lista_core['e'].append(c)

        return lista_core
    
    def pulse(self,filename):
        jsonopen = json.load(open(filename))
        # Oxygenation
        a = jsonopen['resources'][0]
        a["v"] = random.randint(70,100)
        a["t"] = int(time.time())

        # Frequency
        b = jsonopen['resources'][1]
        b["v"] = random.randint(30,220)
        b["t"] = int(time.time())

        lista_pulse={}
        lista_pulse['bn']="pulse"
        lista_pulse['e']=[]
        lista_pulse['e'].append(a)
        lista_pulse['e'].append(b)
        return lista_pulse
    
    def gluco(self,filename):
        jsonopen = json.load(open(filename))

        # Glucose
        c = jsonopen['resources'][0]
        c["v"] = random.randint(30,300)
        c["t"] = int(time.time())
        lista_gluco={}
        lista_gluco['bn']="gluco"
        lista_gluco['e']=[]
        lista_gluco['e'].append(c)

        return lista_gluco


class SendData():
    def __init__(self,basetopic,info_pz,broker,port):
        self.topic=basetopic
        self.info = info_pz
        self.topic='/'.join([self.topic,self.info]) #create the topic by merging the basetopic with the id of the patient whose data I want to send. Example: IoT_project/p_1001
        print('Il topic è: ', self.topic)
        self.client=MyMQTT(self.info,broker,port,None)
    
    def send(self,message):
        self.client.myPublish(self.topic,message)
    
    def start (self):
        self.client.start()

    def stop (self):
        self.client.stop()


class SearchPatient():
    def __init__(self,name):
        self.name=name

    def id_patient(self,lista_pazienti):
        lista_nomi=list(lista_pazienti.values())
        lista_id=list(lista_pazienti.keys())
        for i in range(len(lista_nomi)):
            if self.name==lista_nomi[i]:
                return lista_id[i]
        
        return 'Not present'
    
    def TS_delete(self,lista):
        for x in lista:
            if x["name"]==self.name:
                return x

        return print('Patient not found.')



# Main
def main():
    WB=WebClient()

    #information for data submission
    conf=json.loads(json.dumps(WB.get_broker()))
    bT = conf["baseTopic"]
    broker=conf["IP"]
    port=conf["mqtt_port"]

    #Patient data search
    name_patient=input("Inserisci il nome del paziente di interesse: ")
    lista_pazienti=json.loads(json.dumps(WB.get_patients()))
    cerca = SearchPatient(str(name_patient))

    #patient id recovery
    id_patient= cerca.id_patient(lista_pazienti)

    #retrieval of patient's devices information
    lista_device= json.loads(json.dumps(WB.get_devices(str(id_patient))))
    name_device=list(lista_device.values())

    #object for sending data
    invio_dati=SendData(bT,str(id_patient),broker,port)

    #send data
    invio_dati.start()
    l=1
    while True:
        if 'wave' in name_device and l%60==0: 
            #patient information retrieval
            info_patient=json.loads(json.dumps(WB.get_info_patient(str(id_patient))))
            peso=info_patient["weight"]
            altezza=info_patient["height"]
            
            #object sensors
            sensore=Sensor(peso,altezza)

            invio_dati.send(sensore.wave(json_wave))
            invio_dati.stop()
            invio_dati.start()

            #Patient device control
            lista_device= json.loads(json.dumps(WB.get_devices(str(id_patient))))
            name_device=list(lista_device.values())

            time.sleep(10)

        if 'core' in name_device and l%15==0:
            #patient information retrieval
            info_patient=json.loads(json.dumps(WB.get_info_patient(str(id_patient))))
            peso=info_patient["weight"]
            altezza=info_patient["height"]
            
            #object sensors
            sensore=Sensor(peso,altezza)

            invio_dati.send(sensore.core(json_core))
            invio_dati.stop()
            invio_dati.start()

            #Patient device control
            lista_device= json.loads(json.dumps(WB.get_devices(str(id_patient))))
            name_device=list(lista_device.values())

            time.sleep(10)

        if 'pulse' in name_device and l%30==0:  
            #patient information retrieval
            info_patient=json.loads(json.dumps(WB.get_info_patient(str(id_patient))))
            peso=info_patient["weight"]
            altezza=info_patient["height"]
            
            #object sensors
            sensore=Sensor(peso,altezza)

            invio_dati.send(sensore.pulse(json_pulse))
            invio_dati.stop()
            invio_dati.start()

            #Patient device control
            lista_device= json.loads(json.dumps(WB.get_devices(str(id_patient))))
            name_device=list(lista_device.values())

            time.sleep(10)

        if 'gluco' in name_device and l%45==0: 
            #patient information retrieval
            info_patient=json.loads(json.dumps(WB.get_info_patient(str(id_patient))))
            peso=info_patient["weight"]
            altezza=info_patient["height"]
            
            #object sensors
            sensore=Sensor(peso,altezza)

            invio_dati.send(sensore.gluco(json_gluco))
            invio_dati.stop()
            invio_dati.start()

            #Patient device control
            lista_device= json.loads(json.dumps(WB.get_devices(str(id_patient))))
            name_device=list(lista_device.values())

            time.sleep(10)

        l=l+1
        time.sleep(1)

    
    return


if __name__ == '__main__':
    main()