#!/bin/python

import bottle, ConfigParser, errno, json, os, PIL, re, string



# Some initialization #################################################

# Load config data
config = ConfigParser.ConfigParser()
config.readfp(open('site.cfg'))

class Site:
    pass

site = Site()
site.app = bottle.Bottle()

site.THIS_PATH = os.path.dirname(os.path.realpath(__file__))

# Images:
site.images = []
site.image_pattern = re.compile('\.([Jj][Pp][Ee]?[Gg])|'
    '([Pp][Nn][Gg])|([Gg][Ii][Ff])$')
site.IMG_PATH = os.path.join(site.THIS_PATH,
    config.get('images', 'dir'), '')
site.THUMB_PATH = os.path.join(site.THIS_PATH,
    config.get('thumbnailing', 'cache_dir'), '')

# Add our templates to bottle's path:
bottle.TEMPLATE_PATH.insert(0, os.path.join(site.THIS_PATH,
    config.get('site', 'template_dir'), ''))



# Utility functions ###################################################

def refresh_images():
    def _image_dict(file):
        # skip this file if it does not look like an image
        if not re.search(site.image_pattern, file):
            return

        # build a basic dict for this image...
        ret = {'url': config.get('images', 'route_raw') + file}

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
                print 'Cannot access metadata at {}'.format(meta_path)
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
    print 'Refreshing image list: [{}]'.format(', '.join(map(str, site.images)))



# Handlers ############################################################

@site.app.route('/')
@site.app.route('/s/<skip:int>')
@site.app.route('/n/<n:int>')
@site.app.route('/n/<n:int>/s/<skip:int>')
def serve_main(skip=0, n=6):
    refresh_images()
    return bottle.template('image-listing',
        title=config.get('site', 'title'),
        site_title=config.get('site', 'title'),
        skip=skip, n=n, end=len(site.images),
        images=site.images[skip:skip+n])


@site.app.route('/pages/<name>')
def serve_page(name):
    try:
        page_data = json.load(open(
            os.path.join(config.get('site', 'page_dir'), '{}.json'.format(name))))
        return bottle.template(page_data.get('template'), data=page_data,
            site_title=config.get('site', 'title'))
    except:
        bottle.abort(404, 'Page "{}" not found'.format(name))
    

@site.app.route('/assets/<file:path>')
def serve_asset(file):
    return bottle.static_file(file, root=config.get('site', 'asset_dir'))


@site.app.route('{}{}'.format(config.get('images', 'route_raw'), '<image>'))
def serve_static_image(image):
    return bottle.static_file(image, root=site.IMG_PATH)


@site.app.route('{}{}'.format(config.get('images', 'route_raw'),
    '<image>/<spec:re:[1-9][0-9]{0,3}s?>'))
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
    thumb = do_resize(PIL.Image.open(os.path.join(site.IMG_PATH, image)), spec)
    thumb.save(cached_path)

    return bottle.static_file(cached_name, root=site.THUMB_PATH)


# The 'spec' in the thumbnail route is a 1-to-3 digit positive
# integer interpreted as the maximum dimension (height OR width) of the
# desired image. The aspect ratio of the image will be maintained.
# If there is an 's' trailing the size in pixels the thumbnail will be
# square -- having been scaled such that its SMALLER dimension matches
# the one given in the URL and then cropped in the other dimension.
#
# e.g. beginning with a 500px by 1000px image, spec="200" will get you
# a 100px by 200px image. Applying spec="200s" to the same file will
# first scale the image to 200px by 400px and then crop the edges off
# to obtain a 200px square.
def do_resize(image, spec):

    # original sizes
    o_width, o_height = image.size

    # If we don't find an 's' in our spec we simply scale the image.
    if (string.find(spec, 's') == -1):
        size = int(spec)
        # The LARGER dimension should be scaled to size
        if (o_width > o_height):
            width = size
            height = int(size * float(o_height) / o_width)
        else:
            height = size
            width = int(size * float(o_width) / o_height)

        return image.resize((width, height), PIL.Image.ANTIALIAS)

    # If we did find an 's' in our spec we've got to crop after scaling
    # to make a square
    else:
        size = int(spec[:-1])
        # The SMALLER dimension should be scaled to size
        if (o_width < o_height):
            width = size
            height = int(size * float(o_height) / o_width)
            box = (0, int(float(height - size)/2),
                width, int(float(height - size)/2) + size)
        else:
            height = size
            width = int(size * float(o_width) / o_height)
            box = (int(float(width - size)/2), 0,
                int(float(width - size)/2) + size, height)

        thumb = image.resize((width, height), PIL.Image.ANTIALIAS)
        return thumb.crop(box)
    


# Debug ###############################################################
if __name__ == "__main__":
    site.app.run(host=config.get('debug', 'host'),
        port=config.get('debug', 'port'))
