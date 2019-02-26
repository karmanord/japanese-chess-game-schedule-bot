import urllib.request
import urllib.parse
import json
import time

hist_url = "https://slack.com/api/channels.history"
delete_url = "https://slack.com/api/chat.delete"

token = '#'
channels = ['#']

def exec():
  for channel in channels:
    hist_params = {
      'channel' : channel,
      'token' : token
    }
    req = urllib.request.Request(hist_url)
    hist_params = urllib.parse.urlencode(hist_params).encode('ascii')
    req.data = hist_params

    res = urllib.request.urlopen(req)

    body = res.read()
    data = json.loads(body)
    print(data)
    for m in data['messages']:
        delete_params = {
            'channel' : channel,
            'token' : token,
            'ts' :  m["ts"]
        }
        req = urllib.request.Request(delete_url)
        delete_params = urllib.parse.urlencode(delete_params).encode('ascii')
        req.data = delete_params

        res = urllib.request.urlopen(req)
        body = res.read()

        time.sleep(1)