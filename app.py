from flask import Flask, render_template, url_for, request, jsonify
from bs4 import BeautifulSoup
import requests
import urllib.parse
from datetime import datetime, timedelta
import re

bus_find_list = ("rtnm", "adirection", "stationnm1")
corona_find_list = ("decidecnt", "clearcnt", "deathcnt")

def set_bus_information(id_list):
    global bus_list
    bus_list = []
    for id in id_list:
        list_2 = []
        bus_requests = return_parse("http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid?ServiceKey=vd%2B2nNyF4R6cKQheiYx%2FnBKf3jBbnCburz0CpVI6lma62eC7DKIiVCvnIP8geQzI3muGUuDjvcWrKCKzrzyQhw%3D%3D&arsId={}".format(id), "lxml")
        for bus in bus_requests.find_all("itemlist"):
            list_1 = []
            try:
                if not bus.find("arrmsg1").text == "운행종료":
                    for find in bus_find_list:
                        list_1.append(bus.find(find).text)
                    if bus.find("arrmsg1").text == "곧 도착":
                        
                        list_1.append("곧 도착")
                    else:
                        list_1.append(bus.find("arrmsg1").text.split("분")[0] + "분")
                    list_1.append(id)
                    if list_1[0].isdigit():
                        if int(list_1[0]) < 10000 and  int(list_1[0]) > 1001:
                            list_1.append(2)
                        elif int(list_1[0]) <= 1000 and int(list_1[0]) > 100:
                            list_1.append(1)
                    else:
                        int_bus = int(re.findall('\d+', list_1[0])[0]) 
                        if int_bus >= 1000 and int_bus < 10000:
                            list_1.append(3)
                        elif int_bus <= 1000 and int_bus > 100:
                            list_1.append(1)
                        elif int_bus < 100:
                            list_1.append(2)
                        else:
                            list_1.append(4)
                    list_2.append(list_1)
                    # 1파랑, 2초록, 3빨강, 4노랑
            except:
                pass
        bus_list.append(list_2)

def bus_id_list(station):
    id_list = []
    bus_id_parse = return_parse("http://ws.bus.go.kr/api/rest/stationinfo/getStationByName?ServiceKey=qU6ZiWZWr9TyzBf4CSQePVRrLv656KwyxySrnDDH4o9I71HOfECubfmhWxHeIYMyg6X9yLyogSFQV0ucd9gFpA%3D%3D&stSrch={}".format(urllib.parse.quote_plus(station)) ,"lxml-xml")
    for bus in bus_id_parse.find_all("itemList"):
        if bus.find("stNm").text == station:
            id_list.append(int(bus.find("arsId").text))
    return id_list

def return_parse(url, type):
    return BeautifulSoup(requests.get(url).text.encode('utf-8'), type)
    
def return_corona_data():
    now = datetime.now()
    if int(now.strftime("%H")) < 11:
        now = now + timedelta(days=-1)
    yesterday = now + timedelta(days=-1)
    corona_data = []
    
    now = now.strftime("%Y%m%d")
    yesterday = yesterday.strftime("%Y%m%d")

    corona_response_parse = return_parse("http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey=qU6ZiWZWr9TyzBf4CSQePVRrLv656KwyxySrnDDH4o9I71HOfECubfmhWxHeIYMyg6X9yLyogSFQV0ucd9gFpA%3D%3D&pageNo=1&numOfRows=10&startCreateDt={}&endCreateDt={}".format(now, now), 'lxml')
    print("http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey=qU6ZiWZWr9TyzBf4CSQePVRrLv656KwyxySrnDDH4o9I71HOfECubfmhWxHeIYMyg6X9yLyogSFQV0ucd9gFpA%3D%3D&pageNo=1&numOfRows=10&startCreateDt={}&endCreateDt={}".format(now, now))
    
    for find in corona_find_list:
        corona_data.append(corona_response_parse.find(find).text)

    corona_data.append(int(corona_data[0]) - int(return_parse("http://openapi.data.go.kr/openapi/service/rest/Covid19/getCovid19InfStateJson?serviceKey=qU6ZiWZWr9TyzBf4CSQePVRrLv656KwyxySrnDDH4o9I71HOfECubfmhWxHeIYMyg6X9yLyogSFQV0ucd9gFpA%3D%3D&pageNo=1&numOfRows=10&startCreateDt={}&endCreateDt={}".format(yesterday ,yesterday), 'lxml').find("decidecnt").text))

        
    return corona_data

app = Flask(__name__)

@app.route('/')

def main(): 
    global bus_list 
    station = request.args.get('station')
    if not station == None or station == "": 
        set_bus_information(bus_id_list(station))
    else:
        bus_list = []

    return render_template('main.html', title=station,  bus_data = bus_list, corona_data = return_corona_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6565)
