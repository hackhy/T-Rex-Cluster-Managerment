from flask import Flask, request, make_response,redirect,current_app
import json
import time
import requests
import urllib3
 
app = Flask(__name__)
app.debug = True
 
 
@app.route('/', methods=['POST', 'GET'])
def main():
    return redirect('http://www.fuckyouspider.com')
 
 
@app.route('/up001', methods=['POST'])
def up():
    #data_list = []
    data = json.loads(request.get_data(as_text=True))   # request.get_data(as_text=True) ： 获取前端POST请求传过来的 json 数据
    #print(data)
    if(current_app.config.get('machineSataus') is None):
        current_app.config['machineSataus'] = {}

    machineSataus = current_app.config.get('machineSataus')
    machineSataus[data['machinename']]=data
    current_app.config['machineSataus']=machineSataus
    #print(current_app.config.get('machineSataus'))
    return '辛苦了'
    


@app.route('/show', methods=['GET'])
def show():
    machineSataus = current_app.config.get('machineSataus')
    #print(type(machineSataus))
    totalHashrate = 0
    totalHashrateDay = 0
    totalHashrateHour = 0
    totalHashrateMinute = 0
    totalGPU = 0
    totalMachine = 0
    totalAcceptedCount = 0
    totalRejectedCount = 0
    totalSolvedCount = 0
    realtotalHashrateHour = 0
    eachMachineStr = ''
    machineTableHead = '<table border=\"1\" cellspacing=\"0\" width=\"99%\" style=\"font-size:30px\"><tr ><th align=center>机器</th><th align=center>小时算力</th><th align=center>状态</th><th align=center>最近更新时间</th><th align=center>算力比重</th></tr>'
    machineTable = ''

    if (machineSataus is not None):
        for (key, value) in sorted(machineSataus.items()):
            realtotalHashrateHour += value['hashrate_hour']

    if(machineSataus is not None):
        for (key, value) in sorted(machineSataus.items()):
            #print(type(key),type(value)) #str,dict
            totalHashrate += value['hashrate']
            totalHashrateDay += value['hashrate_day']
            totalHashrateHour += value['hashrate_hour']
            totalHashrateMinute += value['hashrate_minute']
            totalGPU += value['gputotal']
            totalMachine += 1
            totalAcceptedCount += value['accepted_count']
            totalRejectedCount += value['rejected_count']
            totalSolvedCount += value['solved_count']

            timeleft = round(time.time() - value['ts'],1)
            timeleftstr = ''
            machineStatus = ''
            if(timeleft>100):
                timeleftstr = '<b><font color=\'red\'> %s</font></b>' %  timeleft
                machineStatus = '<b><font color=\'yellow\'> Delay</font></b>'
            else:
                timeleftstr = '<b><font color=\'green\'> %s</font></b>' % timeleft
                machineStatus = '<b><font color=\'green\'> Online</font></b>'                
                machineStatusCatFun(value['machinename'],0)
            if (timeleft > 600):
                machineStatus = '<b><font color=\'red\'> Offline</font></b>'
                print(value['machinename']+'掉线超过600秒')
                machineStatusCatFun(value['machinename'],2)

            eachMachineStr += '<br>机器名：%s，GPU数量：%s，延迟：%s ms，更新时间：%s，距今：%s 秒<br>平均算力：%s MH/s，平均日算力：%s MH/s，平均小时算力：%s MH/s，平均分鐘算力：%s MH/s<br>' %(value['machinename'],value['gputotal'],value['ping'],time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(value['ts'])),timeleftstr,round(value['hashrate']/1000000,2),round(value['hashrate_day']/1000000,2),round(value['hashrate_hour']/1000000,2),round(value['hashrate_minute']/1000000,2))

            if(value['hashrate_minute']<value['hashrate_hour']*0.5):
                machineStatusCatFun(value['machinename'],1)




            machinePercent = "%.2f%%" % (round(value['hashrate_hour']/realtotalHashrateHour*100,2))
            machineTable += '<tr><td align=center>%s</td><td align=center>%s MH/s</td><td align=center>%s</td><td align=center>%s 秒</td><td align=center>%s</td><tr>' % (value['machinename'],round(value['hashrate_hour']/1000000,2),machineStatus,timeleftstr,machinePercent)

            for eachGPU in value['gpuList']:
                eachGPUStr = 'GPU：%s，温度：%s，實時算力：%s MH/s，功率：%s W<br>'%(eachGPU['name'],eachGPU['temperature'],round(eachGPU['hashrate_instant']/1000000,2),eachGPU['power'])

                eachMachineStr = eachMachineStr + eachGPUStr


        totalSuccess = "%.2f%%" % (totalAcceptedCount/(totalAcceptedCount+totalRejectedCount+totalSolvedCount)*100)


        returnStr = '总机器：%s，总GPU：%s，总成功率%s  <input type=\"button\" value=\"刷新\" style=\"width:100px;height:60px;font-size:30px\" onclick=\"location.reload()\"> %s<br>平均算力：%s MH/s，平均日算力：%s MH/s，平均小时算力：%s MH/s<br><br>' % (totalMachine, totalGPU, totalSuccess, time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time())),round(totalHashrate/1000000,0), round(totalHashrateDay/1000000,0),round(totalHashrateMinute/1000000,0)) + machineTableHead + machineTable +'</table>'+eachMachineStr




        return returnStr
    else:
        return 'wait plz'


def sendMsg(msg):
    try:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        seesion = requests.Session()
        regurl = ''  #your msg server
        postData = '{\"msgtype\": \"text\",\"text\": {\"content\": \"'+msg+'\"}}'.encode('utf-8')
        headers = {"Content-Type":"application/json"}
        resultyyy = seesion.post(regurl, timeout=30,headers = headers ,data=postData, verify=False)  # ,proxies= proxies,verify=False
        print(resultyyy.text)

    except Exception as e:
        print(' error',e)



def machineStatusCatFun(machineName,status):#0：online ，1：hashrate_error ，2:offline upto 600s
    statusDict = {0:'online',1:'hashrate_error',2:'offline'}
    machineSatausCat = current_app.config.get('machineSatausCat')
    if(machineSatausCat is None):
        machineSatausCat = {}
    if(machineSatausCat.get(machineName) is None):
        machineSatausCat[machineName] = status
    else:
        if(machineSatausCat[machineName] != status):
            machineSatausCat[machineName] = status
            sendMsg(str(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time()))) + machineName + ' status is change to ' + str(status))
        
    current_app.config['machineSatausCat']=machineSatausCat


global machineDict
if __name__ == '__main__':
    #current_app.config['machineSataus']={}
    app.run(host='0.0.0.0',port=80)
