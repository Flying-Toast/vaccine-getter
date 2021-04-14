#!/usr/bin/python
from http.client import HTTPSConnection
import json
import time
from string import capwords
import os

def fetch_openings():
    headers = {
        "Referer": "https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-banner-1-link2-coronavirus-vaccine"
    }
    conn = HTTPSConnection("www.cvs.com")
    conn.request("GET", "/immunizations/covid-19-vaccine.vaccine-status.ma.json?vaccineinfo", headers=headers)
    res = conn.getresponse().read()
    j = json.loads(res.decode("utf-8"))["responsePayloadData"]
    ret = []
    timestamp = j["currentTime"].split("T")[1].split(":")[:-1]
    [hour, minute] = map(int, timestamp)
    hour -= 9
    timestamp = f"{hour}:{str(minute).zfill(2)}"
    for i in j["data"]["MA"]:
        if i["status"] != "Fully Booked":
            ret.append(i["city"])
    return (ret, timestamp)

def beep():
    os.system("cvlc --play-and-exit /usr/share/sounds/freedesktop/stereo/complete.oga")

def main():
    last_timestamp = ""
    while True:
        (openings, timestamp) = fetch_openings()
        if last_timestamp == timestamp:
            continue
        print(f"Updated at {timestamp}. Openings:")
        if len(openings) == 0:
            print("\tNo openings")
        else:
            beep()
            for i in openings:
                print(f"\t{i.city}")
        last_timestamp = timestamp
        time.sleep(15)

if __name__ == "__main__":
    main()
