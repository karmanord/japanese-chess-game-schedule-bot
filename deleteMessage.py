#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import boto3
from base64 import b64decode
import urllib.request
import urllib.parse
import json
import time

hist_url = "https://slack.com/api/channels.history"
delete_url = "https://slack.com/api/chat.delete"

token = boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['token']))['Plaintext']
channels = [
            boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['game_info_channel']))['Plaintext'],
            boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ['images_channel']))['Plaintext']
           ]

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