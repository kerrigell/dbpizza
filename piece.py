#!/usr/bin/env python
#coding:utf-8
# Author:   Haiyang Peng
# Purpose:
# Created: 2013/7/02

from dbi import t_server
from dbi import session
from node import Server

class piece(Server):
    pass

class knife(object):
    self.words = self._all_word()
    def __init__(self,*keywords):
       pass

    def _all_words(sefl):
        words = []
        words += self._get_word(t_server.region)
        words += self._get_word(t_server.product)
        words += self._get_word(t_server.role)
        words += self._get_word(t_server.dbms)
        words += self._get_word(t_server.vender)
        words += self._get_word(t_server.os_type)
        words += self._get_word(t_server.os_release)
        words += self._get_word(t_server.os_arch)
        words += 'reserve'

    def _get_word(self, col):
        ret = session.query(col).distinct().all()
        return [ str(x[0]) for x in ret ]

    def __str__(self):
        print self.words






