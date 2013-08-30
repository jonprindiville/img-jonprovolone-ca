%rebase layout title=title, site_title=site_title, skip=skip, n=n, end=end
%for image in images:
    %if image is not None:
        <a href='{{image['url']}}'><img src='{{image['url']}}/232s' alt='{{image.get('name', '')}}' /></a>
    %end \\
%end \\
<!-- image-listing -->
