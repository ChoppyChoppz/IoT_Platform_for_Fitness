"""
    FitnessCatalog for IoT platform Fitness.

"""
import json
import cherrypy
import time
from pathlib import Path

# Global variables
P = Path(__file__).parent.absolute()
JSON_CONF = P / 'conf.json'
JSON_STATIC = P / 'static_patient.json'
JSON_DEVICE_INFO = [P / 'info_wave_device.json', P / 'info_core_device.json', P / 'info_pulse_device.json', P / 'info_gluco_device.json']

#Classes
class FitnessCatalog(object):
    """ Resource catalog class """

    def __init__(self, filename_static, *filename_devices):
        """ Set filename of static jsons """
        self.filename_s = filename_static
        self.load_file()

        """ 
        Generate lists of:
            1) patientIDs;
            2) names;
            3) username_telegram;
            4) deviceIDs.
        """

        self.list_idpatient = [p["patientID"] for p in self.static["patient"]]
        self.list_namepatient = [p["name"] for p in self.static["patient"]]
        self.list_telegrambot = [p["usernameT"] for p in self.static["patient"]]
        
        list_iddevice = []
        for p in self.static["patient"]:
            for d in p['devices']:
                list_iddevice.append(d['devID'])
        self.list_iddevice = list_iddevice

        if len(filename_devices):
            self.filename_w = filename_devices[0][0]
            self.filename_c = filename_devices[0][1]
            self.filename_p = filename_devices[0][2]
            self.filename_g = filename_devices[0][3]


    def load_file(self):
        """ Load static json file """
        loaded = 0
        while not loaded:
            try:
                with open(self.filename_s, "r") as fs:
                    self.static = json.loads(fs.read())
                loaded = 1
            except Exception:
                print("Problem in loading catalog, retrying...")
                time.sleep(.5)

        self.broker_ip = self.static["broker"]["IP"]
        self.mqtt_port = self.static["broker"]["mqtt_port"]
    
    def write_static(self):
        """ Write data on static json file """
        with open(self.filename_s, "w") as fs:
            json.dump(self.static, fs, ensure_ascii=False, indent=2)
            fs.write("\n")
    
    def get_patients(self):
        """ Get patients info """
        self.load_file()

        p_names = [p["name"] for p in self.static["patient"]]             # Generate list of patient names
        p_IDs = [p["patientID"] for p in self.static["patient"]]          # Generate list of patient names

        info = {
                    "patient" : []
                }
        
        if len(p_names):
            for i in range(len(p_names)):
                info_i = {
                            "name" : p_names[i],
                            "patientID" : p_IDs[i]
                        }
                info["patient"].append(info_i)
        
        return info
    
    def get_patientsTS(self):
        """ Get patients deleted in TS """
        self.load_file()        
        return self.static["TS_delete"]
    
    def get_patientsT(self):
        """ Get patients that use TelegramBot """
        self.load_file()

        p_ID = [p["patientID"] for p in self.static["patient"]]               # Generate list of patient names
        p_Tbot = [p["usernameT"] for p in self.static["patient"]]       # Generate list of patient IDs

        info = {
                    "patient" : []
                }
        
        if len(p_Tbot):
            for i in range(len(p_Tbot)):
                info_i = {
                            "patientID" : p_ID[i],
                            "usernameT" : p_Tbot[i]
                        }
                info["patient"].append(info_i)
        
        return info
    
    def get_alarms(self):
        """ Get patients that have an alarm """
        self.load_file()

        info = {
                    "alarm" : []
                }
        
        for p in self.static["patient"]:
            if len(p["alarm"]):
                info_i = {
                            "name" : p['name'],
                            "usernameT" : p["usernameT"],
                            "patientID" : p['patientID']
                        }
                
                info["alarm"].append(info_i)
                
        return info
    
    def get_devices(self, patientID):
        """ Get devices of a specific patient from his ID """

        self.load_file()

        info = {
                    "devices" : []
                }
        
        
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]["patientID"] == patientID:           
                if len(self.static["patient"][i]['devices']):
                    for d in self.static["patient"][i]['devices']:
                        info_i = {
                                    "device" : d['name'],
                                    "devID" : d['devID']
                                }
                        info["devices"].append(info_i)
                
        return info
    
    
    def get_TrainingInfo(self, patientID):
        """ Get training info of a specific patient from his ID """
        self.load_file()

        info = {
                    "e" : []
                }
        
        
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]["patientID"] == patientID:           
                if len(self.static["patient"][i]['training']):
                    for traini in self.static["patient"][i]['training']:
                        info["e"].append(traini)
           
        return info
    

    def get_info_devices(self, patientID):
        """ Get info devices of a specific patient from his ID """
        self.load_file()        
        
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]["patientID"] == patientID:           
                if len(self.static["patient"][i]['devices']):
                    return self.static["patient"][i]['devices']
    

    def get_TS_channelinfo(self, param):
        """ Get info TS device of a specific patient from his ID """

        info = {
                    "tschannel" : ''
                }
        
        self.load_file()
        print(param)
        pID = param['patientID']
        dName = param['name']
        # Generate list of all patientIDs
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['patientID'] == pID:
                for j in range(len(self.static["patient"][i]['devices'])):
                    if self.static["patient"][i]['devices'][j]['name'] == dName:
                        devicecheck = json.loads(json.dumps(self.static["patient"][i]['devices'][j]))
                        if "ID_channel" in devicecheck: # done to check if there is all information to TS
                            info = {
                                        "name" : dName,
                                        "keyTS" : self.static["patient"][i]['keyTS'],
                                        "ID_channel" : self.static["patient"][i]['devices'][j]['ID_channel'],
                                        "api_keys" : self.static["patient"][i]['devices'][j]['api_keys']
                                    }
                        else:
                            print('TS not found')
                            return 0                            
                        
                        return info
                print('Device not found')
                return 0
        print("Patient not found")
        return 0
    
    
    def get_chatID(self, ID):
        """ Get all information about a patient and devices given an ID """

        self.load_file()
        for p in self.static["patient"]:
            if p["patientID"] == ID:
                info = { 
                            "chatID": p['chatID'],
                        }
                return info
        return 'Patient not foud, enter the correct id'


    def add_patient(self, msg):
        """ 
        Add a new patient in the static catalog.
        The new patientID is auto-generated.
        """
        # Check if patient already exists
        if not msg["name"] in self.list_namepatient:
            # Generate a new patientID.
            numID = 1001
            new_id = 'p_' + str(numID)

            while new_id in self.list_idpatient:
                numID += 1
                new_id = 'p_' + str(numID)

            msg["chatID"] = 0   # default
            msg["patientID"] = new_id
            msg["devices"] = []
            msg["alarm"] = []
            msg["training"] = []

            self.static["patient"].append(msg)
            self.write_static()
            
            # Check if doctor, weight and height exist
            if msg["doctor"] != '' and msg["weight"] != '' and msg["height"] != '':
                return 'Patient added successfully'
            elif msg["doctor"] == '' and msg["weight"] == '' and msg["height"] == '':
                return 'Patient added successfully but doctor, weight and height are not define'
            elif msg["doctor"] == '' and msg["weight"] == '' :
                return 'Patient added successfully but doctor and weight are not define'
            elif msg["doctor"] == '' and msg["height"] == '':
                return 'Patient added successfully but doctor and height are not define'
            elif msg["weight"] == '' and msg["height"] == '':
                return 'Patient added successfully but weight and height are not define'
            elif msg["doctor"] == '':
                return 'Patient added successfully but doctor is not define'
            elif msg["weight"] == '':
                return 'Patient added successfully but weight is not define'
            else:
                return 'Patient added successfully but height is not define'            
        else:
            return 'Patient already exists'

    def mod_patient(self, msg):
        """
        Modify patient in the static catalog.
        """
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['name'] == msg["name"]:
                break   
        
        self.static["patient"][i]['doctor'] = msg["doctor"]
        self.static["patient"][i]['usernameT'] = msg["usernameT"]
        self.static["patient"][i]['keyTS'] = msg["keyTS"]
        self.write_static()


    def add_chatID(self, msg):
        """
        Add chatID in the static catalog.
        """
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['usernameT'] == msg["usernameT"]:
                break   
        
        self.static["patient"][i]['chatID'] = msg["chatID"]
        self.write_static()


    def add_device(self, dev_json):
        """
        Add a new device in the static catalog.
        The new deviceID is auto-generated.
        """

        # Check if patient exists
        if dev_json['patientID'] in self.list_idpatient:
            
            list_name = []
            ind_patient = 0

            for i in range(len(self.static["patient"])):
                if self.static["patient"][i]['patientID'] == dev_json["patientID"]:
                    for j in range(len(self.static["patient"][i]['devices'])):
                        list_name.append(self.static["patient"][i]['devices'][j]["name"])
                    ind_patient = i
                    break                                   
            
            
            if not dev_json['name'] in list_name:           
                # Generate a new devID 
                numID = 1001
                new_id = 'd_' + str(numID)

                while new_id in self.list_iddevice:
                    numID += 1
                    new_id = 'd_' + str(numID)

                dev_json["devID"] = new_id

                info = self.device_info(dev_json['name'])
                if info != -1:
                    dev_json.update(info)
                else:
                    return 'Device unknow'

                del dev_json["patientID"]
                self.static["patient"][ind_patient]["devices"].append(dev_json)
                self.write_static()

                return 'Device added successfully'
            else:
                return 'Device already exist'  
        else:
            return 'It is not possible to add the device, write the payload correctly'

    def add_new_weight(self, weight_json):
        """
        Add a new weight to a patient.
        """ 
        basename = weight_json.get("bn")      
        pID = basename.split("/")[-1]

        for i in range(len(self.list_idpatient)):
            if pID == self.list_idpatient[i]:
                self.static["patient"][i]["weight"]=weight_json["e"][0]["v"]
                self.write_static() 
                return 'New weight added successfully'

    def add_alarm(self, alarm_json):
        """
        Add an alarm to a patient.
        """ 
        basename = alarm_json.get("bn")      
        pID = basename.split("/")[-1]
        name_device=basename.split("/")[0]

        for i in range(len(self.list_idpatient)):
            if pID == self.list_idpatient[i]:
                if self.static["patient"][i]["alarm"]==[]: 
                    self.static["patient"][i]["alarm"].append({"Device":[]})
                    self.static["patient"][i]["alarm"].append({"Telegram":[]})

                alarm_json["bn"]=str(name_device)
                self.static["patient"][i]["alarm"][0]["Device"].append(alarm_json)
                self.write_static() 
                return 'Alarm added successfully'
            
    def add_alarm_telegram(self, alarm_json):
        """
        Add an alarm to a patient given his ID.
        """ 

        telegramBot = alarm_json.get("bn")      
        pID = telegramBot.split("/")[-1]
        bn=telegramBot.split("/")[0]

        for i in range(len(self.list_idpatient)):
            if pID == self.list_idpatient[i]:
                if self.static["patient"][i]["alarm"]==[]: 
                    self.static["patient"][i]["alarm"].append({"Device":[]})
                    self.static["patient"][i]["alarm"].append({"Telegram":[]})

                alarm_json["bn"]=str(bn)
                self.static["patient"][i]["alarm"][1]["Telegram"].append(alarm_json)
                self.write_static() 
                return 'Alarm added successfully'
            
    def add_trainingInfo(self, ID, train_json):
        """
        Add training info to a patient.
        """       
        pID = ID

        for i in range(len(self.list_idpatient)):
            if pID == self.list_idpatient[i]:
                self.static["patient"][i]["training"] = []
                self.write_static()
                for train_i in train_json["e"]:
                    self.static["patient"][i]["training"].append(train_i)
                self.write_static() 
                return 'Training info added successfully'

    def add_TSchannel(self, ID, ts_json):
        """
        Add info of TS channel to a patient given his ID.
        """
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['patientID'] == ID:
                if len(self.static["patient"][i]['devices'])==0:
                    print("No paired device")
                else:
                    for j in range(len(self.static["patient"][i]['devices'])):
                        if self.static["patient"][i]['devices'][j]["name"] in ts_json["name"]:
                            self.static["patient"][i]['devices'][j]['ID_channel'] = ts_json["id"]
                            self.static["patient"][i]['devices'][j]['api_keys'] = ts_json["api_keys"]
                            self.write_static() 
                            return 'Info TS added successfully'

    def info(self, ID):
        """
        Return all information about a patient and devices given an ID.
        """

        self.load_file()
        for p in self.static["patient"]:
            if p["patientID"] == ID:
                info = { 
                            "patientID": p['patientID'], 
                            "name": p["name"], 
                            "age": p["age"],
                            "height" : p["height"],
                            "weight" : p["weight"],
                            "usernameT" : p["usernameT"],
                            "keyTS"    : p["keyTS"],
                            "doctor" : p['doctor']
                        }
                return info
        return 'Patient not foud, enter the correct id'
    

    def search(self, name):
        """
        Return all information about a patient and devices given a name.
        """

        self.load_file()
        for p in self.static["patient"]:
            if p["name"] == name:
                info = { 
                            "patientID": p['patientID'], 
                            "name": p["name"], 
                            "age": p["age"],
                            "height" : p["height"],
                            "weight" : p["weight"],
                            "usernameT" : p["usernameT"],
                            "keyTS"    : p["keyTS"],
                            "doctor" : p['doctor']
                        }
                return info
        return 'Patient not foud, enter the correct id'
    
    def device_info(self, name_device):
        """
        Load info of a specific type of device.
        """

        if name_device == 'wave':
            with open(self.filename_w, "r") as fs:
                info = json.loads(fs.read())
            return info
          
        elif name_device == 'core':
            with open(self.filename_c, "r") as fs:
                info = json.loads(fs.read())
            return info

        elif name_device == 'pulse':
            with open(self.filename_p, "r") as fs:
                info = json.loads(fs.read())
            return info
        elif name_device == 'gluco':
            with open(self.filename_g, "r") as fs:
                info = json.loads(fs.read())
            return info
        else:
            return -1
    
    def delete_patient(self, param):
        """
        Delete a patient in the static catalog.
        """
        self.load_file()
        pID = param['patientID']
        # Generate list of all patientIDs
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['patientID'] == pID:
                json_tsD = {
                    "patientID" : self.static["patient"][i]["patientID"],
                    "name" : self.static["patient"][i]["name"],
                    "keyTS" : self.static["patient"][i]["keyTS"]
                }
                self.static["TS_delete"].append(json_tsD)
                del self.static["patient"][i]
                self.write_static()
                return 'Patient delete'        
        return 'Patient non found'
    
    def delete_ts(self, param):
        """
        Delete a patient in the static catalog.
        """
        self.load_file()
        pID = param['patientID']
        # Generate list of all patientIDs
        for i in range(len(self.static["TS_delete"])):
            if self.static["TS_delete"][i]['patientID'] == pID:
                del self.static["TS_delete"][i]
                self.write_static()
                #self.DB.delpatient(pID)
                return 'Patient delete'        
        return 'Patient non found'

    def delete_device(self, param):
        """
        Delete a device in the static catalog.
        """
        self.load_file()

        pID = param['patientID']
        dID = param['devID']
        
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['patientID'] == pID:                
                for j in range(len(self.static["patient"][i]['devices'])):
                    if self.static["patient"][i]['devices'][j]['devID'] == dID:   
                        del self.static["patient"][i]['devices'][j]
                        self.write_static()
                        #self.DB.deldevice(pID, dID)
                        return 'Device delete'
                return 'Device not found'
        return 'Patient not found'

    def delete_alarm(self, param):
        """
        Delete alarm in the static catalog.
        """
        self.load_file()

        patientID = param['patientID']
        
        for i in range(len(self.static["patient"])):
            if self.static["patient"][i]['patientID'] == patientID:                
                self.static["patient"][i]['alarm'] = []
                self.write_static()
                return 'Alarm delete'
        return 'Patient not found'


class WebServer(object):
    """
    CherryPy webserver.
    """

    exposed = True

    """---Define GET HTTP method for RESTful webserver.----"""
    @cherrypy.tools.json_out()

    def GET(self, *uri, **params):
        cat = FitnessCatalog(JSON_STATIC)
        cat.load_file()
        
        # uri non presente
        if len(uri)==0:
            return 'Error'

        # Get broker info (url, port).
        if uri[0] == 'broker':
            return cat.static["broker"]
        
        # Get thingspeak info (url, port).
        if uri[0] == 'ts':
            return cat.static["thingspeak"]

        # Get static catalog.
        if uri[0] == 'static':
            return cat.static
        
        # Get list of all patients {'i' : 'namei'}.
        if uri[0] == 'patients':
            return cat.get_patients()
        
        # Get list of all patients {'i' : 'namei'}.
        if uri[0] == 'pThingspeak':
            return cat.get_patientsTS()
        
        # Get list of all patients {'name' : 'namei', 'telegram' : 'usernamei'}.
        if uri[0] == 'pTelegram':
            return cat.get_patientsT()
        
        # Get list of all patients in alarm {'name' : 'namei', 'contact' : 'usernameTi', 'patientID' : 'patientIDi'}.
        if uri[0] == 'alarms':
            return cat.get_alarms()
        
        # Get all device of patient.
        if uri[0] == 'devices':
            name = params['patientID']
            if len(params)==0:
                return 'Inserire anche il nome del paziente'
            return cat.get_devices(name)
        
        # Get all info of device of a patient. #nuova
        if uri[0] == 'devices_info':
            name = params['patientID']
            if len(params)==0:
                return 'Inserire anche il nome del paziente'
            return cat.get_info_devices(name)
        
        # Get all information about a specific patient from ID.
        if uri[0] == 'info':
            ID = params['patientID']                     #Ex: http://127.0.0.1:8080/info_ID/p_1001
            if len(uri)==0:
                return 'Inserire anche l\'ID del paziente'
            return cat.info(ID)
        
        # Get all information about patient from name.
        if uri[0] == 'info_name':
            name = params['name']
            if len(params)==0:
                return 'Inserire anche il nome del paziente'
            return cat.search(name)
        
        # Get information about chatID telefram of a specific patient from ID.
        if uri[0] == 'chatID':
            ID = params['patientID']                     #Ex: http://127.0.0.1:8080/info_ID/p_1001
            if len(uri)==0:
                return 'Inserire anche l\'ID del paziente'
            return cat.get_chatID(ID)
        
        # Get training info of patient.
        if uri[0] == 'training':
            ID = params['patientID']
            if len(params)==0:
                return 'Inserire anche l\'ID del paziente'
            return cat.get_TrainingInfo(ID)
        
        # Get channelTS info of patient.
        if uri[0] == 'channelTS':
            if len(params)<2:
                return "Inserire tutti i parametri"
            return cat.get_TS_channelinfo(params)

    
    """--- Define POST HTTP method for RESTful webserver.---"""
    @cherrypy.tools.json_out()

    def POST(self, *uri, **params):
        cat = FitnessCatalog(JSON_STATIC, JSON_DEVICE_INFO)

        # Add new patient.
        if uri[0] == 'add_patient':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            print(json.dumps(body))
            return cat.add_patient(body)
            # return condition #da modificare
            

         # Modify patient.
        if uri[0] == 'mod_patient':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            print(json.dumps(body))
            return cat.mod_patient(body)
            # return condition #da modificare


        # Add new device.
        if uri[0] == 'add_device':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            return cat.add_device(body) 
        
        # Add weight
        if uri[0] == 'new_weight':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            return cat.add_new_weight(body)

        # Add alarm
        if uri[0] == 'alarm':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            return cat.add_alarm(body) 

        # Add alarm telegram
        if uri[0] == 'alarm_telegram':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            return cat.add_alarm_telegram(body)
        
        # Add training
        if uri[0] == 'training':
            ID = uri[1]                   
            if len(uri)==1:
                return 'Inserire anche l\'ID del paziente'
            body = json.loads(cherrypy.request.body.read())  # Read body data
            return cat.add_trainingInfo(ID, body) 

        # Add ts channel
        if uri[0] == 'add_TSchannel':
            ID = uri[1]                   
            if len(uri)==1:
                return 'Inserire anche l\'ID del paziente'
            body = json.loads(cherrypy.request.body.read())  # Read body data
            return cat.add_TSchannel(ID,body)
        
        # Add chatID.
        if uri[0] == 'add_chatID':
            body = json.loads(cherrypy.request.body.read())  # Read body data
            print(json.dumps(body))
            return cat.add_chatID(body)
            # return condition #da modificare

    """--- Define DELETE HTTP method for RESTful webserver.---"""
    @cherrypy.tools.json_in()

    def DELETE(self, *uri, **params):        
        cat = FitnessCatalog(JSON_STATIC)
        cat.load_file()

        # Delete patient.
        if uri[0] == 'delete_patient':
            if len(params):
                print(params)
                return cat.delete_patient(params)
            else:
                return 'ID pateint is not defined'
            
        # Delete patient from TS.
        if uri[0] == 'delete_ts':
            if len(params):
                print(params)
                return cat.delete_ts(params)
            else:
                return 'ID pateint is not defined'
        
        # Delete device.
        if uri[0] == 'delete_device':
            if len(params) == 2:
                return cat.delete_device(params)
            else:
                return 'ID pateint and devaice name are not defined' 
            
        # Delete device.
        if uri[0] == 'delete_alarm':
            if len(params) == 1:
                return cat.delete_alarm(params)
            else:
                return 'ID pateint is not defined' 

# Main
def main():

    try:
        conf = {
                '/': {
                    'request.dispatch': cherrypy.dispatch.MethodDispatcher()
                    },
            }
        cherrypy.tree.mount(WebServer(), '/', conf)

        """ Global Configuration of WebServer"""
        with open(JSON_CONF, "r") as fs:
            settings = json.loads(fs.read())

        cherrypy.config.update({
                                    'server.socket_host': settings["cat_ip"] , 
                                    'server.socket_port': int(settings["cat_port"])
                                })
        
        """ Starts the embedded Webserver """
        cherrypy.engine.start()
        cherrypy.engine.block()

    except KeyboardInterrupt:
        print("Stopping the engine")
        return

if __name__ == '__main__':
    main()
    
    
