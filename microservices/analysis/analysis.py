"""
    Aanalysis for IoT platform Fitness.
    
"""

from MyMQTT import *
from WebClient import *
import json
import requests
import time
import numpy as np
from pathlib import Path
import random

# Global variables
P = Path(__file__).parent.absolute()
CONFIG = P / 'conf.json'  # Config file with absolute path


class DataCollector():
    def __init__(self,clientID,broker,port,baseTopic):
        self.clientID=clientID
        self.baseTopic=baseTopic
        self.Topic=baseTopic
        self.broker=broker
        self.port=port
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
        self.weight(topic,payload) #analysis of weight data received
    
    def pub(self,id_patient, msg):
        #topic to send data via MQTT
        send_topic= 'IoT_project/telegram/analysis/'+str(id_patient)
        self.client.myPublish(send_topic,msg) #sending via MQTT to Telegram
        time.sleep(5)
    
    def weight(self,topic,payload):
        id_patient=topic.split('/')[-1]
        WC=WebClient()

        if id_patient != 'noderedtry':
            #object to send patient's weight to catalog
            AW=analysis_weight(payload,id_patient) 
            value, c=AW.value()
            if c != 0: #check if the weight data is present
                WC.post_weight(json.dumps(value)) #sending via REST to Catalog
                time.sleep(5)

    
class analysis_weight():
    def __init__(self,payload,id_patient):
        self.payload=payload
        self.ID=id_patient
    
    def value(self):
        weight={}
        weight["bn"]=''
        weight["e"]=[]
        c=0
        #Only data from one device is analyzed: core.
        if self.payload["bn"] == 'core': 
            weight["bn"]=self.payload["bn"]+'/'+str(self.ID) #basename has the device name and the patient id
            for x in self.payload["e"]:
                if x["n"]=='weight': #I only want a specific device data 
                    weight["e"].append(x)
                    c=c+1

        return weight, c


class PatientAnalysis(object):
    def __init__(self,pID):        
        self.pID = pID #patient id
        #names of the devices considered
        self.dName1 = "wave"
        self.dName2 = "core"

    def GetDataTS(self, data):
        for i in range(len(data["api_keys"])):
            if data["api_keys"][i]["write_flag"] != True:
                break
            
        id = data["ID_channel"] #channel ID
        api = data["api_keys"][i]["api_key"] #channel key for reading data
        ts_url = f"https://api.thingspeak.com/channels/{id}/feeds.json"
        params = { "api_key" : api, "results" : str(2)}
        data = json.loads(requests.get(ts_url, params=params).text) #channel data

        return data, id, api


    def Analysis(self, BMI, duration, calories):
        #Define BMI status 
        BMI_mean=np.mean(BMI[BMI != 0])
        if BMI_mean>=18.5 and BMI_mean<= 24.9:
            category = 'Normal'
        else:
            if BMI_mean<18.5:
                if BMI_mean>=16.5:
                    category='Severe underweight'
                else:
                    category= 'Underweight'
            
            else:
                if BMI_mean<=30:
                    category='Overweight'
                else:
                    category='Severe overweight'

        #create the message with all the information
        msg1 = f"In this week the average value of your body mass index was {round(BMI_mean,2)} kg/m^2.\n"
        msg2 = f"The weight class associated with your BMI is: {category}.\n"
        msg3 = f"You can increase duration of exercise in order to increase your average number of calories burned ({round(np.mean(calories[calories != 0]),2)} kCal).\n"
        msg4 = f"You can increase aerobic exercise duration. This week you have spent an average of {round(np.mean(duration[calories != 0]),2)} minutes on exercises.\n"

        msg_finale=msg1+msg2+msg3+msg4
    
        payload={}
        payload["bn"]='Analysis'
        payload["e"]=[]
        payload["e"].append(msg_finale)

        return payload


    def Data(self):
        WB = WebClient()
        #information contained in the catalog
        infoWave = WB.get_channel_TS(self.pID, self.dName1)
        infoCore = WB.get_channel_TS(self.pID, self.dName2)

        if 0 != infoWave or 0 != infoCore:

            # WAVE  
            dataWave, id, apiWave = self.GetDataTS(infoWave) #get channel data
            my_dict = {key: value for key, value in dataWave["channel"].items() if "field" in key}


            for key, value in my_dict.items():
                nfield = key.split("field")[-1]
                ts_url = f"https://api.thingspeak.com/channels/{id}/fields/{nfield}.json"
                
                # Weekly Analysis
                params ={
                            "api_key": apiWave,
                            "days": 7,
                            "average": "daily"
                        }
                dataWeek = json.loads(requests.get(ts_url, params=params).text)    

                #focus on two types of data: duration and calories
                if "duration" in value: 
                    if len(dataWeek["feeds"]):
                        DurationWeek = np.array([float(0.0) if feed['field'+nfield] is None else round(float(feed['field'+nfield]),2) for feed in dataWeek['feeds']])
                        if sum(DurationWeek) > 0:  #check if there are enough values
                            flagWave_duration = 1  #flag
                        else:
                            flagWave_duration = 0

                if "calories" in value:
                    if len(dataWeek["feeds"]):
                        CaloriesWeek = np.array([float(0.0) if feed['field'+nfield] is None else round(float(feed['field'+nfield]),2) for feed in dataWeek['feeds']])
                        if sum(CaloriesWeek) > 0:  #check if there are enough values
                            flagWave_calories = 1  #flag
                        else:
                            flagWave_calories = 0

            # CORE  
            dataCore, id, apiCore = self.GetDataTS(infoCore) #get channel data
            my_dict = {key: value for key, value in dataCore["channel"].items() if "field" in key}

            for key, value in my_dict.items():
                nfield = key.split("field")[-1]
                ts_url = f"https://api.thingspeak.com/channels/{id}/fields/{nfield}.json"
                
                # Weekly Analysis
                params ={
                            "api_key": apiCore,
                            "days" : 7,
                            "average" : "daily"
                        }
                dataWeek = json.loads(requests.get(ts_url, params=params).text)         
                
                #focus on one type of data: BMI
                if "BMI" in value:
                    if len(dataWeek["feeds"]):
                        BMIWeek = np.array([float(0.0) if feed['field'+nfield] is None else round(float(feed['field'+nfield]),2) for feed in dataWeek['feeds']])
                        if sum(BMIWeek) > 0:  #check if there are enough values
                            flagCore_BMI = 1  #flag
                        else:
                            flagCore_BMI = 0

            if flagCore_BMI ==0 or flagWave_calories==0 or flagWave_duration==0:  #check if all data are available
                msg = "There is not enough data for this week."
                payload={}
                payload["bn"]='Analysis'
                payload["e"]=[]
                payload["e"].append(msg) 
 
            else:
                payload = self.Analysis(BMIWeek, DurationWeek, CaloriesWeek)  #data analysis

        else:
            msg = "You don't have the devices to recover this data."
            payload={}
            payload["bn"]='Analysis'
            payload["e"]=[]
            payload["e"].append(msg)


        return payload


# Main
def main():
    WB=WebClient()

    #information for data exchange
    conf=json.loads(json.dumps(WB.get_broker()))
    bT = conf["baseTopic"]
    broker=conf["IP"]
    port=conf["mqtt_port"]
    clientID = 'dc'+str(random.randint(1,10**5))

    #object to receive/send data
    coll=DataCollector(clientID,broker,port,bT)
    coll.run()
    print(f'This is the client to follow the data coming from the sensors of {coll.baseTopic}')
    coll.client.unsubscribe()
    coll.follow(coll.baseTopic+'/+')

    #get patient list
    pdict = json.loads(json.dumps(WB.get_patients()))

    timewait =  300

    while True:
        #get patient list
        pdict = json.loads(json.dumps(WB.get_patients()))

        # Every timewait update data
        for pID in pdict.keys():
            #object to analyze patient parameters 
            PA = PatientAnalysis(pID)
            msg = PA.Data()  #get the message to send
            coll.pub(pID, msg) 	#send data
            time.sleep(10)
        
        time.sleep(timewait) #Wait


if __name__ == '__main__':
    main()