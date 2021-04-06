# -*- coding: utf-8 -*-

import requests
import urllib3
import time
import sys
import json


class Services:

    global machinename,serverUrl

    def __init__(self):
        self.machinename = ''        
        self.serverUrl = ''

    def getJsonObj(self,jsonstr,obj):
        if(obj in jsonstr):
            return jsonstr[obj]
        else:
            return 'NoneInJson'


    def replacemh(self,o):
        if(o is None):
            return ''
        else:
            return str(o).replace('\'',' ').replace('\"',' ').replace('`',' ') + ' '

    def run(self,serverUrl,machinename):
        i = 1
        while(True):
            try:
                print(i, time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time())))
                i = i+1
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                seesion = requests.Session()
                info = {}
                regurl = 'http://127.0.0.1:4067/summary?last-stat-ts='+str(time.time())  #?page_size= &page= ,now max 400 per
              
                resultyyy = seesion.get(regurl, timeout=30, verify=False)  # ,proxies= proxies,verify=False
                resultyyy.encoding = 'utf-8'

                resultjson = json.loads(resultyyy.text)
                    

                info['machinename'] = machinename
                active_pool = self.getJsonObj(resultjson,'active_pool')
                info['ping'] = self.getJsonObj(active_pool,'ping')
                info['gputotal'] = self.getJsonObj(resultjson,'gpu_total')
                gpuList = []
                for gpu in self.getJsonObj(resultjson,'gpus'):                    
                    gpuobj = {}
                    gpuobj['hashrate'] = gpu['hashrate']
                    gpuobj['hashrate_day'] = gpu['hashrate_day']
                    gpuobj['hashrate_hour'] = gpu['hashrate_hour']
                    gpuobj['hashrate_instant'] = gpu['hashrate_instant']
                    gpuobj['hashrate_minute'] = gpu['hashrate_minute']
                    gpuobj['name'] = gpu['name']
                    gpuobj['power'] = gpu['power']
                    gpuobj['temperature'] = gpu['temperature']
                    gpuList.append(gpuobj)
                    #print(0,gpuList)
                    
                #print(gpuList)    
                info['gpuList'] = gpuList
                info['hashrate'] = self.getJsonObj(resultjson,'hashrate')
                info['hashrate_day'] = self.getJsonObj(resultjson,'hashrate_day')
                info['hashrate_hour'] = self.getJsonObj(resultjson,'hashrate_hour')
                info['hashrate_minute'] = self.getJsonObj(resultjson,'hashrate_minute')
                info['ts'] = self.getJsonObj(resultjson,'ts')
                info['accepted_count'] = self.getJsonObj(resultjson,'accepted_count')
                info['rejected_count'] = self.getJsonObj(resultjson,'rejected_count')         
                info['solved_count'] = self.getJsonObj(resultjson,'solved_count') 
                info['record_time'] = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))
                

                postData = json.dumps(info)
                resultyyy = seesion.post(serverUrl+'/up001', data=postData, timeout=30)  # ,proxies= proxies,verify=False
                resultyyy.encoding = 'utf-8'
                print(resultyyy.text)

                
                time.sleep(60)
            

            except Exception as e:
                print(' error',e)
 


    
    

    

servicesIns = Services()
servicesIns.run(sys.argv[1],sys.argv[2])


