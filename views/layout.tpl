%s_title = site.config.get('site','title')
<!DOCTYPE html>
<html>
<head>
    <title>{{s_title}}\\
%if (defined('title') and (title != None)):
 - {{title}}\\
%end \\
</title>
    <link href='http://fonts.googleapis.com/css?family=Merriweather:400,700italic|Roboto:500,300,400italic,100' rel='stylesheet' type='text/css' />
    <link href='/assets/normalize.css' rel='stylesheet' type='text/css' />
    <link href='/assets/basic.css' rel='stylesheet' type='text/css' />
    <meta name='viewport' content='width=device-width, initial-scale=1' />
</head>
<body>
    <header>
        <p class='site-name'><a href='/'>{{s_title}}</a></p>
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
%if defined('scripts'):
    %scripts()
%end
</body>
