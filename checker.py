#!/usr/bin/python
from http.client import HTTPSConnection
import json
import time
from string import capwords
import os
from smtplib import SMTP_SSL

RECIPIENTS = ["vaccine@theschwartz.xyz"]

EMAIL_ADDRESS = "vaccine-notifier@theschwartz.xyz"
EMAIL_PASSWORD = "BadPassword!"

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
            ret.append(capwords(i["city"]))
    return (ret, timestamp)

def notify(conn, timestamp, openings):
    if len(openings) == 0:
        return
    print(f"Vaccines availible (updated at {timestamp}):")
    for city in openings:
        print(f"\t{city}")
    msg = f"Subject: MA Vaccine Openings\n\nUpdated at {timestamp}. Openings:"
    for city in openings:
        msg += f"\n    - {city}, Massachusetts"
    msg += "\n--------\nSchedule an appointment here: https://www.cvs.com/immunizations/covid-19-vaccine"
    for i in RECIPIENTS:
        conn.sendmail(EMAIL_ADDRESS, i, msg)

def main():
    smtp_conn = SMTP_SSL("mail.gandi.net", 465)
    smtp_conn.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    last_timestamp = ""
    while True:
        (openings, timestamp) = fetch_openings()
        if last_timestamp == timestamp:
            continue
        notify(smtp_conn, timestamp, openings)
        last_timestamp = timestamp
        time.sleep(15)

if __name__ == "__main__":
    main()
