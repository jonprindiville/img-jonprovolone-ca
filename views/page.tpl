%rebase layout title=data.get('page-title'), site=site
<article>
    <h3 class='article-name'>{{data.get('page-title')}}</h3>
    {{!'\n'.join(data.get('page-content'))}}
</article>
