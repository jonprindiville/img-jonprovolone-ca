[jpro]: http://jonprovolone.ca
[bottle]: http://bottlepy.org/
[pillow]: http://python-imaging.github.io/

[jonprovolone.ca][jpro]
=======================
A simple [bottle][bottle]-based webapp (which will be) deployed on my personal
site, [jonprovolone.ca][jpro]. It does some image-thumbnailing and some
templating of pages / blog-posts.

TODO
----
- Restrict the thumbnailing to some subset of possible sizes (also, no enlarging)
- thumbnail cache aging/eviction
- locking for thumbnail writing? (passenger spawns multiple processes? not sure for wsgi -- it does for ruby)
- Pull image date from EXIF/filesystem if not in JSON
- Sort images by something
- Thumbnail caching to play nice with HTTP caching 
- Describe this
- posts/ handling

Installation
------------
virtualenv is probably best

Requirements:
- [bottle][bottle] (I am using 0.11.6)
- [Pillow][pillow] (I am using 2.1.0)
- libjpeg-devel (in order for Pillow to decode JPEGs)

Running
-------
Executing jonprovolone.py will currently use bottle's built-in server. On
Dreamhost this will be served by Passenger via Apache.
