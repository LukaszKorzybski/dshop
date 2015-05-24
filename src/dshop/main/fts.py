# -*- coding: utf-8 -*-

from datetime import datetime
import time

import sphinxapi as spx

from dshop import settings
from dshop.main import models as m

ARTICLES_INDEX = 'dshop-%s-articles' % settings.SHOP_ID


class Sort(object):
    WEIGHT  = 0
    NAME    = 1
    PRICE   = 2
    CREATED = 3


class GroupTreeItem(object):
    def __init__(self, id, count=0, name='', children=None):
        self.id = id
        self.count = count
        self.group = None
        self.children = children if children else {}
    
    def children_by_count(self):
        '''Children groups sorted by count.'''
        return sorted(self.children.itervalues(), lambda x,y: cmp(x.count, y.count), reverse=True)

    def children_by_name(self):
        '''Children groups sorted by name.'''
        return sorted(self.children.itervalues(), lambda x,y: cmp(x.group.name, y.group.name))
    
    def all_descendants_dict(self, dic):
        '''Populate dictionary dic with all descendants dumped to dict (to_dict() is used).'''
        for g in self.children.itervalues():
            dic[g.id] = g.to_dict()
            g.all_descendants(dic)
    
    def to_dict(self):
        '''Dump base attributes to dictionary.'''
        return { 'id' : self.id, 'count' : self.count }

    def debug_print(self, level=0):
        print '%s%s' % ('   '*level, self)
        for g in self.children_by_count():
            g.debug_print(level+1)

    def __unicode__(self):
        return u'<GroupTreeItem: (%s, %s)>' % (self.id, self.count)

    def __repr__(self):
        return self.__unicode__().encode('utf-8')

    def __eq__(self, other):
        return True if self.id == other.id else False

    def __ne__(self, other):
        return not self.__eq__(other)


class GroupTree(GroupTreeItem):
    def __init__(self, group_id=None):
        super(GroupTree, self).__init__(group_id)

    @property
    def is_empty(self):
        return False if self.children else True

    def from_articles(self, fts_articles, level=20):
        '''Build tree from given full-text search articles result set or from postgresql articles result set.
           The only difference is in fts_articles structure, which we handle here.
        '''
        if not fts_articles:
            return

        tmpl_lids = fts_articles[0]['attrs']['categories'] if 'attrs' in fts_articles[0] else fts_articles[0]['r_category_path']
        group_idx = m.Category.leveled_to_ids(tmpl_lids).index(self.id) if self.id else -1
        
        for art in fts_articles:
            lids = art['attrs']['categories'] if 'attrs' in art else art['r_category_path']
            self._inc_article_count(self, m.Category.leveled_to_ids(lids), group_idx, level)

        groups = m.Category.objects.filter(id__in=[g.id for g in self.children.itervalues()])
        for g in groups:
            self.children[g.id].group = g

    def as_dict(self):
        d = {}
        for g in self.children:
            g.all_descendants_dict(d)

        groups = m.Category.filter(id__in=[g.id for g in self.children.itervalues()])
        for g in groups:
            self.children[g.id].group = g
    
    def _inc_article_count(self, gtitem, groups, idx, level):
        '''Build tree top-down and increment articles count for subgroup of given gtitem.'''
        if level <= 0 or idx+1 >= len(groups):
            return

        gid = groups[idx+1]
        subgroup = gtitem.children.get(gid, None)
        if not subgroup:
            subgroup = GroupTreeItem(gid)
            gtitem.children[gid] = subgroup

        subgroup.count += 1
        self._inc_article_count(subgroup, groups, idx+1, level-1)


class Page(object):
    def __init__(self, items=None, total_items=0, page_num=1, sort=Sort.WEIGHT):
        self.items = items if items else []
        self.total_items = total_items
        self.page_num = page_num
        self.sort = sort
    @property
    def total_pages(self):
        return (self.total_items / settings.PAGE_SIZE) + 1
    @property
    def items_from(self):
        return ((self.page_num-1) * settings.PAGE_SIZE) + 1
    @property
    def items_to(self):
        return self.page_num * settings.PAGE_SIZE if self.page_num < self.total_pages else self.total_pages
    @property
    def next(self):
        return self.page_num + 1 if self.page_num < self.total_pages else None
    @property
    def prev(self):
        return self.page_num - 1 if self.page_num > 1 else None
    @property
    def next_pages(self):
        return range(self.page_num+1, min(self.total_pages, self.page_num+4)) if self.page_num < self.total_pages-1 else []
    @property
    def prev_pages(self):
        return range(max(2,self.page_num-3), self.page_num) if self.page_num > 2 else []
    @property
    def onepage(self):
        return True if self.total_pages == 1 else False


def sph_match_articles(phrase, filters, limit):
    '''Sphinx backend for searching articles.'''
    cl = spx.SphinxClient()
    cl.SetServer(settings.SPHINX_HOST, settings.SPHINX_PORT)
    cl.SetRetries(2, 50)
    cl.SetFieldWeights({ 'name' : 12, 'producer' : 12, 'desc' : 3 })
    cl.SetLimits(0, limit, limit)

    if phrase:
        cl.SetMatchMode(spx.SPH_MATCH_EXTENDED2)

    for f in filters:
        if type(f[1]) == int:
            cl.SetFilter(f[0], [f[1]])
        else:
            cl.SetFilter(f[0], f[1])

    res = cl.Query(phrase, ARTICLES_INDEX)
    if res:
        return res
    else:
        raise RuntimeError(cl.GetLastError())


def get_articles(qs, group=None, page=1, sort='name', tree_levels=20):
    if group:
        qs = qs.filter(r_category_path__startswith=group.r_lid_path)

    match = list(qs.order_by(sort).values('id', 'r_category_path'))

    ids = [a['id'] for a in match][(page-1)*settings.PAGE_SIZE : page*settings.PAGE_SIZE]
    articles = m.ShopArticle.publics.filter(id__in=ids)\
            .select_related('article__promotion', 'producer', 'r_main_photo').defer('desc').order_by(sort)
    
    page = Page(articles, len(match), page)

    if articles:
        gtree = GroupTree(group.id if group else None)
        gtree.from_articles(match, tree_levels)
    else:
        gtree = None
    
    return ( page, gtree )
    

def search_articles(phrase="", filters=[], group=None, page=1, tree_levels=20):
    '''Find articles using full-text search and/or filters functionality.'''
    ft = list(filters)
    if group:
        ft.append(('categories', group.leveled_id()))
    res = sph_match_articles(phrase, ft, 2000)

    ids = [a['id'] for a in res['matches']][(page-1)*settings.PAGE_SIZE : page*settings.PAGE_SIZE]
    articles = m.sort_by_list(
        m.ShopArticle.publics.filter(id__in=ids).select_related('article__promotion', 'producer', 'r_main_photo').defer('desc'), ids
    )

    page = Page(articles, res['total'], page)
    if articles:
        gtree = GroupTree(group.id if group else None)
        gtree.from_articles(res['matches'], tree_levels)
    else:
        gtree = None
    
    return ( page, gtree )