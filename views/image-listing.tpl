%title = None
%images = site.images(tag=tag)
%link_base = site.cfg.get('images', 'route_list')
%if tag is not None:
    %title = 'tagged with ' + tag
    %link_base = link_base + ':{}/'.format(tag)
%end
%#
%## nav() gets stuffed into the header of layout.tpl
%def nav():
    %do_prev = (skip > 0)
    %do_next = ((skip + n) < len(images))
    %if (do_prev or do_next):
        <p class='nav'>
        %if do_prev: 
            <a id='prev-link' href='{{"{}{}+{}".format(link_base, max(skip - n, 0), n)}}'>previous</a>
        %end \\
        %if do_next:
            <a id='next-link' href='{{"{}{}+{}".format(link_base, skip + n, n)}}'>next</a>
        %end \\
        </p>
    %end \\
%end \\
%#
%## scripts() gets stuffed into the end of the body section of layout.tpl
%def scripts():
    <script src='http://code.jquery.com/jquery-2.0.3.min.js'></script>
    <script>loaded={{n}};skipped={{skip}};link_base='{{link_base}}';</script>
    <script src='/assets/image-loader.js'></script>
%end \\ 
%#
<!-- image-listing -->
%include image-listing-images images=images[skip:skip+n], expected=n
<!-- /image-listing -->
%#
%rebase layout title=title, site=site, nav=nav, scripts=scripts
