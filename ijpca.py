#!/bin/python

# Copyright 2013, Jon Prindiville

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import bottle, ConfigParser, datetime, errno, fcntl, json, logging, os, re, shlex, string, tempfile, time
from PIL import Image



# Global level defs ###################################################

EXIF_DATETIME = 36867 
IMAGE_PATTERN = re.compile('\.([Jj][Pp][Ee]?[Gg])|'
    '([Pp][Nn][Gg])|([Gg][Ii][Ff])$')

class Site:

    def __init__(self, cfg_file='default.cfg'):

        pid = os.getpid()

        self.app = bottle.Bottle()
        
        # Image metadata
        self._images = {'timestamp': None, 'data': []}
        
        # Load config
        self.cfg = ConfigParser.ConfigParser()
        try:
            print '{}|Initializing. Reading default configuration data...'.format(pid)

            with open(cfg_file) as cfg:
                self.cfg.readfp(cfg)
            
            try:
                cfg_files = shlex.split(self.cfg.get('config', 'more'))
                print '{}|Reading additional config ({})...'.format(pid, cfg_files)
                self.cfg.read(cfg_files)
            except ConfigParser.NoOptionError:
                pass # No additional config to read


        except IOError:
            print '{}|Error reading default config from {}'.format(pid, cfg_file)

        # Initialize logging
        self.log = False
        try:
            if self.cfg.getboolean('logging', 'enable'):
                try:
                    loglevel = self.cfg.get('logging', 'level').upper()
                except ConfigParser.NoOptionError:
                    loglevel = 'NOTSET'
                
                try:
                    logfile = self.cfg.get('logging', 'file')
                except ConfigParser.NoOptionError:
                    logfile = None

                logging.basicConfig(filename=logfile, level=loglevel,
                    format='%(asctime)s|%(levelname)s|%(process)d|%(message)s')
                self.log = logging.getLogger()

                print '{}|Logging to {} at level "{}"'.format(pid,
                    'console' if (logfile == None) else '"{}"'.format(logfile),
                    loglevel)

            else:
                print '{}|Logging disabled'.format(pid);

        except ConfigParser.NoSectionError:
            print '{}|No "[logging]" section found in config, logging disabled'.format(pid)
           
        # Set up some paths
        self.THIS_PATH = os.getcwd()
        self.IMG_PATH = os.path.join(self.THIS_PATH,
            self.cfg.get('images', 'dir'), '')
        self.CACHE_PATH = os.path.join(self.THIS_PATH,
            self.cfg.get('site', 'cache_dir'), '')

        self.IS_UPDATER = self.am_i_the_updater()

        done = 'Init complete. I am {}the updater process'.format(
            '' if self.IS_UPDATER else 'not ')
        print '{}|{}'.format(pid, done)
        self.info(done)


    # Decide if this process should act as updater or not. If there
    # are multiple copies of this app running we only want one to
    # be acting as the updater.
    def am_i_the_updater(self):

        we_are = False

        # helper for below...
        def _open_pidfile(mode):
            return open(os.path.join(self.CACHE_PATH,
                self.cfg.get('cache_metadata', 'pidfile')), mode)

        # Open the pidfile for reading if it already exists...
        try:
            with _open_pidfile('r+') as pidfile:
                fcntl.lockf(pidfile, fcntl.LOCK_EX) # blocks waiting for lock

                try:
                    # see if this pid is active
                    os.kill(int(pidfile.read()), 0)
                except (ValueError, OSError):
                    # non-integer read from file or pid no longer running
                    # so rewind the file and write our own pid in there
                    pidfile.seek(0)
                    pidfile.write(str(os.getpid()))
                    we_are = True
                else:
                    # pid still active, we're not the updater
                    pass

                fcntl.lockf(pidfile, fcntl.LOCK_UN) # release
                return we_are

        except IOError as e:
            self.info('Error opening updater pidfile for reading: {}'.format(e))

        # ... or for writing if that fails
        try:
            with _open_pidfile('w+') as pidfile:
                try:
                    fcntl.lockf(pidfile, fcntl.LOCK_EX|fcntl.LOCK_NB) # don't block
                except IOError:
                    # someone else has the lock, we'll back off
                    pass
                else:
                    # we got the lock, we are the updater
                    pidfile.write(str(os.getpid()))
                    we_are = True
                    fcntl.lockf(pidfile, fcntl.LOCK_UN) # release
                    return we_are

        except IOError as ioe:
            self.info('Error creating updater pidfile: {}'.format(e))
            raise ioe

        return we_are


    def debug(self, msg):
        if self.log:
            self.log.debug(msg)


    def info(self, msg):
        if self.log:
            self.log.info(msg)


    def warn(self, msg):
        if self.log:
            self.log.warn(msg)


    def error(self, msg):
        if self.log:
            self.log.error(msg)


    def critical(self, msg):
        if self.log:
            self.log.critical(msg)



    # if our image list is greater than refreshold seconds old (or if it
    # does not exist yet) we will refresh it before returning it --
    # otherwise skip the refresh, return the data we have
    def images(self, refreshold=None):

        # use configured value for refreshold if none given
        if not refreshold:
            refreshold = self.cfg.getint('images', 'refresh')

        # check age...
        try:
            age = int(time.time()) - self._images['timestamp']
            
            if (age < refreshold):
                # we have refreshed recently, just return stored data
                return self._images['data']
            else:
                # we have not recently refreshed, so... 
                pass #and hit the refresh call below
        except TypeError as te:
            # probably because _images['timestamp'] is non-existant
            pass #and hit the refresh call below

        try:
            self.info("Image list is {} seconds old, refreshing...".format(age))
        except NameError:
            # age was not defined because of the TypeError in above try block
            self.info("Image list not found...")

        self._refresh_image_list()
        return self._images['data']


    # scan the image directory, updating our image list
    def _refresh_image_list(self):

        # helper function for map() invocation below: given a file name, make
        # a dict of that image's metadata for our images list
        def _make_image_dict(file):

            # skip this file if it does not look like an image
            if not re.search(IMAGE_PATTERN, file):
                return

            filepath = os.path.join(self.IMG_PATH, file)

            # build a basic dict for this image...
            ret = {'filename': file,
                'url_img': self.cfg.get('images', 'route_file') + file,
                'url_html': self.cfg.get('images', 'route_html') + file}

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
                with open(meta_path) as meta_file:
                    meta_json = json.load(meta_file)
                    meta_json.update(ret)
                    return meta_json
                    
            except IOError as e:
                self.info('Could not read metadata file: {}'.format(e))
            except ValueError as e:
                self.error('Could not parse {} as JSON: {}'.format(meta_path, e))

            # return what we've accumulated
            return ret
        # / _make_image_dict()


        # If we are NOT the updater, read in cached metadata
        if (not self.IS_UPDATER):
            try:
                with open(os.path.join(self.CACHE_PATH, self.cfg.get(
                    'cache_metadata', 'file'))) as meta_file_cached:
                    self._images = json.load(meta_file_cached)
                    self.info('Loaded cached metadata from {}'.format(
                        time.ctime(self._images['timestamp'])))
                    return self._images['data']

            except (IOError, ValueError) as e:
                self.error('Could not load cached metadata from: {}'.format(e));
                # ... fall through to retrieve the information ourselves
       
        # record time of this update
        self._images['timestamp'] = int(time.time())

       # ls the directory of images, building a list of dicts
        self._images['data'] = [i for i in \
            map(_make_image_dict, os.listdir(self.IMG_PATH)) if i is not None];

        # Sorted descending by date
        self._images['data'].sort(reverse=True, key=lambda im: im.get('date'))

        self.info('Refreshed image list')
        self.debug('Image list: [{}]'.format(', '.join(map(str, self._images['data']))))

        # If we are the updater we should put this out to disk for the others
        # We'll write to a temporary file and then move (atomically) the new
        # data to replace the old.
        if self.IS_UPDATER:
            try:
                # Securely create a temp file and open it
                (tmp_fd, tmp_name) = tempfile.mkstemp(
                    prefix=site.cfg.get('cache_metadata', 'file'),
                    dir=self.CACHE_PATH, text=True)
                tmp = os.fdopen(tmp_fd, 'w')

                # Dump information, close
                json.dump(self._images, tmp)
                tmp.close()

                # Move, clobbering old cached data
                dest = os.path.join(self.CACHE_PATH, site.cfg.get('cache_metadata', 'file'))
                os.rename(tmp_name, dest)
                self.info('Cached image metadata to disk at "{}"'.format(dest))

            except (IOError, ValueError, OSError) as e:
                self.error('Problem caching image metadata: {}:{}'.format(type(e),e))



# Some initialization #################################################

site = Site()

# Add our templates to bottle's path:
bottle.TEMPLATE_PATH.insert(0, os.path.join(site.THIS_PATH,
    site.cfg.get('site', 'template_dir'), ''))



# Handlers ############################################################

# Bounce these requests to the image list
@site.app.route('/')
@site.app.route(site.cfg.get('images', 'route_list').rstrip('/'))
@site.app.route(site.cfg.get('images', 'route_list').replace('list/', ''))
@site.app.route(site.cfg.get('images', 'route_list').replace('/list/', ''))
def _redir_to_img_list():
    bottle.redirect(site.cfg.get('images', 'route_list'))


@site.app.route(site.cfg.get('images', 'route_list'))
@site.app.route(site.cfg.get('images', 'route_list') +
    '<offset:re:([0-9]*)\+([0-9]*)\/?>')
def serve_img_list(offset=None):
    offs = offset.split('+') if (offset is not None) else None

    try:
        skip = int(offs[0])
    except:
        skip = 0

    try:
        n = int(offs[1])
    except:
        n = site.cfg.getint('images', 'n_per_page')

    if bottle.request.query.fmt == 'frag':
        return bottle.template('image-listing-images', expected=n,
            images=site.images()[skip:skip+n])
    else:
        return bottle.template('image-listing', site=site, skip=skip, n=n)


@site.app.route(site.cfg.get('images', 'route_html') + '<image>')
def serve_img_html(image):
    try:
        return bottle.template('image-show', site=site, image=filter(
            (lambda x: x['filename'] == image), site.images())[0])
    except IndexError: 
        # Guess we didn't have that
        msg = 'Image {} not found'.format(image)
        site.error(msg)
        bottle.abort(404, msg)


# TODO: not use json for page data -- no long lines (maybe yaml?)
@site.app.route('/pages/<name>')
def serve_page(name):
    try:
        with open(os.path.join(site.cfg.get('site', 'page_dir'),
            '{}.json'.format(name))) as page_file:
            page_data = json.load(page_file)

        return bottle.template(page_data.get('template'),
            data=page_data, site=site)

    except ValueError as ve:
        msg = 'Exception while parsing page data'
        site.error(msg + ": " + str(ve))
        bottle.abort(500, msg)

    except Exception as e:
        msg = 'Exception while rendering page'
        site.error(msg + ": " + str(e));
        bottle.abort(500, msg)
    

@site.app.route('/assets/<file:path>')
def serve_asset(file):
    return bottle.static_file(file, root=site.cfg.get('site',
        'asset_dir'))


@site.app.route(site.cfg.get('images', 'route_file') + '<image>')
def serve_static_image(image):
    return bottle.static_file(image, root=site.IMG_PATH)


@site.app.route(site.cfg.get('images', 'route_file') +
    '<image>/<spec:re:[1-9][0-9]*(s|h|w)?>')
def serve_thumbnail(spec, image):
    
    # Is this request referring to a valid image?
    if not (os.access(os.path.join(site.IMG_PATH, image), os.R_OK)):
        site.error('Error serving thumbnail "{}": file unreadable'.format(image))
        bottle.abort(404, 'File not found')

    # Return the cached thumbnail if it exists
    cached_name = '{}-{}'.format(spec, image)
    cached_path = os.path.join(site.CACHE_PATH, cached_name)
    if (os.access(cached_path, os.R_OK)):
        return bottle.static_file(cached_name, root=site.CACHE_PATH)

# TODO: refactor above to use try/except

    # If not, we'll try generating the thumbnail...

    # Try creating the cache directory if not existing already...
    if not (os.access(site.CACHE_PATH, os.F_OK)):
        os.mkdir(site.CACHE_PATH, 0755)

    # Do we have a cache dir now?
    if not (os.path.isdir(site.CACHE_PATH)):
        err = 'Cache "{}" not a directory'.format(site.CACHE_PATH)
        site.error(err)
        bottle.abort(500, err)

    # Is it writeable?
    if not (os.access(site.CACHE_PATH, os.W_OK)):
        err = 'Cache "{}" not writeable'.format(site.CACHE_PATH)
        site.error(err)
        bottle.abort(500, err)

    # Resize according to spec, if the user has asked for the image to
    # be enlarged, we'll see a ValueError from do_resize, redirect to original
    try:
        thumb = do_resize(Image.open(os.path.join(site.IMG_PATH, image)), spec)
    except ValueError:
        bottle.redirect(site.cfg.get('images', 'route_file') + image)

    thumb.save(cached_path)
    return bottle.static_file(cached_name, root=site.CACHE_PATH)


# The 'spec' in the thumbnail route is a 1+ digit unsigned integer
# followed (optionally) by an 's', 'h', or 'w'.
#
# The integer is interpreted as the maximum dimension of the desired image.
# The aspect ratio of the image will be maintained.
#
# 's': create a square image. Scale such that the image's SMALLER
# dimension matches the one given in the URL and then crop (centered) in the
# other dimension to obtain a square.
#
# 'h': The dimension in the URL is the maximum height
#
# 'w': The dimension in the URL is the maximum width
#
# no letter: The dimension in the URL is the maximum of either dimension
# (preserve aspect ratio)
#
# Will raise a ValueError if an enlargement is requested
def do_resize(image, spec):

    # original sizes
    o_width, o_height = image.size

    # requested dimension as int
    new_size = int(spec.translate(string.maketrans('hsw', '   ')))

    # We don't do enlarging
    if (new_size >= o_width) and (new_size >= o_height):
        raise ValueError('Enlargement requested')

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
    site.app.run(host=site.cfg.get('debug', 'host'),
        port=site.cfg.get('debug', 'port'))
