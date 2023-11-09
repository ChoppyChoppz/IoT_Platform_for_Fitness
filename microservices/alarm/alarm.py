"""
    Alarm for IoT platform Fitness.
    
"""

from MyMQTT import *
from WebClient import WebClient
import json
import time
import random
    
    
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
        #print(json.dumps(payload,indent=4))
        self.alarm(topic,payload) #analysis of data received
    
    def alarm(self,topic,payload):
        id_patient=topic.split('/')[-1]
        WC=WebClient()

        if id_patient != 'noderedtry':
            #topic to send data via MQTT
            send_topic='IoT_project/telegram/alarm/'+str(id_patient)
            
            #object to check patient parameters
            AR=AlarmRange(payload,id_patient)
            value, c=AR.value()
            if c != 0: #check for out of range values
                self.client.myPublish(send_topic,value) #sending via MQTT to Telegram
                WC.post_alarm(json.dumps(value)) #sending via REST to Catalog
                time.sleep(5)



class AlarmRange():
    def __init__(self,payload,id_patient):
        self.payload=payload
        self.ID=id_patient
    
    def value(self):
        alarm={}
        alarm["bn"]=''
        alarm["e"]=[]
        c=0
        #Only data from two devices are analyzed: pulse and gluco.
        if self.payload["bn"] == 'pulse': 
            alarm["bn"]=self.payload["bn"]+'/'+str(self.ID) #basename has the device name and the patient id
            for x in self.payload["e"]:
                if x["n"]=='Sp02':
                    if x["v"] < 80:  # 80 is the limit value for oxygenation
                        alarm["e"].append(x)
                        c=c+1

                elif x["n"]=='frequency':
                    if x["v"] < 45 or x["v"] >120:  #(45-120) is the optimal range for frequency
                        alarm["e"].append(x)
                        c=c+1
        
        elif self.payload["bn"] == 'gluco':
            alarm["bn"]=self.payload["bn"]+'/'+str(self.ID) #basename has the device name and the patient id
            for x in self.payload["e"]:
                if x["n"]=='glucometer':
                    if x["v"] < 60 or x["v"] >140:  #(60-140) is the optimal range for glycemia
                        alarm["e"].append(x)
                        c=c+1

        return alarm, c



# Main
def main():

    WB=WebClient()

    #information for data submission
    conf=json.loads(json.dumps(WB.get_broker()))
    bT = conf["baseTopic"]
    broker=conf["IP"]
    port=conf["mqtt_port"]

    #object to receive/send data
    coll=DataCollector('dc'+str(random.randint(1,10**5)),broker,port,bT)
    coll.run()

    print(f'This is the client to follow the data coming from the sensors of {coll.baseTopic}')
    coll.client.unsubscribe()
    coll.follow(coll.baseTopic+'/+')

    while True:
        time.sleep(5)



if __name__ == '__main__':
    main()