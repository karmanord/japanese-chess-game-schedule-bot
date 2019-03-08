#!/usr/bin/env python
# -*- coding: utf-8 -*-
from main import main
from base64 import b64decode

def lambda_handler(event, context):
  main()