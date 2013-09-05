#!/bin/python

# Copyright 2013, Jon Prindiville

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import bottle, ConfigParser, datetime, errno, json, os, re, string
from PIL import Image



# Global level defs ###################################################

EXIF_DATETIME = 36867 
IMAGE_PATTERN = re.compile('\.([Jj][Pp][Ee]?[Gg])|'
    '([Pp][Nn][Gg])|([Gg][Ii][Ff])$')

class Site:

    def __init__(self, cfg_file='site.cfg'):

        self.app = bottle.Bottle()
        
        self._images = []
        self._images_timestamp = None
        
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(cfg_file))

        self.THIS_PATH = os.path.dirname(os.path.realpath(__file__))
        self.IMG_PATH = os.path.join(self.THIS_PATH,
            self.config.get('images', 'dir'), '')
        self.THUMB_PATH = os.path.join(self.THIS_PATH,
            self.config.get('thumbnailing', 'cache_dir'), '')


    # if our image list is greater than refreshold seconds old (or if it
    # does not exist yet) we will refresh it before returning it --
    # otherwise skip the refresh, return the data we have
    def images(self, refreshold=None):

        # use configured value for refreshold if none given
        if not refreshold:
            refreshold = self.config.getint('images', 'refresh')

        # check age...
        try:
            age = (datetime.datetime.now() -
                self._images_timestamp).total_seconds()
            
            if (age < refreshold):
                # we have refreshed recently, just return stored data
                return self._images
            else:
                # we have not recently refreshed, so... 
                pass #and hit the refresh call below
        except TypeError:
            # probably because _images_timestamp is non-existant
            pass #and hit the refresh call below

        try:
            print "Image list is {} seconds old, refreshing...".format(age)
        except NameError:
            print "Image list being generated for the first time.."
        self._refresh_image_list()
        return self._images


    # scan the image directory, updating our image list
    def _refresh_image_list(self):

        # record time of update
        self._images_timestamp = datetime.datetime.now()

        # given a file name, make a dict of that image's metadata for
        # our images list (this is used in the map() call below)
        def _make_image_dict(file):

            # skip this file if it does not look like an image
            if not re.search(IMAGE_PATTERN, file):
                return

            filepath = os.path.join(self.IMG_PATH, file)

            # build a basic dict for this image...
            ret = {'url': self.config.get('images', 'route_raw') + file}

            # Try pulling date from EXIF... 
            try:
                d = Image.open(filepath)._getexif().get(EXIF_DATETIME)
                ret.update({'date': datetime.datetime.
                    strptime(d.split(' ')[0], '%Y:%m:%d').strftime('%Y-%m-%d') })
            except:
                # ... failing that, take the mtime:
                try:
                    ret.update({'date': datetime.date.fromtimestamp(
                        os.stat(filepath).st_mtime).strftime('%Y-%m-%d')})
                except:
                    # EXIF and mtime failed, oh well
                    pass

            # see if there is any extra metadata in a json file of the 
            # same basename and incorporate it in our return value...
            base, ext = os.path.splitext(self.IMG_PATH + file)
            meta_path = base + '.json'
            try:
                meta_file = open(meta_path)
            except IOError as e:
                #TODO: error logging
                pass
            else:
                with meta_file:
                    meta_json = json.load(meta_file)
                    meta_json.update(ret)
                    return meta_json

            # return what we've accumulated
            return ret


       # ls the directory of images, building a list of dicts
        self._images = [i for i in \
            map(_make_image_dict, os.listdir(self.IMG_PATH)) if i is not None];

        # Sorted descending by date
        self._images.sort(reverse=True, key=lambda im: im.get('date'))

        print 'Refreshed image list: [{}]'.format(', '.join(map(str, self._images)))



# Some initialization #################################################

site = Site()

# Add our templates to bottle's path:
bottle.TEMPLATE_PATH.insert(0, os.path.join(site.THIS_PATH,
    site.config.get('site', 'template_dir'), ''))



# Handlers ############################################################

@site.app.route('/')
@site.app.route('/s/<skip:int>')
@site.app.route('/n/<n:int>')
@site.app.route('/n/<n:int>/s/<skip:int>')
def serve_main(skip=0, n=6):
    return bottle.template('image-listing',
        site_title=site.config.get('site', 'title'),
        title=site.config.get('site', 'title'),
        skip=skip, n=n, end=len(site.images()),
        images=site.images()[skip:skip+n])
#TODO: pass site to templates... simplify, man

@site.app.route('/pages/<name>')
def serve_page(name):
    try:
        page_data = json.load(open(
            os.path.join(site.config.get('site', 'page_dir'),
                '{}.json'.format(name))))

        return bottle.template(page_data.get('template'), data=page_data,
            site_title=site.config.get('site', 'title'))
    except:
        bottle.abort(404, 'Page "{}" not found'.format(name))
    

@site.app.route('/assets/<file:path>')
def serve_asset(file):
    return bottle.static_file(file, root=site.config.get('site',
        'asset_dir'))


@site.app.route('{}{}'.format(site.config.get('images', 'route_raw'),
    '<image>'))
def serve_static_image(image):
    return bottle.static_file(image, root=site.IMG_PATH)


@site.app.route('{}{}'.format(site.config.get('images', 'route_raw'),
    '<image>/<spec:re:[1-9][0-9]*(s|h|w)?>'))
def serve_thumbnail(spec, image):
    
    # Is this request referring to a valid image?
    if not (os.access(os.path.join(site.IMG_PATH, image), os.R_OK)):
        bottle.abort(404, 'File not found')

    # Return the cached thumbnail if it exists
    cached_name = '{}-{}'.format(spec, image)
    cached_path = os.path.join(site.THUMB_PATH, cached_name)
    if (os.access(cached_path, os.R_OK)):
        return bottle.static_file(cached_name, root=site.THUMB_PATH)

# TODO: refactor above to use try/except

    # If not, we'll try generating the thumbnail...

    # Try creating the cache directory if not existing already...
    if not (os.access(site.THUMB_PATH, os.F_OK)):
        os.mkdir(site.THUMB_PATH, 0755)

    # Do we have a cache dir now?
    if not (os.path.isdir(site.THUMB_PATH)):
        bottle.abort(500, 'Cache "{}" not a directory'.format(site.THUMB_PATH))

    # Is it writeable?
    if not (os.access(site.THUMB_PATH, os.W_OK)):
        bottle.abort(500, 'Cache "{}" not writeable'.format(site.THUMB_PATH))

    # Resize according to spec
    thumb = do_resize(Image.open(os.path.join(site.IMG_PATH, image)), spec)
    thumb.save(cached_path)

    return bottle.static_file(cached_name, root=site.THUMB_PATH)


# The 'spec' in the thumbnail route is a 1+ digit unsigned integer
# followed (optionally) by an 's', 'h', or 'w'.
#
# The integer is interpreted as the maximum dimension of the desired image.
# The aspect ratio of the image will be maintained.
#
# 's': create a square image. Scale such that the image's SMALLER
# dimension matches the one given in the URL and then crop in the other
# dimension to obtain a square.
#
# 'h': The dimension in the URL is the maximum height
#
# 'w': The dimension in the URL is the maximum width
#
# no letter: The dimension in the URL is the maximum of either dimension
# (preserve aspect ratio)
def do_resize(image, spec):

    # original sizes
    o_width, o_height = image.size

    # requested dimension as int
    new_size = int(spec.translate(string.maketrans('hsw', '   ')))

    if (new_size >= o_width) and (new_size >= o_height):
        bottle.abort(400, 'No enlarging of images permitted')

    def _resize_w(image, size):
        width = size
        height = int(size * float(o_height) / o_width)
        return image.resize((width, height), Image.ANTIALIAS)

    def _resize_h(image, size):
        height = size
        width = int(size * float(o_width) / o_height)
        return image.resize((width, height), Image.ANTIALIAS)

    # height was specified
    if (string.find(spec, 'h') != -1):
        return _resize_h(image, new_size)

    # weight was specified
    if (string.find(spec, 'w') != -1):
        return _resize_w(image, new_size)

    # square! scale the smaller dimension to the appropriate size
    # and then crop
    if (string.find(spec, 's') != -1):
        if (o_width < o_height):
            thumb = _resize_w(image, new_size)
            w, h = thumb.size
            box = (0, int(float(h - new_size)/2),
                w, int(float(h - new_size)/2) + new_size)
        else:
            thumb = _resize_h(image, new_size)
            w, h = thumb.size
            box = (int(float(w - new_size)/2), 0,
                int(float(w - new_size)/2) + new_size, h)

        return thumb.crop(box)

    # must not have specified, choose larger dimension
    return _resize_w(image, new_size) if (o_width > o_height) else \
        _resize_h(image, new_size)



# Debug ###############################################################
if __name__ == "__main__":
    site.app.run(host=site.config.get('debug', 'host'),
        port=site.config.get('debug', 'port'))
