%use_title = image['filename'] if ('title' not in image) else image['title']
<!-- image-show -->
<article class='image-show'>
    <img src='{{image['url_img']}}/500w' />
    <p>
        <span class='date'>{{image['date']}}</span>
        <span class='title'>{{use_title}}</span>
        <span class='original'>(<a href='{{image['url_img']}}'>full size</a>)</span>
    </p>
%if 'comment' in image:
    <p class='comment'>{{image['comment']}}</p>
%end \\
</article>
<!-- /image-show -->
%rebase layout title=use_title, site=site
