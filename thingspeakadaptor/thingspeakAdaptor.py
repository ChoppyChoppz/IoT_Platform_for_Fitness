"""
    Thingspeak Adaptor for IoT platform Fitness.

"""

import json
import time
import requests
from WebClient import WebClient
from MyMQTT import *
import random
import os


class DataCollector_TS():
    def __init__(self,clientID,broker,port,baseTopic,current_dir):
        self.clientID=clientID
        self.baseTopic=baseTopic
        self.Topic=baseTopic
        self.current_dir=current_dir
        self.client=MyMQTT(clientID,broker,port,self)

    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
        
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))

    def follow(self,topic):
        self.client.mySubscribe(topic)
        
    def notify(self,topic,msg):
        payload=json.loads(msg)
        #print(json.dumps(payload,indent=4))
        id_patient=topic.split('/')[-1] #get via topic the id patient
        if id_patient != 'noderedtry':
            #object to manage channels 
            TS=TS_folder(self.current_dir)
            #check/modify patient channels
            payload_TS,path = TS.new(id_patient)

            #object to send data to ThingSpeak
            sendTS = SendThingSpeak(id_patient,payload_TS)
            #send data
            sendTS.SendData(path,id_patient,payload)


class channel_delete():
    def __init__(self,payload):
        self.payload=payload

    def delete(self,id_channel): #delete a channel on ThingSpeak
        payload_delete={}
        payload_delete["api_key"]=self.payload["api_key"]
        d=requests.delete(self.payload["url_delete_channel"]+str(id_channel),data=payload_delete)
        print('Channel successfully deleted')


class SendThingSpeak():
    def __init__(self,id,payload):
        self.id_pz=id
        self.payload=payload
    
    def post(self,api_key,value):
        payload_prov={}
        payload_prov["api_key"]=api_key
        for i in range(len(value)):
            campo='field'+str(i+1)
            payload_prov[str(campo)]=value[i]["v"]

        r=requests.post(self.payload["URL"],data=payload_prov)
        print(r.text)

        return r
    
    def SendData(self,path,id_patient,dati_pz):  #send data to ThingSpeak
        json_channelpz_file=json.load(open(path))
        canali_pz = json_channelpz_file[str(id_patient)]
        for k in range(len(canali_pz)):
            if dati_pz['bn'] in canali_pz[k]["name"]:
                r=self.post(canali_pz[k]["api_keys"][0]["api_key"],dati_pz['e'])
                if '400' in str(r): #check for errors
                    print("Error in data submission")
                else:
                    print('Successful data submission')

    def delete(self,id_channel):  #delete data on ThingSpeak
        payload_delete={}
        payload_delete["api_key"]=self.payload["User api"] 
        d=requests.delete(self.payload["url_clear_channel"]+str(id_channel)+'/feeds.json',data=payload_delete)
        print(d.text)
        if json.loads(d.text) == []:
            print('Data successfully deleted')


class channel():
    def __init__(self,id,payload):
        self.id_pz=id
        self.payload=payload

    def post(self,nome_canale,campi_device): #add a new channel on ThingSpeak
        payload_prov={}
        payload_prov["api_key"]=self.payload["api_key"]
        payload_prov['name']=str(nome_canale + '_' + self.id_pz)
        for i in range(len(campi_device)):
            campo='field'+str(i+1)
            payload_prov[str(campo)]=str(campi_device[i]["n"]+' ('+ campi_device[i]["u"] + ") ")

        #channel creation
        r=requests.post(self.payload["url_new_channel"],data=payload_prov)

        return r
    
    def delete(self,id_channel): #delete a channel on ThingSpeak
        payload_delete={}
        payload_delete["api_key"]=self.payload["api_key"] 
        d=requests.delete(self.payload["url_delete_channel"]+str(id_channel),data=payload_delete)
        print('Channel successfully deleted')


def jsonupload(filename_originale,file_modificato):
    with open((filename_originale),'w') as filemod:
        json.dump(file_modificato,filemod)


class TS_folder():
    def __init__(self,current_dir):
        self.WB=WebClient()
        self.current_dir = current_dir

    def new(self,id_patient):
        #retrieval patient's devices
        lista_device= json.loads(json.dumps(self.WB.get_devices(str(id_patient))))
        name_device=list(lista_device.values())
        #retrieval of patient's devices information
        lista_info_device= json.loads(json.dumps(self.WB.get_info_devices(str(id_patient))))

        #loading basic payload
        payload=json.loads(json.dumps(self.WB.get_ts()))
        #retrieve information about user api for TS
        info_patient=json.loads(json.dumps(self.WB.get_info_patient(str(id_patient))))
        payload["User api"]=info_patient["keyTS"]
        payload["api_key"]=info_patient["keyTS"]

        #Data folder
        if not os.path.exists(os.path.join(self.current_dir,'TS',str(id_patient))):
            os.makedirs(os.path.join(self.current_dir,'TS',str(id_patient)))
        #change folder of work
        os.chdir(self.current_dir +'/TS/'+str(id_patient))

        #object channel
        canale=channel(id_patient,payload)
        if not os.path.exists(os.path.join(os.getcwd() ,'Dati_canali_'+str(id_patient)+'.json')):  #check if the patient has no channels
            json_channel_file={}
            json_channel_file[str(id_patient)]=[]
            for i in range(len(lista_info_device)):  #a channel is created for each device
                parametri_canale=canale.post(lista_info_device[i]["name"],lista_info_device[i]["resources"])
                print("New channel "+lista_info_device[i]["name"]+" successfully created.")
                json_single_channel=json.loads(parametri_canale.text)
                json_channel_file[str(id_patient)].append(json_single_channel)

                #send channel information to catalog
                self.WB.post_TS_channel(str(id_patient),json_single_channel)

                time.sleep(3)

            #Saving channel data
            jsonupload('Dati_canali_'+str(id_patient)+'.json',json_channel_file)

        else: #in case the patient already has channels
            json_channelpz_file=json.load(open('Dati_canali_'+str(id_patient)+'.json'))
            canali_pz = json_channelpz_file[str(id_patient)]
            
            #delete the channels of the removed devices
            t=0
            for i in range(len(canali_pz)):
                presenza_canale=0 #flag
                for j in range(len(name_device)):
                    if name_device[j] in canali_pz[i-t]["name"]:
                        presenza_canale=1 #flag
                    
                if presenza_canale==0:
                    #delete the channel
                    canale.delete(canali_pz[i-t]["id"]) #need id of the channel to be deleted.
                    print("The channel "+ canali_pz[i-t]["name"] +" has been deleted.")
                    del json_channelpz_file[str(id_patient)][i-t]
                    t=t+1


            #Saving channel data
            jsonupload('Dati_canali_'+str(id_patient)+'.json',json_channelpz_file)

                        
            json_channelpz_file=json.load(open('Dati_canali_'+str(id_patient)+'.json'))
            canali_pz = json_channelpz_file[str(id_patient)]

            #create the channels for new devices
            for i in range(len(name_device)):
                presenza_device=0  #flag
                for j in range(len(canali_pz)):
                    if name_device[i] in canali_pz[j]["name"]:
                        presenza_device=1  #flag
                
                if presenza_device==0:
                    #create the channel
                    parametri_canale=canale.post(lista_info_device[i]["name"],lista_info_device[i]["resources"])
                    print("New channel "+lista_info_device[i]["name"]+" successfully created.")
                    json_single_channel=json.loads(parametri_canale.text)
                    json_channelpz_file[str(id_patient)].append(json_single_channel)

                    #send channel information to catalog
                    self.WB.post_TS_channel(str(id_patient),json_single_channel)
            
            #Saving channel data
            jsonupload('Dati_canali_'+str(id_patient)+'.json',json_channelpz_file)


        json_channelpz_file=json.load(open('Dati_canali_'+str(id_patient)+'.json'))
        canali_pz = json_channelpz_file[str(id_patient)]

        #path of channel data
        path='Dati_canali_'+str(id_patient)+'.json'

        return payload, path
    

    def delete(self):
        lista_TS_delete=json.loads(json.dumps(self.WB.get_patients_TS()))

        for TS_info in lista_TS_delete:
            #change folder of work
            os.chdir(self.current_dir +'/TS/'+str(TS_info["patientID"]))
            #loading the patient's channels
            json_channel_file=json.load(open('Dati_canali_'+str(TS_info["patientID"])+'.json'))

            #loading basic payload
            payload=json.loads(json.dumps(self.WB.get_ts()))
            payload["api_key"]=TS_info["keyTS"]

            #object to delete channels
            CD = channel_delete(payload)

            #channels deletion
            canali_pz = json_channel_file[str(TS_info["patientID"])]
            for i in range(len(canali_pz)):
                CD.delete(canali_pz[i]["id"]) #need id of the channel to be deleted.
                print("The channel "+ canali_pz[i]["name"] +" has been deleted.")
            json_channel_file[str(TS_info["patientID"])]=[]

            #Saving channel data
            with open('Dati_canali_'+str(TS_info["patientID"])+'.json', "w") as outfile:
                json.dump(json_channel_file, outfile)

            #update the catalog
            self.WB.delete_TS(TS_info["patientID"])

        return 
   


#Main
def main():
    WB=WebClient()

    #information for data exchange
    conf=json.loads(json.dumps(WB.get_broker()))
    bT = conf["baseTopic"]
    broker=conf["IP"]
    port=conf["mqtt_port"]

    #current direction
    current_dir = os.getcwd() 

    #object to manage channels 
    TS=TS_folder(current_dir)

    #object to receive data
    coll=DataCollector_TS('dc'+str(random.randint(1,10**5)),broker,port,bT,current_dir)
    coll.run()

    print(f'This is the client to follow the data coming from the sensors of {coll.baseTopic}')
    coll.client.unsubscribe()
    coll.follow(coll.baseTopic+'/+')

    while True:
        # Delete channles of a patient who has been removed from the service.
        TS.delete()
        time.sleep(60) #check every minute for patients removed
    
    return



if __name__ == '__main__':
    main()