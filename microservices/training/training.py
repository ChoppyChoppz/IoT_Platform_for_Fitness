"""
    Training for IoT platform Fitness.
"""
from MyMQTT import *
from WebClient import *
import json
import requests
import time
import numpy as np
from pathlib import Path


# Global variables
P = Path(__file__).parent.absolute()

class PatientTraining(object):

    def __init__(self,pID):        
        self.pID = pID
        self.dName = "wave"

    def Score(self, steps, duration):
        # Calculate Score day using number of step and duration time of day
        score = 0

        if steps[-1] == 0:
            score = 0
        
        elif steps[-1] < 7000:
            score = 1

        elif steps[-1] >= 7000 and steps[-1] <= 15000:
            score = 2

        elif steps[-1] > 15000:
            score = 3

        if duration[-1] != 0:
            if steps[-1]/duration[-1] < 200:
                score = score
            else:
                score += 1
        
        return score
    
    def ScoreWeek(self, steps, duration):
        # Calculate Score day using number of step and duration time of week
        score = 0
        
        if sum(steps) == 0:
            score = 0
        
        elif sum(steps) < 7000 * len(steps):
            score = 1

        elif sum(steps) >= 7000 * len(steps) and sum(steps) <= 15000 * len(steps):
            score = 2

        elif sum(steps) > 15000 * len(steps):
            score = 3

        if sum(duration) != 0:
            if sum(steps)/sum(duration) < 200:
                score = score
            else:
                score += 1
        
        return score
        

    def Data(self):
        WB=WebClient()     
        # Get info of Thingspeak channel   
        data = WB.get_channel_TS(self.pID, self.dName)
        calories = []
        # print(data)
        if 0 != data: # Equal to 0 data not availe
            for i in range(len(data["api_keys"])):
                if data["api_keys"][i]["write_flag"] != True:
                    break
            
            id = data["ID_channel"]
            api = data["api_keys"][i]["api_key"]
            ts_url = f"https://api.thingspeak.com/channels/{id}/feeds.json"
            params = { "api_key" : api, "results" : str(2)}
            data = json.loads(requests.get(ts_url, params=params).text)            # GET for TS   
            my_dict = {key: value for key, value in data["channel"].items() if "field" in key}

            for key, value in my_dict.items():
                nfield = key.split("field")[-1]
                ts_url = f"https://api.thingspeak.com/channels/{id}/fields/{nfield}.json"
                params = { "api_key" : api, "days" : 7} # ultimi 7 giorni
                dataWeek = json.loads(requests.get(ts_url, params=params).text)          # GET for TS 

                # Weekly Analysis
                params ={
                            "api_key": api,
                            "day": 7,
                            "sum": "daily"
                        }
                
                url = f'https://api.thingspeak.com/channels/{id}/fields/{nfield}.json'

                if "duration" in value:
                    if len(dataWeek["feeds"]):
                        responseD = json.loads(requests.get(url, params=params).text) 
                        DurationWeek = np.array([float(0.0) if feed['field'+nfield] is None else float(feed['field'+nfield]) for feed in responseD['feeds']])
                        #print(DurationWeek)

                elif "steps" in value:
                    if len(dataWeek["feeds"]):
                        responseS = json.loads(requests.get(url, params=params).text)
                        StepsWeek = []
                        StepsWeek = np.array([float(0.0) if feed['field'+nfield] is None else float(feed['field'+nfield]) for feed in responseS['feeds']])
                        #print(StepsWeek)

                elif "calories" in value:
                    if len(dataWeek["feeds"]):
                        responseS = json.loads(requests.get(url, params=params).text)
                        calories = []
                        calories = np.array([float(0.0) if feed['field'+nfield] is None else float(feed['field'+nfield]) for feed in responseS['feeds']])
                        #print(calories)
                    
                    else:
                        scored = -2 
                        scorew = -2
                        calories = -2
                        return scored, scorew, calories

            scored = self.Score(StepsWeek, DurationWeek)
            scorew = self.ScoreWeek(StepsWeek, DurationWeek)

        else:
            scored = -1 
            scorew = -1
            calories = -1

        
        return scored, scorew, calories

# Main
def main():

    WC=WebClient()
    pdict = json.loads(json.dumps(WC.get_patients()))

    timewait = 300

    while True:
        pdict = json.loads(json.dumps(WC.get_patients()))
        # Every timewait update data to FitnessCatalog for all patient
        for pID in pdict.keys():
            PT = PatientTraining(pID)
            print(f"Score assessment for patient with ID {pID} and update info to catalog")
            scored, scorew, calories = PT.Data()
            # print(scored , scorew , calories)
            msg = {}
            msg["bn"] = 'Training'
            msg["e"] = []

            if scored == -1 and scorew == -1:
                msg["e"] = [
                        { 
                            "n" : 'No data',
                            "v" : scored,
                            "u" : None,
                            "t" : time.time()
                        }]

            elif scored == -2 and scorew == -2:
                msg["e"] = [
                        { 
                            "n" : 'No data',
                            "v" : scored,
                            "u" : None,
                            "t" : time.time()
                        }]
            
            else:        
                eDay = { 
                            "n" : 'scoreDay',
                            "v" : scored,
                            "u" : None,
                            "t" : time.time()
                        }
                
                eWeek = { 
                            "n" : 'scoreWeek',
                            "v" : scorew,
                            "u" : None,
                            "t" : time.time()
                        }
                
                if len(calories):            
                    cDay = { 
                                "n" : 'cloriesDay',
                                "v" : calories[-1],
                                "u" : "kcal",
                                "t" : time.time()
                            }
                    
                    cWeek = { 
                                "n" : 'cloriesWeek',
                                "v" : np.mean(calories[calories != 0]),
                                "u" : "kcal",
                                "t" : time.time()
                            }
                
                else:
                    cDay = { 
                                "n" : 'cloriesDay',
                                "v" : None,
                                "u" : "kcal",
                                "t" : time.time()
                            }
                    
                    cWeek = { 
                                "n" : 'cloriesWeek',
                                "v" : None,
                                "u" : "kcal",
                                "t" : time.time()
                            }
                
                msg["e"].append(eDay)
                msg["e"].append(eWeek)
                msg["e"].append(cDay)
                msg["e"].append(cWeek)
            
            WC.post_training(pID, msg) 	
        
            time.sleep(10)
        
        time.sleep(timewait) # Wait


if __name__ == '__main__':
    main()