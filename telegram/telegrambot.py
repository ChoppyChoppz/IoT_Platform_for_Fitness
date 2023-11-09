"""
        Telegram bot for IoT platform Fitness.
"""

from telegram import *
from telegram import ext
import logging
import json
import requests
import time
from MyMQTT import *
from pathlib import Path
from time import strftime, localtime
import random
from WebClient import WebClient
import urllib.parse

# Enable logging, logging is a different way we can see what is happening
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - '
                    '"%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# Global variables
P = Path(__file__).parent.absolute()
CONF = P / 'settings_telegram.json'

with open(CONF, "r") as f:
    config = json.loads(f.read())    
    token=config['telegramToken']



# MQTT that follows the alarm topic and sends a message to the user when the alarm is triggered
class DataCollector():
    def __init__(self,clientID,broker,port,baseTopic, token):
        self.clientID=clientID
        self.baseTopic=baseTopic
        self.Topic=baseTopic
        self.client=MyMQTT(clientID,broker,port,self)
        self.token=token


    def run(self):
        self.client.start()
        print('{} has started'.format(self.clientID))
        
    def end(self):
        self.client.stop()
        print('{} has stopped'.format(self.clientID))

    def follow(self,topic):
        self.client.mySubscribe(topic)
        
        #when notify get the message from the topic it send a telegram get request to the user using chatID and the message. The msg is received in SenML format.
    def notify(self,topic,msg):
        payload=json.loads(msg)

        ID_patient=topic.split("/")[-1]
        WC = WebClient()
        chatID = WC.get_chatID(ID_patient)

        if chatID != 0:
            if "alarm" in topic:        #Es. IoT_project/telegram/alarm/p_1001
                for x in payload['e']:
                    dt = strftime('%H:%M %d-%m-%Y', localtime(x['t']))
                    text_msg = "Your device "+ payload['bn'].split("/")[0] + " measured an abnormal value of  " + str(x["v"]) + " on the " +x['n'] + " at the time " + dt + ", an alert has already been sent to your doctor."
                    requests.get("https://api.telegram.org/bot"+str(token)+"/sendMessage?chat_id="+str(chatID)+"&text="+text_msg)

            if "analysis" in topic:     #Es. IoT_project/telegram/analysis/p_1001
                for x in payload['e']:
                    text_msg = str(x)
                    requests.get("https://api.telegram.org/bot"+str(token)+"/sendMessage?chat_id="+str(chatID)+"&text="+text_msg)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, context: ext.CallbackContext):
    """Send a message when the command /start is issued."""
    
    WB = WebClient()
    # Get all patient subscribed to the service from catalog
    patient_dict = WB.get_patientsT()               

    # Send chat_id to catalog. 
    data = {
                "usernameT": update.message.from_user.username,
                "chatID": update.message.chat_id
           }

    WB.post_chatID(data)

    # Check if the user is registered in the service 
    print(patient_dict)
    if not data["usernameT"] in list(patient_dict.values()):
        msg_w = ("Welcome to the Smart Health IoT 🫀" +
            "\nUnfortunately, you are not registered in our service."+
            "\nPlease contact your doctor who will provide you with all the information you need to register.")

        context.bot.sendMessage(chat_id = update.message.chat_id, text = msg_w, parse_mode=ParseMode.MARKDOWN)
        
    else:

        msg_c = ("Welcome %s to the Smart Health IoT 🫀." % (next((v for k, v in list(patient_dict.items()) if v == data["usernameT"]), None)) 
                + "\nNow, you can access our services:" )

        # create a list of buttons
        buttons = [[InlineKeyboardButton("Balance",            callback_data='1')],
                   [InlineKeyboardButton("Training sessions",  callback_data='2')],
                   [InlineKeyboardButton("Device",             callback_data='3')],
                   [InlineKeyboardButton("Support",            callback_data='4')]]
        
        

        # create an InlineKeyboardMarkup object
        reply_markup = InlineKeyboardMarkup(buttons)

        # send a message with the custom keyboard
        context.bot.sendMessage(chat_id = update.message.chat_id, text = msg_c, reply_markup = reply_markup,
                                parse_mode=ParseMode.MARKDOWN)



def button(update: Update, context: ext.CallbackContext):

    # retrieve the callback_data from the button press
    callback_data = update.callback_query.data
    usernameTBot = update.callback_query.from_user.username

    # show some data based on the callback_data

    # 1 --> Balance
    if callback_data == '1':
        peso=Balance(usernameTBot)
        mgs = "Your weight is reported to be " + str(peso) + " kg"
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=mgs)

    # 2 --> Training
    elif callback_data == '2':
        msg = TrainingSession(usernameTBot)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=msg, parse_mode=ParseMode.MARKDOWN)

    # 3 --> Devices
    elif callback_data == '3':
        id_patient=WebClient().get_patientsT_ID(usernameTBot)
        device_dict =WebClient().get_devices(id_patient)
        keyboard = []
        
        #Buttons for each device creation 
        for key, value in device_dict.items():
            # create a button with the key as the label and the value as the callback data
            button = InlineKeyboardButton(value, callback_data=str(value)+'/'+str(id_patient))
            # append the button to the keyboard list
            keyboard.append([button])
        
        # create a reply markup with the keyboard
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Your device:", reply_markup = reply_markup)

    # 4 --> Support
    elif callback_data == '4':
        alarm_json=Alarm(usernameTBot)

        # Sending alarm from telegram to the doctor.
        WebClient().post_alarm_telegram(json.dumps(alarm_json))

        # Sending response to the user on telegram.
        mgs = "The doctor will call you soon."
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=mgs)
    
    # Others --> Manage devices and send link to visualize data
    else:
        Dname = callback_data.split("/")[0]
        pID=callback_data.split("/")[-1]
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=Dname)
        plot_TS(pID,Dname)


def Balance(TbotName): 
    # Using the WebClient class to get the patient's ID with Telegram username as input
    id_patient=WebClient().get_patientsT_ID(TbotName)
    # retrieve information about weight
    info_patient=json.loads(json.dumps(WebClient().get_info_patient(str(id_patient))))
    peso=info_patient["weight"]

    return peso
   
   
def TrainingSession(TbotName):
    #retrieve patient ID using telegram bot username
    id_patient = WebClient().get_patientsT_ID(TbotName)

    #retrieve information about and score
    data = WebClient().get_info_training(id_patient)
    text_msg = ''
    print(data['e'])
    if len(data["e"]) == 0:
        text_msg = 'Impossible to compute scores'
    elif len(data["e"]) == 1:
        text_msg = 'Impossible to compute scores'
    else:
        text_msg = f'*SCORE DAY: {data["e"][0]["v"]}/5* with claories burnes {data["e"][2]["v"]} {data["e"][2]["u"]}\n \n \n*SCORE WEEK: {data["e"][1]["v"]}/5 *with claories burnes {data["e"][3]["v"]} {data["e"][3]["u"]}'
    
    return text_msg


def Alarm(TbotName):
    #get patient ID using telegram bot username
    id_patient=WebClient().get_patientsT_ID(TbotName)

    alarm_json={}
    alarm_json["bn"]='Support/'+ str(id_patient)
    alarm_json["e"]=[]
    
    time_alarm = {
        "t":int(time.time())
    }
    alarm_json["e"].append(time_alarm)
    
    return alarm_json


def plot_TS(pID,Dname):

    WB = WebClient()
    data = WB.get_channel_TS(pID,Dname)
    chatID = WB.get_chatID(pID)
    if 0 != data:
        for i in range(len(data["api_keys"])):
            if data["api_keys"][i]["write_flag"] != True:
                break
        #build api request for teamspeak
        id = data["ID_channel"]
        api = data["api_keys"][i]["api_key"]
        ts_url = f"https://api.thingspeak.com/channels/{id}/feeds.json"
        params = { "api_key" : api, "results" : str(2)}
        # GET for TS
        data = json.loads(requests.get(ts_url, params=params).text)   
        my_dict = {key: value for key, value in data["channel"].items() if "field" in key}
        print(my_dict)

        flag=0  
        for key, value in my_dict.items():
            nfield = key.split("field")[-1]
            ts_url = f"https://api.thingspeak.com/channels/{id}/fields/{nfield}.json"
            params = { "api_key" : api, "days" : 7} # ultimi 7 giorni
            # GET for TS
            dataWeek = json.loads(requests.get(ts_url, params=params).text)
            if len(dataWeek["feeds"]):
                url = f'https://api.thingspeak.com/channels/{id}/charts/{nfield}'
                params_week={
                    "title": 'Weekly',
                    "dynamic": True,
                    "update": 15,
                    'width': 'auto',
                    'height': 'auto',
                    "api_key": api,
                    "days": 7
                }
                params_day={
                    "title": 'Daily',
                    "dynamic": True,
                    "update": 15,
                    'width': 'auto',
                    'height': 'auto',
                    "api_key": api,
                    "days": 1
                }
                link_week=concatenate_url_params(url, params_week)
                link_day=concatenate_url_params(url, params_day)

                url_telegram='https://api.telegram.org/bot'+str(token)+'/sendMessage'
                params_telegram={
                    "chat_id": str(chatID),
                    "text": str(value)+'\n'+'Weekly: '+str(link_week)+'\n'+'Daily: '+str(link_day),
                }
                requests.get(url_telegram,params=params_telegram)
                flag=1
        
        if flag==0:
            msg = "No data for this week"
            print(msg)
            requests.get("https://api.telegram.org/bot"+str(token)+"/sendMessage?chat_id="+str(chatID)+"&text="+msg)



def concatenate_url_params(url, params):
    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)
    return urllib.parse.urlunparse(url_parts)


def Notification(token):
    # Information for data exchange
    WB=WebClient()
    conf=json.loads(json.dumps(WB.get_broker()))
    bT = conf["baseTopic"]
    broker=conf["IP"]
    port=conf["mqtt_port"]
    coll=DataCollector('dc'+str(random.randint(1,10**5)),broker,port,bT,token)

    coll.run()
    print(f'This is the client to follow the data coming from the sensors of {coll.baseTopic}')
    coll.client.unsubscribe()
    coll.follow("IoT_project/telegram/#")  



def main():
    """Setup and start the bot."""

    with open(CONF, "r") as f:
        config = json.loads(f.read())

    # Load TOKEN from conf file    
    token=config['telegramToken']

    updater = ext.Updater(token, use_context=True)
    # Get the dispatcher to register handlers.
    dp = updater.dispatcher
    # Activate different commands.
    start_handler = ext.CommandHandler('start', start, run_async=True)
    dp.add_handler(start_handler)

    button_handler = ext.CallbackQueryHandler(button, run_async=True)
    dp.add_handler(button_handler)
    # Log all errors.
    #dp.add_error_handler(error)

    """ Start the Bot."""

    Notification(token)
    updater.start_polling()
    
    updater.idle()


if __name__ == '__main__':
    main()