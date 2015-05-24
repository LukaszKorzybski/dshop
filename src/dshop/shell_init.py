# -*- coding: utf-8 -*-
'''Dshop interactive python console initialization module. It is executed by dshop-shell.sh script.'''

# import usefull stuff
from decimal import Decimal

from django.db import connection as conn

from dshop.main import models as m
from dshop.main import managers as mgr
