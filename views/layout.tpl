<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
    <link href='http://fonts.googleapis.com/css?family=Merriweather:400,700italic|Roboto:500,300,400italic' rel='stylesheet' type='text/css' />
    <link href='/assets/basic.css' rel='stylesheet' type='text/css' />
</head>
<body>
    <header>
        <p class='site-name'>{{site_title}}</p>
        <p class='nav'>
            <a href='/pages/about'>about</a>
%if defined('skip'):
    %if (skip > 0):
            <a href='/n/{{n}}/s/{{skip - n}}'>previous</a>
    %end \\
    %if ((skip + n) < end):
            <a href='/n/{{n}}/s/{{skip + n}}'>next</a>
    %end \\
%end
        </p>
    </header>
    <section class='main'>
%include
    </section>
</body>
