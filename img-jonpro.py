#!/bin/python

import bottle
import errno
import json
import os
import re

from bottle import route, run, static_file, template

class Site:
    pass



# Some initialization #################################################

site = Site()
site.images = []
site.image_pattern = re.compile('\.([Jj][Pp][Ee]?[Gg])|'
                                '([Pp][Nn][Gg])|([Gg][Ii][Ff])$');
site.TITLE = "img . jon provolone . ca"

# The path containing this file
site.THIS_PATH = os.path.dirname(os.path.realpath(__file__))

# path to image files
site.IMG_DIR = 'images'
site.IMG_PATH = os.path.join(site.THIS_PATH, site.IMG_DIR, "")
site.IMG_ROUTE = '/static/img/'

# path to templates
TEMPLATE_DIR = 'views'
TEMPLATE_PATH = os.path.join(site.THIS_PATH, TEMPLATE_DIR, "")
bottle.TEMPLATE_PATH.insert(0,TEMPLATE_PATH)



# Utility functions ###################################################

def refresh_images():
    def _image_dict(file):
        # skip this file if it does not look like an image
        if not re.search(site.image_pattern, file):
            return

        # build a basic dict for this image...
        ret = {'url': site.IMG_ROUTE + file}

        # TODO: pull date from EXIF or mtime

        # see if there is any extra metadata in a json file of the 
        # same basename and incorporate it in our return value...
        base, ext = os.path.splitext(site.IMG_PATH + file)
        meta_path = base + '.json'
        try:
            meta_file = open(meta_path)
        except IOError as e:
            if e.errno == errno.ENOENT:
                # No extra metadata, carry on
                return ret
            if e.errno == errno.EACCESS:
                # Permission or other access error
                print 'Cannot access metadata at %s' % meta_path
                return ret
            raise
        else:
            with meta_file:
                meta_json = json.load(meta_file)
                meta_json.update(ret)
                return meta_json

    # ls the directory of images, building a list of dicts
    site.images = [i for i in \
        map(_image_dict, os.listdir(site.IMG_PATH)) if i is not None];
    print 'Refreshing image list: [%s]' % ', '.join(map(str, site.images))



# Handlers ############################################################

@route('/')
@route('/s/<skip:int>')
@route('/n/<n:int>')
@route('/n/<n:int>/s/<skip:int>')
def basic(skip=0, n=10):
    refresh_images()
    return template('basic', title=site.TITLE, skip=skip, n=n,
                    end=len(site.images), images=site.images[skip:skip+n])

@route('/static/img/<file>')
def static_img(file):
    return static_file(file, root=site.IMG_PATH)


# Debug ###############################################################
print "TEMPLATES@%s" % bottle.TEMPLATE_PATH
run(host="localhost", port=8080)
