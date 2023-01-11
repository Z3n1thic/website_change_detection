from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import requests
import json
import os
import dotenv

webhook_url = dotenv.get_key('.env', 'WEBHOOK_URL')
if webhook_url == None:
    exit()

def get_comp(url, html_class, html_tag="div"):
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    return re.sub(r'\n{2,}', "\n", soup.find(html_tag, class_=html_class).get_text())

def compare_and_notify(url, html_class, html_tag, name):
    comp_file_name = "comp/"+name+".comp"
    try:
        with open(comp_file_name, 'r') as comp:
            out = get_comp(url=url, html_class=html_class, html_tag=html_tag)

            if out != comp.read():
                print('new event')
                comp.close()
                with open(comp_file_name, 'w') as comp:
                    comp.write(out)
                    requests.post(webhook_url, json={"content": f"Hey, there could be a new event at {url} ! Have a look!"})

    except IOError as e:
        out = get_comp(url=url, html_class=html_class, html_tag=html_tag)
        try:
            with open(comp_file_name, 'w') as comp:
                comp.write(out)
        except IOError as e:
            os.mkdir("comp")
            with open(comp_file_name, 'w') as comp:
                comp.write(out)

if __name__ == '__main__':
    with open('monitor.json') as f:
        monitorlist = json.load(f)

        for monitor in monitorlist:
            compare_and_notify(url=monitor['url'], html_class=monitor['html_class'], html_tag=monitor['html_tag'], name=monitor['name'])