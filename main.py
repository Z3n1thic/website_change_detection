from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import requests
import json
import os
import dotenv
import xxhash

real_path = os.path.realpath(os.path.dirname(__file__))
webhook_url = dotenv.get_key(real_path+'/.env', 'WEBHOOK_URL')
if webhook_url == None:
    exit()

def remove_excessive_newlines(text):
    return re.sub(r'\n{2,}', "\n", text).replace("\r", "") # remove excessive newlines and carriage returns

def get_comp(url, html_class="", html_tag="div", html_id=""):
    page = urlopen(url)
    html = page.read().decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")
    args = {}
    if (html_class != None and html_class.strip() != ""):
        args['class_'] = html_class
    if (html_id != None and html_id.strip() != ""):
        args['id'] = html_id
        
    return remove_excessive_newlines(soup.find(html_tag, **args).get_text())

def compare_and_notify(url, html_class, html_tag, name, html_id):
    comp_file_name = real_path+"/comp/"+name+".comp"
    hash = xxhash.xxh3_128(get_comp(url=url, html_class=html_class, html_tag=html_tag, html_id=html_id)).hexdigest()
    try:
        with open(comp_file_name, 'r') as comp:
            compare_hash = comp.read()
            if hash != compare_hash.strip():
                print('new event')
                comp.close()
                with open(comp_file_name, 'w') as comp:
                    comp.write(hash)
                    requests.post(webhook_url, json={"content": f"Hey, there could be a new event at {url} ! Have a look!"})

    except IOError as e:
        try:
            with open(comp_file_name, 'w') as comp:
                comp.write(hash)
        except IOError as e:
            os.mkdir(real_path+"/comp/")
            with open(comp_file_name, 'w') as comp:
                comp.write(hash)

if __name__ == '__main__':
    with open(real_path+'/monitor.json') as f:
        monitorlist = json.load(f)

        for monitor in monitorlist:
            compare_and_notify(url=monitor['url'], html_class=monitor['html_class'], html_tag=monitor['html_tag'], name=monitor['name'], html_id=monitor['html_id'])