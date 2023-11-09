import requests
import json
from pathlib import Path

# Global variables
P = Path(__file__).parent.absolute()
CONFIG = P / 'conf.json'                                          # Config file with absolute path

class WebClient(object):
    """ Get info from catalog """

    def __init__(self):
        file = open(CONFIG, 'r')
        self.config = json.load(file)
        file.close()
        return
    
    def get_broker(self):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/broker" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)            # GET for catalog

        return data
    
    def get_ts(self):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/ts" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)            # GET for catalog

        return data

    def get_patients(self):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/patients" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)            # GET for catalog

        "**** Optimising data for GUI ****"
        p_ids = [p["patientID"] for p in data["patient"]]   # Generate list of index patient
        p_names = [p["name"] for p in data["patient"]]          # Generate list of patient names 
        p_dict = dict(zip(p_ids, p_names))                      # Generate dictionary of patient

        return p_dict
    
    def get_patients_TS(self):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/pThingspeak" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)            # GET for catalog

        return data
    
    def get_patientsT(self):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/pTelegram" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)                            # GET for catalog
        print(cat_url)
        "**** Optimising data for Telegram ****"
        if data["patient"]:
            p_ID = [p["patientID"] for p in data["patient"]]                   # Generate list of patient names
            p_telegram = [p["usernameT"] for p in data["patient"]]       # Generate list of patient IDs
        else:
            p_ID = ''
            p_telegram = ''

        p_dict = dict(zip(p_ID, p_telegram))                               # Generate dictionary of Telegram
        return p_dict
    
    def get_patientsT_ID(self,TbotName):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/pTelegram" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)                            # GET for catalog
        print(cat_url)
        "**** Optimising data for Telegram ****"
        if data["patient"]:
            p_ID = [p["patientID"] for p in data["patient"]]                   # Generate list of patient names
            p_telegram = [p["usernameT"] for p in data["patient"]]       # Generate list of patient IDs
        else:
            p_ID = ''
            p_telegram = ''

        p_dict = dict(zip(p_ID, p_telegram))                               # Generate dictionary of Telegram
        #Ricerca dati paziente
        cerca = SearchPatient(str(TbotName))
        #recupero id paziente
        id_patient= cerca.id_patient(p_dict)

        return id_patient
    
    def get_patients_alarm(self):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/alarms" #URL for GET
        print("Sending a GET request to %s ..." %(cat_url))
        data = json.loads(requests.get(cat_url).text)              # GET for catalog

        "**** Optimising data for GUI ****"
        p_names = []
        p_Tbot = []
        p_ID = []
        p_Tbot = [p["usernameT"] for p in data["alarm"]]   # Generate list of telegram patient
        p_names = [p["name"] for p in data["alarm"]]           # Generate list of patient names 
        p_ID = [p["patientID"] for p in data["alarm"]] 
        p_dict = dict(zip(p_names, p_Tbot))                    # Generate dictionary of patient
        p_dictID = dict(zip(p_names, p_ID))
        return p_dict, p_dictID

    def get_devices(self,pID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/devices" #URL for GET
        params = {"patientID" : pID}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        data = json.loads(requests.get(cat_url, params=params).text)            # GET for catalog

        "**** Optimising data for GUI ****"
        d_device = ''
        d_ids = ''
        
        if len(data["devices"]): 
            d_ids = [d["devID"] for d in data["devices"]]      # Generate list of device IDs
            d_device = [d["device"] for d in data["devices"]]                 # Generate list of device names                   
        
        d_dict = dict(zip(d_ids, d_device))                          # Generate dictionary of device
        return d_dict

    def get_info_devices(self,pID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/devices_info" #URL for GET
        params = {"patientID" : pID}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        data = json.loads(requests.get(cat_url, params=params).text)
        return data
    
    def get_chatID(self,pID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/chatID" #URL for GET
        params = {"patientID" : pID}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        data = json.loads(requests.get(cat_url, params=params).text)
        "**** Optimising data for Telegram ****"
        return data["chatID"]

    def get_info_patient(self,pID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/info" #URL for GET
        params = {"patientID" : pID}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        data = json.loads(requests.get(cat_url, params=params).text)            # GET for catalog        
        return data
    
    def get_info_training(self,pID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/training" #URL for GET
        params = {"patientID" : pID}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        data = json.loads(requests.get(cat_url, params=params).text)            # GET for catalog        
        return data
    
    def get_channel_TS(self,pID,Dname):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/channelTS" #URL for GET
        params = {"patientID" : pID, "name": Dname}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        data = json.loads(requests.get(cat_url, params=params).text)            # GET for catalog        
        return data
    
    def post_patient(self,msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/add_patient"
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(msg))
    
    def mod_patient(self, msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/mod_patient"  
        print("Sending a POST request to %s " %(cat_url))      
        return requests.post(cat_url, json.dumps(msg))
    
    def post_device(self, msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/add_device"
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(msg))
    
    def post_TS_channel(self, pID, msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/add_TSchannel/"+str(pID)
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(msg))
    
    def post_alarm(self, msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/alarm"
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(json.loads(msg)))
    
    def post_alarm_telegram(self, msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/alarm_telegram"
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(json.loads(msg)))
    
    def post_training(self, pID, msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/training/" + pID
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(msg))
    
    def post_chatID(self,msg):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/add_chatID"
        print("Sending a POST request to %s " %(cat_url))
        return requests.post(cat_url, json.dumps(msg))

    def delete_patient(self,params):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/delete_patient" 
        print("Sending a DELETE request to %s with params %s..." %(cat_url, params))
        return requests.delete(cat_url, params=params)
    
    def delete_alarm(self,params):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/delete_alarm" 
        print("Sending a DELETE request to %s with params %s..." %(cat_url, params))
        return requests.delete(cat_url, params=params)
    
    def delete_device(self, pID, dID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/delete_device" 
        params = {"patientID" : pID, "devID": dID}
        str_params = json.dumps(params)
        print("Sending a DELETE request to %s with params %s..." %(cat_url, str_params))
        return requests.delete(cat_url, params = params)

    def delete_TS(self,pID):
        cat_url = "http://" + self.config["cat_ip"] + ":" + self.config["cat_port"] + "/delete_ts" 
        params = {"patientID" : pID}
        str_params = json.dumps(params)
        print("Sending a GET request to %s with params %s..." %(cat_url, str_params))
        return requests.delete(cat_url, params=params)


class SearchPatient():
    def __init__(self,name):
        self.name=name

    def id_patient(self,lista_pazienti):
        lista_nomi=list(lista_pazienti.values())
        lista_id=list(lista_pazienti.keys())
        for i in range(len(lista_nomi)):
            if self.name==lista_nomi[i]:
                return lista_id[i]
        
        return 'Non presente'
    
    def TS_delete(self,lista):
        for x in lista:
            if x["name"]==self.name:
                return x

        return print('Paziente non trovato.')

#Prova
# Main
def main():
    WB=WebClient()




if __name__ == '__main__':
    main()