# -*- coding: utf-8 -*-

import sys
from decimal import Decimal
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import sql
from sqlalchemy import func
from sqlalchemy.sql import and_, or_, not_

from dshop import settings
from dshop.main import models as m

connurl = 'mssql+pyodbc://%s:%s@%s' % \
        (settings.WFMAG_DB_USER, settings.WFMAG_DB_PASSWORD, settings.WFMAG_DB_NAME)

class Foo(): pass
t = Foo()

def setup_tables(engine):
    meta = sa.MetaData()
    meta.bind = engine
    
    t.art = sa.Table('ARTYKUL', meta, autoload=True)
    t.ceny = sa.Table('CENA', meta, autoload=True)
    t.ceny_art = sa.Table('CENA_ARTYKULU', meta,
                        sa.Column('ID_CENY', sa.Numeric, sa.ForeignKey('CENA.ID_CENY'), primary_key=True),
                        sa.Column('ID_ARTYKULU', sa.Numeric, sa.ForeignKey('ARTYKUL.ID_ARTYKULU'), primary_key=True),
                        autoload=True)

    t.foo = sa.Table('foo', meta, sa.Column('id', sa.Integer, primary_key=True), sa.Column('name', sa.String), sa.Column('test', sa.Numeric));
    
    t.klienci = sa.Table('KONTRAHENT', meta, 
                        sa.Column('ID_KONTRAHENTA', sa.Numeric, primary_key=True),
                        autoload=True)

def init_db(connurl):
    '''Inicjuje SQL Alchemy i zwraca konstruktor obiektów Session.'''
    engine = sa.create_engine(connurl)
    setup_tables(engine)
    return engine
    #return orm.sessionmaker(bind=engine, autocommit=False)()

def enc(text):
    return text.encode('utf-8')

def encode_dict(d):
    for k,v in d.iteritems():
        if type(v) == unicode: d[k] = v.encode('utf-8')
    return d

def client_to_dict(c):
    d = {
        'NAZWA'             : (c.inverse_name() + u' (%s)' % c.client_num)[:50],
        'NAZWA_PELNA'       : c.name[:200],
        'NIP'               : c.nip[:30],
        'PLATNIK_VAT'       : 1 if c.is_company() else 0,
        'TERMIN_NALEZNOSCI' : c.payment_deadline,
        'TERMIN_ZOBOWIAZAN' : c.payment_deadline,
        'KOD_POCZTOWY'      : c.code[:20],
        'MIEJSCOWOSC'       : c.town[:50],
        'ULICA_LOKAL'       : (u'%s %s' % (c.street, c.number))[:50],
        'NIPL'              : c.nip[:30],
        'KTO_WPISAL'        : (u'sklep %s' % datetime.now().strftime('%d.%m.%Y %H:%M'))[:50],
        'ADRES_EMAIL'       : c.login[:100],
        'WYROZNIK'          : unicode(c.client_num)[:50],
        'ZGODA_NA_PRZETWARZANIE' : 1
    }
    return d

def insert_or_update_client(c, conn):
    '''Return id of new client if client has been added, None if was updated.'''
    client_defaults = {
        'ID_FIRMY'          : 1,
        'ID_PLATNIKA'       : 1,
        'ID_GRUPY'          : 6,
        'ID_KLASYFIKACJI'   : 1,
        'SYM_KRAJU'         : u"PL",
        'ODBIORCA'          : 1,
        'DOSTAWCA'          : 0,
        'FORMA_PLATNOSCI'   : u'gotówka',
        'PRIORYTET'         : 2,
        'FLAGA_STANU'       : 0,
        'DOMYSLNY_RABAT'    : 0,
        'BLOKOWANIE'        : 0,
        'SYM_KRAJU_KOR'     : u'PL',
        'DOKUMENT_TOZSAMOSCI_NAZWA' : u'Dowód osobisty'
    }

    def next_kod_kontrahenta():
        return conn.execute(sql.select([func.max(t.klienci.c.KOD_KONTRAHENTA)])).scalar() + 1
    def next_id_kontrahenta():
        return conn.execute(sql.select([func.max(t.klienci.c.ID_KONTRAHENTA)])).scalar() + 1

    values = client_to_dict(c)
    if c.stock_id:
        query = t.klienci.update().values(encode_dict(values)).where(t.klienci.c.ID_KONTRAHENTA==c.stock_id)
        res = conn.execute(query)
        return None
    else:
        values.update(client_defaults)
        values['ID_KONTRAHENTA'] = next_id_kontrahenta()
        values['KOD_KONTRAHENTA'] = next_kod_kontrahenta()
        query = t.klienci.insert().values(encode_dict(values))

        res = conn.execute(query)
        new_id = res.inserted_primary_key[0]
        conn.execute(t.klienci.update().values(ID_PLATNIKA=new_id).where(t.klienci.c.ID_KONTRAHENTA==new_id))
        return new_id
    
def sync_clients(conn):
    print "Syncing clients "
    i, j = 0, 0
    clients = m.Client.objects.filter(profile_complete=True, stock_id__isnull=False)
    for c in clients:
        insert_or_update_client(c, conn)
        i += 1
    print u'%d clients synchronized to WFMAG.' % i

def sync_articles(conn):
    print "Syncing articles "
    i, j = 0, 0
    articles = m.Article.objects.all()
    for a in articles:
        j += 1
        s = sql.select([t.art.c.STAN, t.art.c.VAT_SPRZEDAZY,
                        t.ceny_art.c.CENA_NETTO, t.ceny_art.c.CENA_BRUTTO,
                        t.art.c.CENA_ZAKUPU_NETTO, t.art.c.CENA_ZAKUPU_BRUTTO])
        s = s.select_from(t.art.join(t.ceny_art)).where(t.art.c.INDEKS_KATALOGOWY == enc(a.cat_index))\
                .where(t.ceny_art.c.ID_CENY==Decimal(settings.WFMAG_ID_CENY))
        res = conn.execute(s)
        data = res.fetchone()
        if data:
            a.stock_lvl = data[0].quantize(Decimal('1.0000'))
            a.vat = Decimal(data[1])
            a.net = data[2]
            a.gross = data[3]
            a.purchase_net = data[4]
            a.purchase_gross = data[5]
            a.save()
            i += 1
        res.close()
    print u'\nUpdated %d articles from WFMAG, total articles in shop: %d.' % (i, j)

# setup engine on module load
engine = init_db(connurl)

# can be used as shell script
if __name__ == "__main__":
    comm = sys.argv[1] if len(sys.argv) > 1 else 'sync'
    conn = engine.connect()

    if comm == "sync":
        sync_articles(conn)
        sync_clients(conn)
	
    elif comm == "shell":
        from IPython.Shell import IPShellEmbed
        ipshell = IPShellEmbed()
        ipshell(local_ns=locals())
	
    conn.close()
