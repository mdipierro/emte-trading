from gluon.storage import Storage
settings = Storage()

settings.migrate = True
settings.title = '[E]xchange [M]atching and [T]trading [E]ngine'
settings.subtitle = 'full-stack exchange and trading plaform (fast, scalable, secure)'
settings.author = 'mdipierro'
settings.author_email = 'mdipierro@cs.depaul.edu'
settings.keywords = ''
settings.description = ''
settings.layout_theme = 'default'
settings.database_uri = 'sqlite://storage.sqlite'
settings.security_key = 'e7f25229-0161-48f2-bdbe-e2c325a6b390'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.hmac_key = 'secret' # to communicate to matchingengine.py
