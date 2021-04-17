#!/usr/bin/python3
from http.client import HTTPSConnection
import json
import time
from string import capwords
from smtplib import SMTP_SSL

RECIPIENTS = [
    "vaccine@theschwartz.xyz",
    "jorsch@gmail.com",
    "davidflodman1@verizon.net",
    "gmlaskowsk@gmail.com",
    #"akhilmibrahim@gmail.com",
]

SLEEP_SECONDS = 15
EMAIL_ADDRESS = "vaccine-notifier@theschwartz.xyz"
EMAIL_PASSWORD = "BadPassword!"

def fetch_openings():
    headers = {
        "Referer": "https://www.cvs.com/immunizations/covid-19-vaccine?icid=cvs-home-hero1-banner-1-link2-coronavirus-vaccine"
    }
    conn = HTTPSConnection("www.cvs.com")
    conn.request("GET", "/immunizations/covid-19-vaccine.vaccine-status.ma.json?vaccineinfo", headers=headers)
    res = conn.getresponse().read()
    conn.close()
    j = json.loads(res.decode("utf-8"))["responsePayloadData"]
    ret = []
    timestamp = j["currentTime"]
    for i in j["data"]["MA"]:
        if i["status"] != "Fully Booked":
            ret.append(capwords(i["city"]))
    return (ret, timestamp)

def notify(conn, timestamp, openings):
    if len(openings) == 0:
        return
    pretty_time = time.strftime("%I:%M %p").lstrip("0")
    msg = "Subject: MA Vaccine Openings\n\nOpenings as of %s:" % pretty_time
    for city in openings:
        msg += "\n    - %s, Massachusetts" % city
    msg += "\n--------\nSchedule an appointment here: https://www.cvs.com/immunizations/covid-19-vaccine (when you get to the page that asks for a zipcode/city, enter one of these^^ cities)"
    for i in RECIPIENTS:
        conn.sendmail(EMAIL_ADDRESS, i, msg)

def main():
    smtp_conn = SMTP_SSL("mail.gandi.net", 465)
    smtp_conn.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    last_timestamp = ""
    while True:
        (openings, timestamp) = fetch_openings()
        if last_timestamp == timestamp:
            time.sleep(SLEEP_SECONDS)
            continue
        notify(smtp_conn, timestamp, openings)
        last_timestamp = timestamp
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
