[i.jp.ca]: http://img.jonprovolone.ca
[bottle]: http://bottlepy.org/
[pillow]: http://python-imaging.github.io/

[img.jonprovolone.ca][i.jp.ca]
==============================
A simple [bottle][bottle]-based webapp deployed on my personal
site, [img.jonprovolone.ca][i.jp.ca]. It does some image-thumbnailing and some
basic templating of pages.

Serving images
--------------
Upload some images and then...

    # get the image as stored on disk
    GET /img/file/foo.jpg

    # scale the image proportionally to...
    GET /img/file/foo.jpg/600w      # ... 600px wide
    GET /img/file/foo.jpg/600h      # ... 600px high
    GET /img/file/foo.jpg/600       # ... the smaller of 600px wide or high
    GET /img/file/foo.jpg/600s      # ... the larger of 600px wide or high, then crop square

    GET /img/show/foo.jpg           # HTML page with image details

    # HTML listing of thumbnails...
    GET /img/list/                  # ... of the first x (defaults to 8) images
    GET /img/list/4+10              # ... of 10 images, skipping the first 4
    GET /img/list/:cat              # ... of the first x images tagged with 'cat'
    GET /img/list/:cat/4+10         # ... of 10 'cat'-tagged images, skipping the first 4

Scaled images are cached on the server, hopefully we play nice with
HTTP cache control mechanisms.


Installation
------------
virtualenv is probably best

Requirements:
- [bottle][bottle] (I am using 0.11.6)
- [Pillow][pillow] (I am using 2.1.0)
- libjpeg-devel (in order for Pillow to decode JPEGs)

Running
-------
Executing ijpca.py will currently use bottle's built-in server. On
Dreamhost this will be served by Passenger via Apache.

TODO
----
- Rethink the "only one updater" behaviour: sometimes one of the non-updater
processes seems to handle a bunch of requests in a row -- if at that time its
metadata is out of date it will pull in the cached copy. If the cached copy is
also old, subsequent requests will have it loading and re-loading that
expired cached copy from disk.
    - Maybe do it on site start-up? I wonder how long passenger keeps these
    processes up?
    - Maybe just do it by a cronjob and the active applications don't do any
    updating.
    -
- image detail page (several size links, EXIF data, tags, prev/next links)
- pull tags from EXIF
- js-load newer (not just older) images
- log rotation
- Restrict the thumbnailing to some subset of possible sizes
- thumbnail cache aging/eviction
- locking for thumbnail writing? (passenger spawns multiple processes)
- examine bottle's cache-control settings
