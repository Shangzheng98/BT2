# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
import xml.etree.ElementTree as ET
import csv
import time
import datetime
from datetime import date
import os
import threading

Routes = ['CAS', 'CRC', "HXP", "HWA", "HWB", "HDG", "TOM", "UMS",
          "CBD", "MSN", "MSS", "PHD", "PRB", "PRO", "MSA", "TTT", "UCB"]
date = date.today().strftime("%b-%d-%Y")

DAY_END = datetime.time(21, 0, 0)
DAY_START = datetime.time(7, 0)


class BtThread(threading.Thread):
    def __int__(self, threadID, routeName):
        threading.Thread.__init__(target=getBusInfo, args=(routeName, date,), group=None)
        self.threadId = threadID
        self.routeName = routeName
        print("this is thread ", self.threadId, routeName)
    # def run(self):
    #     print("this is thread ", self.threadId, routeName)
    #     getBusInfo(self.routeName)


class Stop:

    def __init__(self, stopCode, stopName):
        self.stopCode = stopCode
        self.stopName = stopName

    def toString(self):
        return str(self.stopCode) + ',' + self.stopName


def getStopInfo():
    csvFile = open("stopList.csv", "w+", newline='')
    csvWriter = csv.writer(csvFile)

    for e in Routes:
        StopNameResponse = requests.get(
            "http://www.bt4uclassic.org/webservices/bt4u_webservice.asmx/GetScheduledStopNames",
            "routeShortName=" + e)
        root = ET.fromstring(StopNameResponse.content)
        csvWriter.writerow([str(e)])
        for ele in root.iter("ScheduledStops"):
            stopName = ele.find("StopName").text
            stopCode = int(ele.find("StopCode").text)
            stop = Stop(stopCode, stopName)

            csvWriter.writerow([stop.stopCode, stop.stopName])


def sleep_time(hour, min, sec):
    return hour * 3600 + min * 60 + sec


def getBusInfo(routeName, date):
    print("this is route ", routeName)
    path = os.path.join('./', routeName)
    if not os.path.exists(routeName):
        os.mkdir(path)
    dataFile = open(path + "/" + routeName + "_" + date + "-rough" + ".csv", "w+", newline='')
    csvWriter = csv.writer(dataFile)
    csvWriter.writerow(
        ['routeName', 'bus ID', 'LastStopName', 'stopCode', 'IsTimePoint', 'latestEventTime',
         'number of passengers remaining',
         'percent of capacity'])
    counter = 0
    while 1:
        current_time = datetime.datetime.now().time()
        if current_time < DAY_START:
            continue
        if current_time > DAY_END:
            dataFile.close()
            break
        print("-----------", counter, "-----------")
        try:
            response = requests.post("http://www.bt4uclassic.org/webservices/bt4u_webservice.asmx/GetCurrentBusInfo")

            tree = ET.fromstring(response.content)

            for table in tree.iter('LatestInfoTable'):
                AgencyVehicleName = table.find('AgencyVehicleName').text
                ShortName = table.find('RouteShortName').text
                lastStopName = table.find('LastStopName').text
                stopCode = table.find('StopCode').text
                people = table.find('TotalCount').text
                isTimePoint = table.find('IsTimePoint').text
                latestEventTime = table.find('LatestEvent').text
                PercentOfCapacity = table.find('PercentOfCapacity').text
                if ShortName == routeName:
                    csvWriter.writerow(
                        [ShortName, AgencyVehicleName, lastStopName, stopCode, isTimePoint,
                         latestEventTime, people, PercentOfCapacity + "%"])
        except Exception as e:
            print("time", "exception:", e)
            continue

        counter = counter + 1
        time.sleep(sleep_time(0, 0, 20))
        # time.sleep(20)


if __name__ == '__main__':
    # getStopInfo()
    threadlist = []
    for i in range(len(Routes)):
        routeName = Routes[i]
        thread = threading.Thread(target=getBusInfo, args=(Routes[i], date,))
        thread.start()
        threadlist.append(thread)

    for thread in threadlist:
        thread.join()
