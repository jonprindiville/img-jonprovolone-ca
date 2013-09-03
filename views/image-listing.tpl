<!-- image-listing -->
%def nav():
        <p class='nav'>
    %if (skip > 0): 
            <a href='/n/{{n}}/s/{{skip - n}}'>previous</a>
    %end \\
    %if ((skip + n) < end):
            <a href='/n/{{n}}/s/{{skip + n}}'>next</a>
    %end \\
        </p>
%end \\ 
%for image in images:
    %if image is not None:
        <a href='{{image['url']}}'><img src='{{image['url']}}/232s' alt='{{image.get('name', '')}}' /></a>
    %end \\
%end \\
<!-- /image-listing -->
%rebase layout title=title, site_title=site_title, nav=nav
