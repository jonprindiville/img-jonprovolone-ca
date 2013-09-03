[i.jp.ca]: http://img.jonprovolone.ca
[bottle]: http://bottlepy.org/
[pillow]: http://python-imaging.github.io/

[img.jonprovolone.ca][i.jp.ca]
==============================
A simple [bottle][bottle]-based webapp (which will be) deployed on my personal
site, [img.jonprovolone.ca][i.jp.ca]. It does some image-thumbnailing and some
basic templating of pages.

TODO
----
- Specify width or height restrictions independantly for thumbs
- Restrict the thumbnailing to some subset of possible sizes (also, no enlarging)
- thumbnail cache aging/eviction
- locking for thumbnail writing? (passenger spawns multiple processes? not sure for wsgi -- it does for ruby)
- Thumbnail caching to play nice with HTTP caching 

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
