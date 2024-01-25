# -*- coding: utf-8 -*-
from fastapi import Depends, FastAPI, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware
import uvicorn
import requests
import json
import xmltodict
from datetime import *


def getyj(jb, lx):
    url = "http://fabu.12379.cn/WarningShareV3/WarnService"
    body = "<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>" \
              "<soap:Header>" \
                "<authHeader>" \
                 " <username>jyb_center_user</username>" \
                  "<password>RDoavgi6ApU0PWSH</password>" \
                "</authHeader>" \
              "</soap:Header>" \
              "<soap:Body>" \
                "<ns1:listWarnCapByTime xmlns:ns1='http://service.warning.pmsc.com/'>" \
                  "<startTime>20210401165500</startTime>" \
               " </ns1:listWarnCapByTime>" \
              "</soap:Body>" \
            "</soap:Envelope>"

    r = requests.post(url, data=body.encode("utf-8"), headers={'Content-Type': 'text/xml;charset=utf-8'})
    xmlres = r.content.decode("utf-8")
    parser_data = xmltodict.parse(xmlres[xmlres.index("<soap:Envelope"):xmlres.index("</soap:Envelope>")+16])
    json_res = json.loads(json.dumps(parser_data, ensure_ascii=False))["soap:Envelope"]["soap:Body"]["ns2:listWarnCapByTimeResponse"]["return"]
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.0")    #当前时间
    # bjtime =  datetime.now() + timedelta(days=-1)
    # time24hago = datetime.strftime(bjtime, "%Y-%m-%d %H:%M:%S.0")
    restemp = []
    # print(json_res)
    for each in json_res:
        if each["eventType"] in lx:   # 暴雨、台风、干旱、沙尘暴
            if nowtime < each['expires']:   # 未到失效时间
                restemp.append(each)
    res = []
    for eachyj in restemp:
        flag = 0
        for otheryj in restemp:
            if eachyj['msgType'] == 'Cancel':   #本条是取消
                flag = 1
                break
            if eachyj['msgType'] != 'Cancel' and otheryj['msgType'] == 'Cancel':    #本条不是取消，其他是取消
                if eachyj['identifier'][0:6] == otheryj['identifier'][0:6]: #同单位
                    if eachyj['eventType'] == otheryj['eventType']: #同类型
                        if eachyj['effective'] < otheryj['effective']:  #取消比本条晚发
                            flag = 1
                            break
        if flag == 0 and eachyj['severity'] in jb:
            eachyj['areaCode'] = eachyj['identifier'][0:6]
            res.append(eachyj)
    return res


def getyjexcept(jb, lx):
    url = "http://fabu.12379.cn/WarningShareV3/WarnService"
    body = "<soap:Envelope xmlns:soap='http://schemas.xmlsoap.org/soap/envelope/'>" \
              "<soap:Header>" \
                "<authHeader>" \
                 " <username>jyb_center_user</username>" \
                  "<password>RDoavgi6ApU0PWSH</password>" \
                "</authHeader>" \
              "</soap:Header>" \
              "<soap:Body>" \
                "<ns1:listWarnCapByTime xmlns:ns1='http://service.warning.pmsc.com/'>" \
                  "<startTime>20210401165500</startTime>" \
               " </ns1:listWarnCapByTime>" \
              "</soap:Body>" \
            "</soap:Envelope>"

    r = requests.post(url, data=body.encode("utf-8"), headers={'Content-Type': 'text/xml;charset=utf-8'})
    xmlres = r.content.decode("utf-8")
    parser_data = xmltodict.parse(xmlres[xmlres.index("<soap:Envelope"):xmlres.index("</soap:Envelope>")+16])
    json_res = json.loads(json.dumps(parser_data, ensure_ascii=False))["soap:Envelope"]["soap:Body"]["ns2:listWarnCapByTimeResponse"]["return"]

    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S.0")    #当前时间
    # bjtime =  datetime.now() + timedelta(days=-1)
    # time24hago = datetime.strftime(bjtime, "%Y-%m-%d %H:%M:%S.0")
    restemp = []
    # print(json_res)
    for each in json_res:
        if each["eventType"] not in lx:   # 暴雨、台风、干旱、沙尘暴
            if nowtime < each['expires']:   # 未到失效时间
                restemp.append(each)
    res = []
    for eachyj in restemp:
        flag = 0
        for otheryj in restemp:
            if eachyj['msgType'] == 'Cancel':   #本条是取消
                flag = 1
                break
            if eachyj['msgType'] != 'Cancel' and otheryj['msgType'] == 'Cancel':    #本条不是取消，其他是取消
                if eachyj['identifier'][0:6] == otheryj['identifier'][0:6]: #同单位
                    if eachyj['eventType'] == otheryj['eventType']: #同类型
                        if eachyj['effective'] < otheryj['effective']:  #取消比本条晚发
                            flag = 1
                            break
        if flag == 0 and eachyj['severity'] in jb:
            eachyj['areaCode'] = eachyj['identifier'][0:6]
            res.append(eachyj)
    return res


app = FastAPI()
origins = [
    "http://10.27.28.139",
    "http://10.27.28.139:8000",
    "http://10.30.16.156:40054",
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8888",
]

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/xintiao')
def xt():
    return "true"


@app.get('/effectiveEarlyWarnings')
def geteffectiveEarlyWarnings():
    return getyj(jb=['orange', 'red'], lx=["11B01", "11B03", "11B07", "11B22"])


@app.get('/effectiveEarlyWarningsMin')
def geteffectiveEarlyWarningsMin():
    ori = getyj(jb=['orange', 'red'], lx=["11B01", "11B03", "11B07", "11B22"])
    res = []
    for each in ori:
        res.append({
            'eventType': each['eventType'],
            'eventType_CN': each['eventType_CN'],
            'areaCode': each['areaCode'],
            'severity': each['severity']
        })
    return res


@app.get('/effectiveAllEarlyWarnings')
def geteffectiveAllEarlyWarnings():
    return getyjexcept(jb=['blue', 'yellow', 'orange', 'red'], lx=[])


@app.get('/effectiveAllEarlyWarningsMin')
def geteffectiveAllEarlyWarningsMin():
    ori = getyj(jb=['blue', 'yellow', 'orange', 'red'], lx=["11B01", "11B03", "11B07", "11B22"])
    res = []
    for each in ori:
        res.append({
            'eventType': each['eventType'],
            'eventType_CN': each['eventType_CN'],
            'areaCode': each['areaCode'],
            'severity': each['severity']
        })
    return res


@app.get('/effectiveAllEarlyWarningsMin')
def geteffectiveAllEarlyWarningsMin():
    ori = getyj(jb=['blue', 'yellow', 'orange', 'red'], lx=["11B01", "11B03", "11B07", "11B22"])
    res = []
    for each in ori:
        res.append({
            'eventType': each['eventType'],
            'eventType_CN': each['eventType_CN'],
            'areaCode': each['areaCode'],
            'severity': each['severity']
        })
    return res




if __name__ == '__main__':
    print(geteffectiveAllEarlyWarnings())
