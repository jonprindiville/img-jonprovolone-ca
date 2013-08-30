img-jonprovolone-ca
===================

TODO
----
- Pull image date from EXIF/filesystem if not in JSON
- Sort images by something
- Thumbnail caching to play nice with HTTP caching 
- Describe this
- posts/ handling

Installation
------------
virtualenv is probably best

Requirements:
- bottle (I am using 0.11.6)
- Pillow (I am using 2.1.0)
- libjpeg-devel (in order for Pillow to decode JPEGs)

Running
-------
Executing img-jonpro.py will currently use bottle's built-in server.
I'll figure out deploying behind Apache later.
