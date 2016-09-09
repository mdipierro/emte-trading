# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())
def download(): return response.download(request,db)
def call():
    session.forget()
    return service()
### end requires
def index():
    """**index** action associated with index.html

    detailed information for the Exchange Matching and Trading Engine
    """
    return dict()

def error():
    """ **error** action associated with error.html."""
    return dict()

@auth.requires_login()
def products():
    """**products** action associated with product.html

    Register new tradable security, and entering trading platform here. Login requrired
    """
    form=auth.user.manager and crud.create(db.product) or ''
    rows=db(db.product).select(orderby=db.product.name)
    return dict(rows=rows, form=form)

@auth.requires(auth.user and auth.user.manager)
def edit_product():
    """update product table. Must have manager privilege"""
    return dict(form=crud.update(db.product,request.args(0)))


def send(url,order):
    """sends data after unencrypts serect key, and read message from the fetched from the url

    :param str url: the url to be fetched
    :param str order: the order from users.
    .. seealso:: :function:: order

    :return: order id
    """
    import urllib, hmac
    sig = settings.hmac_key and hmac.new(settings.hmac_key,order).hexdigest() or ''
    params = urllib.urlencode({'order': order, 'signature': sig})
    f = urllib.urlopen(url, params)
    data= f.read()
    f.close()
    return data


@auth.requires_login()
def trade():
    """**trade** action associated with trade.html. Login requrired"""
    product = db.product(request.args(0)) or redirect(URL('products'))
    return dict(product=product)

@auth.requires_login()
def order():
    """sends order to websocket server, and inserts order to buy_sell_order table. Login requrired"""
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
    """ Delete records. Login required """
    db(db.buy_sell_order).delete()
    db(db.match).delete()
    return 'zapped!'

@auth.requires_login()
def delete():
    """ send message to websocket server to delete order. Login required """
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
    """ **pandl** (profit and loss) action associated with pandl.html, that shows trading account balance. Login required. """
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
    """**about** action associated with about.html. Login required"""
    return dict()

@auth.requires_login()
def old_trade():
    """**old_trade** action associated with old_trade.html. Login required"""
    product = db.product(request.args(0)) or redirect(URL('products'))
    form=LOAD(request.controller,'trade_form',args=[product.id],ajax_trap=True)
    return dict(form=form,product=product)

@auth.requires_login()
def trade_form():
    """
    submits order by sending to websocket server. This action add extra form elements to old_trade action

    :return: SQLFORM form
    """
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
