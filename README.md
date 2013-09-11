[i.jp.ca]: http://img.jonprovolone.ca
[bottle]: http://bottlepy.org/
[pillow]: http://python-imaging.github.io/

[img.jonprovolone.ca][i.jp.ca]
==============================
A simple [bottle][bottle]-based webapp deployed on my personal
site, [img.jonprovolone.ca][i.jp.ca]. It does some image-thumbnailing and some
basic templating of pages.

TODO
----
- trigger loading on click of whole box, not just 'more' text
- images listed by tag
- image detail page (several size links, EXIF data, tags, comments)
- pull tags from EXIF
- js-load newer (not just older) images
- update 'next'/'prev' links while js-loading more images
- log rotation
- configurable image dir refresh time
- Restrict the thumbnailing to some subset of possible sizes
- thumbnail cache aging/eviction
- locking for thumbnail writing? (passenger spawns multiple processes)
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
Executing ijpca.py will currently use bottle's built-in server. On
Dreamhost this will be served by Passenger via Apache.
