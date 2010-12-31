response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%s <%s>' % (settings.author, settings.author_email)
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Index'),URL('index').xml()==URL().xml(),URL('index'),[]),
    (T('Products'),URL('products').xml()==URL().xml(),URL('products'),[]),
    (T('About'),URL('about').xml()==URL().xml(),URL('about'),[]),
]
