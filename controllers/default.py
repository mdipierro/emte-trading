# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call():
    session.forget()
    return service()
### end requires
def index():
    return dict()

def error():
    return dict()

@auth.requires_login()
def products():
    form=auth.user.manager and crud.create(db.product) or ''
    rows=db(db.product).select(orderby=db.product.name)
    return dict(rows=rows, form=form)

@auth.requires(auth.user and auth.user.manager)
def edit_product():
    return dict(form=crud.update(db.product,request.args(0)))


def send(url,order):
    import urllib, hmac
    sig = settings.hmac_key and hmac.new(settings.hmac_key,order).hexdigest() or ''
    params = urllib.urlencode({'order': order, 'signature': sig})
    f = urllib.urlopen(url, params)
    data= f.read()
    f.close()
    return data
        

@auth.requires_login()
def trade():
    product = db.product(request.args(0)) or redirect(URL('products'))
    return dict(product=product)

@auth.requires_login()
def order():
    print request.vars
    product = db.product(request.vars.product)
    order = '%i:%s %s %s@%s/%s' % (auth.user.id,request.vars.type,
                                   product.name,request.vars.quantity,
                                   request.vars.price or 0,request.vars.stop or 0)
    oid = int(send(product.post_url,order))
    db.buy_sell_order.insert(buy_sell=request.vars.type,
                             product=product.id,
                             quantity=request.vars.quantity,
                             price=request.vars.price,
                             stop_price=request.vars.stop_price,                             
                             oid=oid)
    #if request.vars.type=='buy':
    #    db(db.auth_user.id==auth.user.id).update(virtual_cash=db.auth_user.virtual_cash-request.vars.price*form.vars.quantity)
    return oid

@auth.requires_login()
def zap():
    db(db.buy_sell_order).delete()
    db(db.match).delete()
    return 'zapped!'

@auth.requires_login()
def delete():
    print request.vars
    product=db.product(request.vars.product)
    order=db.buy_sell_order(oid=request.vars.oid,product=request.vars.product,created_by=auth.user.id)
    print order
    if not order: return
    order = '%s:del %s %s' % (auth.user.id,product.name,request.vars.oid)
    print order
    print send(product.post_url,order)
    print request.vars

@auth.requires_login()
def pandl():
    import urllib
    product = db.product(request.args(0)) or redirect(URL('products'))
    f = urllib.urlopen(product.quote_url)
    quote = float(f.read())
    f.close()
    user = db.auth_user[auth.user.id]
    rows = db((db.match.buyer==auth.user.id)|(db.match.seller==auth.user.id)).select(orderby=db.match.match_time)
    return dict(rows=rows,user=user,quote=quote)

@auth.requires_login()
def about():
    return dict()

@auth.requires_login()
def old_trade():
    product = db.product(request.args(0)) or redirect(URL('products'))
    form=LOAD(request.controller,'trade_form',args=[product.id],ajax_trap=True)
    return dict(form=form,product=product)

@auth.requires_login()
def trade_form():
    product = db.product(request.args(0))
    db.buy_sell_order.product.default = product.id
    form = SQLFORM(db.buy_sell_order)
    form.element(_name='buy_sell')['_style']='width:70px'
    form.element(_name='quantity')['_style']='width:70px'
    form.element(_name='price')['_style']='width:70px'
    form.element(_name='stop_price')['_style']='width:70px'
    if form.accepts(request):
        import urllib, hmac
        order = '%i:%s %s %i@%s/%s' % (auth.user.id,form.vars.buy_sell,
                                       product.name,form.vars.quantity,
                                       form.vars.price or 0,form.vars.stop or 0)
        oid = int(send(product.post_url,order))
        db(db.buy_sell_order.id==form.vars.id).update(oid=oid)
        #if form.vars.buy_sell=='buy':
        #    db(db.auth_user.id==auth.user.id).update(virtual_cash=db.auth_user.virtual_cash-form.vars.price*form.vars.quantity)
        response.js = "jQuery('.flash').html('your order %s was submitted').slideDown()" % order
    return form

