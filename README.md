# website_change_detection
Checks if a websites content changed. Then sends post request to a discord webhook endpoint.
Can be executed periodically using cronjob.

## Usage
1. Create a discord webhook
2. Create .env file and add webhook URL with key WEBHOOK_URL
3. Create monitor.json file and configure monitored websites

### Example Configs
.env file:
```sh
WEBHOOK_URL=https://canary.discord.com/api/webhooks/{id}/{token}
```

monitor.json file:
```json
[
    {
        "name": "Eschenlaube",
        "url": "https://eschenlaube.at/veranstaltungen",
        "html_class": "et_pb_row et_pb_row_1",
        "html_tag": "div"    
    },
    {
        "name": "Miles Jazz",
        "url": "https://www.milesjazz.at/",
        "html_class": "css-events-list",
        "html_tag": "div" 
    }
]
```

## Run
```sh
python3 main.py
```
