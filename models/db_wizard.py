### we prepend t_ to tablenames and f_ to fieldnames for disambiguity

########################################
db.define_table('product',                
                Field('name', type='string',label=T('Name'),requires=[IS_MATCH('[_a-z]+'),IS_NOT_IN_DB(db,'product.name')]),
                Field('description', type='string',label=T('Desciption')),
                Field('unit_price', type='double',label=T('Unit Price')),
                Field('post_url'),
                Field('quote_url'),
                Field('ws_url'),
                Field('active','boolean',default=True,label=T('Active'),writable=False,readable=False),
                Field('created_on','datetime',default=request.now,
                      label=T('Created On'),writable=False,readable=False),
                Field('modified_on','datetime',default=request.now,
                      label=T('Modified On'),writable=False,readable=False,
                      update=request.now),
                Field('created_by',db.auth_user,default=auth.user_id,
                      label=T('Created By'),writable=False,readable=False),
                Field('modified_by',db.auth_user,default=auth.user_id,
                      label=T('Modified By'),writable=False,readable=False,
                      update=auth.user_id),
                format='%(name)s',
                migrate=settings.migrate)

db.define_table('buy_sell_order',               
                Field('product', db.product,readable=False,writable=False),
                Field('buy_sell',requires=IS_IN_SET(('buy','sell')),default='buy'),
                Field('quantity','integer',requires=IS_INT_IN_RANGE(1,10000)),
                Field('price','double',default=0,requires=IS_FLOAT_IN_RANGE(0,10000),comment='0 for market order'),
                Field('stop_price','double',default=0,comment='0 if not stop order'),
                Field('oid','integer',default=0,writable=False,readable=False),
                Field('created_on','datetime',default=request.now,writable=False,readable=False),
                Field('created_by',db.auth_user,default=auth.user_id,writable=False,readable=False))

db.define_table('match',
                Field('product', db.product),
                Field('quantity','integer'),
                Field('price','double'),
                Field('buyer','reference auth_user'),
                Field('seller','reference auth_user'),
                Field('buy_oid','integer'),
                Field('sell_oid','integer'),
                Field('match_time','double'),
                Field('created_on','datetime',writable=False,readable=False))
