%# This file has been split out from image-listing.tpl so that it can
%# be used on its own (".../?fmt=frag" requests) by js requests
%for image in images:
    %if image is not None:
        <a href='{{image['url_html']}}'><img src='{{image['url_img']}}/200s' {{!('title=\'{}\''.format(image['title'])) if ('title' in image) else ''}} /></a>
    %end \\
%end \\
\\
%# Display a way to load more images or a notice that there are no more
%cls = 'none'
%if (len(images) == expected):
    %cls = 'more'
    %msg = 'more'
%elif (len(images) < expected):
    %cls = 'no-more'
    %msg = 'the end'
%end \\
        <div id='more-images' class='{{cls}}' style='display: none'>
            <p class='msg'>{{msg}}</p>
        </div>
