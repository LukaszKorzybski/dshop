# -*- coding: utf-8 -*-

from os import path, getenv
import random
import subprocess
import decimal
from decimal import Decimal

from dshop import settings

def money(dec):
    return dec.quantize(Decimal('1.00'), rounding=decimal.ROUND_HALF_UP)

def consoleToolInit(smodule):
    '''Init function for dshop console tools written in python.'''
    if not getenv('DSHOP_ENV_SET', None):
        sys.exit("DSHOP_ENV_SET not set. Please set enviroment first!")
    loadEnvSettings(smodule)

def distribute_filepath(fpath, position=0, dirs=30):
    '''Randolmy distribute given file path across 2-level tree of directories.
        @param position - position in the fpath, starting from top (0), at which tree will be inserted
        @return distributed file path
    '''
    tab = fpath.split('/')
    assert len(tab) > 0
    assert position < len(tab)

    if fpath.startswith('/'):
        position += 1

    a = random.randint(0,dirs-1)
    b = random.randint(0,dirs-1)
    npath = tab[0:position] + [str(a),str(b)] + tab[position:]
    return '/'.join(npath)

def version_filename(fpath):
    '''Version file name in a given file path so that the file name is unique in it's directory.
       @param fpath absolute path to the file
       @return versioned filename with absolute path
    '''
    if not path.exists(fpath):
        return fpath

    (head, fname) = path.split(fpath)
    root, ext = path.splitext(fname)
    assert root; assert ext

    for i in range(1, 100):
        npath = path.join(head, root+'-'+str(i)+ext)
        if not path.exists(npath):
            break
    return npath

def get_upload_to(media_root, fpath, fname, position=1):
    dpath = distribute_filepath(path.join(fpath, fname), position=position)
    vpath = version_filename(path.join(media_root, dpath))
    return path.join(path.split(dpath)[0], path.split(vpath)[1])

# if other operations will emerge then we should make class of it, with possibly chainable methods
def img_resize(img, width, height, quality, modifier='', rename=True, ext=''):
    '''Resize given image (media root related). Accepts various image types, resulting image is JPEG.
       Return resized img path related to media root - .../origname_widthxheight.ext
    '''
    root, orig_ext = path.splitext(img)
    assert root
    assert orig_ext
    ext = ext if ext else orig_ext

    if rename:
        out_img = root + '_%dx%d' % (width, height) + ext
    else:
        out_img = root + ext

    values = {
        'quality' : quality,
        'width' : width,
        'height' : height,
        'modifier' : modifier,
        'in' : path.join(settings.MEDIA_ROOT, img),
        'out' : path.join(settings.MEDIA_ROOT, out_img)
    }
    
    ret_code = subprocess.call([img_resize.cmd_tmpl % values], shell=True)
    if ret_code:
        # TODO log error here
        return ''
    return out_img

img_resize.cmd_tmpl = 'convert -strip -quality %(quality)d -resize "%(width)dx%(height)d%(modifier)s" %(in)s %(out)s'