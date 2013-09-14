%images = site.images()
%rt_l = site.cfg.get('images', 'route_list')
%#
%## nav() gets stuffed into the header of layout.tpl
%def nav():
        <p class='nav'>
    %if (skip > 0): 
            <a id='prev-link' href='{{"{}{}+{}".format(rt_l, max(skip - n, 0), n)}}'>previous</a>
    %end \\
    %if ((skip + n) < len(images)):
            <a id='next-link' href='{{"{}{}+{}".format(rt_l, skip + n, n)}}'>next</a>
    %end \\
        </p>
%end \\
%#
%## scripts() gets stuffed into the end of the body section of layout.tpl
%def scripts():
    <script src='http://code.jquery.com/jquery-2.0.3.min.js'></script>
    <script>loaded={{n}};skipped={{skip}};</script>
    <script src='/assets/image-loader.js'></script>
%end \\ 
%#
<!-- image-listing -->
%include image-listing-images images=images[skip:skip+n], expected=n
<!-- /image-listing -->
%#
%rebase layout title=None, site=site, nav=nav, scripts=scripts
