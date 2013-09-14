%rebase layout title=data['page-title'], site=site
<article>
    <h3 class='article-name'>{{data['page-title']}}</h3>
    {{!'\n'.join(data['page-content'])}}
</article>
