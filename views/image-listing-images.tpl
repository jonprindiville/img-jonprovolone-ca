%for image in images:
    %if image is not None:
        <a href='{{image['url']}}/1000'><img src='{{image['url']}}/200s' alt='{{image.get('name', '')}}' /></a>
    %end \\
%end \\
