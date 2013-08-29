<!DOCTYPE html>
<html>
<head>
    <title>{{title}}</title>
</head>
<body>
    <section>
%if (skip > 0):
        <a href="/n/{{n}}/s/{{max(skip - n, 0)}}">Previous</a>
%end
%for image in images:
    %if image is not None:
        <img src='{{image['url']}}' alt='{{image.get('name', '')}}' /> 
        %if image.get('comment', False):
        <p class='comment'>{{image['comment']}}</p>
        %end        
    %end
%end
%if ((skip + n) < end):
        <a href="/n/{{n}}/s/{{skip + n}}">Next</a>
%end
    </section>
</body>
