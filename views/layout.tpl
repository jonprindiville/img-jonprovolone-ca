<!DOCTYPE html>
<html>
<head>
    <title>{{site_title}}{{"" if (site_title == title) else " - {}".format(title)}}</title>
    <link href='http://fonts.googleapis.com/css?family=Merriweather:400,700italic|Roboto:500,300,400italic,100' rel='stylesheet' type='text/css' />
    <link href='/assets/basic.css' rel='stylesheet' type='text/css' />
</head>
<body>
    <header>
        <p class='site-name'><a href='/'>{{site_title}}</a></p>
        <p class='pages'>
            <a href='/pages/about'>about</a>
        </p>
%if defined('nav'):
        %nav()
%end
    </header>
    <section class='main'>
%include
    </section>
</body>
%import os
<!-- pid {{os.getpid()}} -->
