from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import requests
import json
import os
import dotenv
import hashlib
import datetime
import typing

real_path = os.path.realpath(os.path.dirname(__file__))
webhook_url = dotenv.get_key(real_path + "/.env", "WEBHOOK_URL")
if webhook_url == None:
    exit()


def remove_excessive_newlines(text):
    return re.sub(r"\n{2,}", "\n", text).replace(
        "\r", ""
    )  # remove excessive newlines and carriage returns


def get_comp(url, html_class="", html_tag="div", html_id=""):
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    args = {}
    if html_class != None and html_class.strip() != "":
        args["class_"] = html_class
    if html_id != None and html_id.strip() != "":
        args["id"] = html_id

    return remove_excessive_newlines(soup.find(html_tag, **args).get_text())


def compare_and_notify(url, html_class, html_tag, name, html_id, checks):
    out = get_comp(url=url, html_class=html_class, html_tag=html_tag, html_id=html_id)
    newhash = hashlib.sha256(out.strip().encode("UTF-8")).hexdigest()
    if newhash != checks[name]["hash"]:
        print("new event")
        requests.post(
            webhook_url,
            json={
                "content": f"Hey, there could be a new event at {url} ! Have a look!"
            },
        )
        checks[name]["hash"] = newhash
        with open(
            "checks.json", "w"
        ) as f:  # This not ideal because it results in a lot of disk writes
            json.dump(checks, f)
    else:
        print(name + " is up to date")


if __name__ == "__main__":
    with open(real_path + "/monitor.json") as f:
        monitorlist = json.load(f)
    try:
        with open("checks.json", "r") as f:
            checks = json.load(f)
    except FileNotFoundError:
        checks = {}
        for monitor in monitorlist:
            data = get_comp(
                monitor["url"],
                monitor.get("html_class"),
                monitor.get("html_tag"),
                monitor.get("html_id"),
            )
            checks[monitor["name"]] = {
                "hash": hashlib.sha256(data.strip().encode("UTF-8")).hexdigest(),
                "lastupdated": datetime.datetime.now().isoformat(),
            }
        with open("checks.json", "w") as f:
            json.dump(checks, f)
        exit()

    for monitor in monitorlist:
        # Check if monitor is in checks and add if it isn't
        if monitor["name"] not in checks:
            print(monitor["name"] + "not in checks")
            data = get_comp(
                monitor["url"],
                monitor.get("html_class"),
                monitor.get("html_tag"),
                monitor.get("html_id"),
            )
            checks[monitor["name"]] = {
                "hash": hashlib.sha256(data.strip().encode("UTF-8")).hexdigest(),
                "lastupdated": datetime.datetime.now().isoformat(),
            }
            with open("checks.json", "w") as f:
                json.dump(checks, f)
            continue

        compare_and_notify(
            url=monitor["url"],
            html_class=monitor.get("html_class"),
            html_tag=monitor.get("html_tag"),
            name=monitor["name"],
            html_id=monitor.get("html_id"),
            checks=checks,
        )
