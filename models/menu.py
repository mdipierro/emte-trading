response.title = settings.title
response.subtitle = settings.subtitle
response.meta.author = '%s <%s>' % (settings.author, settings.author_email)
response.meta.keywords = settings.keywords
response.meta.description = settings.description
response.menu = [
    (T('Index'),URL('index')==URL(),URL('index'),[]),
    (T('Products'),URL('products')==URL(),URL('products'),[]),
    (T('About'),URL('about')==URL(),URL('about'),[]),
]
