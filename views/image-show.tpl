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
%if 'tags' in image:
    <ul class='tags'>
    %for tag in image['tags']:
        <li><a href='{{site.cfg.get('images', 'route_list') + ':' + tag}}'>{{tag}}</a></li>
    %end
    </ul>
%end
</article>
<!-- /image-show -->
%rebase layout title=use_title, site=site
