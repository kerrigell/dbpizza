#!/usr/bin/env python
#coding:utf-8
# Author:  Jianpo Ma
# Purpose: 
# Created: 2013/3/29

import sqlobject
from sqlobject.mysql import builder
conn=builder()(user='root', password='',host='127.0.0.1',db='dbpizza')