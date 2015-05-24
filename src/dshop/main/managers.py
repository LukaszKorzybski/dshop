# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.db import connection, transaction

class SPageManager(models.Manager):
    def get_query_set(self):
      return super(SPageManager, self).get_query_set().filter(public=True)


class NewsManager(models.Manager):
    def get_query_set(self):
        return super(NewsManager, self).get_query_set().filter(public=True)


class NoMoreClientNumbers(Exception):
    pass

class ClientNumberManager(models.Manager):
    def get_next(self):
        nums = self.get_query_set().filter(available=True).order_by('?')[:1]
        if len(nums) == 0:
            raise NoMoreClientNumbers()
        return nums[0]


class CategoryManager(models.Manager):
    def main_categories(self):
        return self.get_query_set().filter(level=0)


class ProducerManager(models.Manager):
    def get_query_set(self):
        return super(ProducerManager, self).get_query_set().filter(public=True)

    def toplist(self):
        return self.get_query_set().filter(toplist=True)


class ShopArticleManager(models.Manager):
    def get_query_set(self):
        return super(ShopArticleManager, self).get_query_set().filter(public=True, producer__public=True)


class OrderManager(models.Manager):
    '''Default QuerySet returns only submitted orders. Use methods to get temporary orders.'''
    
    def get_query_set(self):
        return super(OrderManager, self).get_query_set().filter(submitted=True)

    def temp(self):
        '''Return orders which are not yet submitted.
           These orders are temporary because they are removed after specified time if not submitted.'''
        return  super(OrderManager, self).get_query_set().filter(submitted=False)

    def all_orders(self):
        return super(OrderManager, self).get_query_set()

    def get_next_number(self, submitted):
        '''Get next order number.
        
           Use submitted=True for submitted order number and False for orders that are
           being placed and are not yet submitted. Numeration of submitted and not submitted orders is independent.
           Temp order numbers are prefixed with "TEMP-".
        '''
        now = datetime.now()
        counter = 'orders-submitted' if submitted else 'orders-temp'
        cursor = connection.cursor()

        cursor.execute("SELECT value FROM main_counter WHERE name = %s FOR UPDATE", [counter])
        count = cursor.fetchone()[0]
        cursor.execute("UPDATE main_counter SET value = %s WHERE name = %s", [count+1, counter])
        transaction.commit_unless_managed()

        return u'%s%s%d%s/%s' % ('TEMP-' if not submitted else '', now.strftime('%U'),
                                count+1, now.strftime('%S'), now.strftime('%m'))


class ShipperManager(models.Manager):
    pass