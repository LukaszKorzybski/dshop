# -*- coding: utf-8 -*-
'''Dshop application main initialization module.'''

from dshop import settings as s

def legacyJDBCInit():
    '''
    Create JDBC DataSources and register under appropriate JNDI names.

    Use only when running djangoshop outsite Tomcat environment (jython shell or django webserver).
    Tomcat when used, is itself responsible for JNDI bindings.
    '''
    from org.springframework.mock.jndi import SimpleNamingContextBuilder
    from org.postgresql.ds import PGSimpleDataSource
    from net.sourceforge.jtds.jdbcx import JtdsDataSource

    # Making code changes in Django webserver environment results in python
    # modules being auto reloaded (this code is executed on each reload).
    # But the JVM, that we are running on, stays the same. In that case we don't
    # want to register JNDI Context again, cause it is already there.
    if not SimpleNamingContextBuilder.getCurrentContextBuilder():
        ds = PGSimpleDataSource()
        ds.setServerName(s.DATABASE_HOST)
        ds.setPortNumber(int(s.DATABASE_PORT) if s.DATABASE_PORT else 0)
        ds.setDatabaseName(s.DATABASE_NAME)
        ds.setUser(s.DATABASE_USER)
        ds.setPassword(s.DATABASE_PASSWORD)

        ds1 = JtdsDataSource()
        ds1.setServerName(s.WFMAG_DB_HOST)
        ds1.setDatabaseName(s.WFMAG_DB_NAME)
        ds1.setUser(s.WFMAG_DB_USER)
        ds1.setPassword(s.WFMAG_DB_PASSWORD)

        builder = SimpleNamingContextBuilder();
        builder.bind("java:comp/env/jdbc/perfektShop/main", ds);
        builder.bind("java:comp/env/jdbc/perfektShop/wfmag", ds1);
        builder.activate();

# Jython hotfix for Django
if s.JYTHON:
    import os
    os.getcwdu = os.getcwd

# Initialize dummy JNDI bindings for databases if running under JVM but not in Tomcat
if s.JYTHON and not s.TOMCAT:
    legacyJDBCInit()

# register online payment adapters
from dshop import dotpay
from dshop import paypal
from dshop.main import adapters
dotpay.payment_factories.append(adapters.getDotPayAdapterClass)
paypal.payment_factories.append(adapters.getPayPalAdapterClass)

# register custom admin filters
from dshop.main import admin_filters