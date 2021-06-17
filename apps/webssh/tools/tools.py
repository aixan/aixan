#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : HuYuan
# @File    : tools.py

import time
import random
import hashlib


def unique():
    ctime = str(time.time())
    salt = str(random.random())
    m = hashlib.md5(bytes(salt, encoding='utf-8'))
    m.update(bytes(ctime, encoding='utf-8'))
    return m.hexdigest()
