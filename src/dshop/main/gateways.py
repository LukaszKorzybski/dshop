# -*- coding: utf-8 -*-

from dshop import settings

class EmailGateway(object):
    def __init__(self):
        pass
    def send(self, email):
         email.send()

email = EmailGateway()