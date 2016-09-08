#!/usr/bin/python
# example based on http://thomas.pelletier.im/2010/08/websocket-tornado-redis/

hmac_key = 'secret'

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import hmac
import re
import time
import sys
import optparse
import simplejson

(TYPE,QUANTITY,PRICE,STOP,OID,OWNER,TIMESTAMP) = ('type','quantity','price','stop','oid','owner','timestamp')

def prettyprint(oid,order,matches,state):
    """"
    formats the order message

    :param str oid: the id from order of user
    :param str order: order from user
    :param list matches: the list of orders that are fullfiled
    :param list state: list of order type

    :return: the message of order type, and order quantity at a bid/ask price
    :rtype: str
    """

    message = '[%s] from user %s\n' % (oid, order)
    message +=  '    quotes: '+' '.join('%(quantity)s@%(price)s' % m for m in matches)+'\n'
    for ell in ('mo_buy','mo_sell','lo_buy','lo_sell'):
        message += '    '+ell+': '+' '.join('%(quantity)s@%(price)s' % x for x in state[ell])+'\n'
    for ell in ('so_buy','so_sell'):
        message += '    '+ell+': '+' '.join('%(quantity)s@%(price)s/%(stop)s' % x for x in state[ell])+'\n'
    return message

class Engine:
    """
    Matches orders of single security

    Example usage::

        >>> engine = Engine('intc')
        >>> user = 1
        >>> oid,matches = engine.process('1:buy intc 1',user)         # market order
        >>> oid,matches = engine.process('2:buy intc 1@50.6',user)    # limit order
        >>> oid,matches = engine.process('3:buy intc 1@50.6/49',user) # stop order
        >>> engine.process('3:del intc %s' % oid, user)               # delete order
        >>> for match in matches: print match['quantity'], match['price'], match['buyer'], match['seller']

    """

    # re_order = re.compile('^((?P<o>\d+):)?(?P<t>(buy|sell|del))( (?P<n>[_a-z]+))? (?P<q>\d+)(\@(?P<p>\d+(\.\d+)?))?(/(?P<s>\d+(\.\d+)?))?$')


    def __init__(self,ticker,price=100.0,logfilename=None):
        """
        creates instance assosicate with the Engine class

        :param str ticker: the security ticker symbol
        :param float price: the security price (optional)
        :param str logfilename: the name of the logfile (optional)
        """
        self.logfile = open(logfilename or ticker+'.log','a')
        self.price = price  # initial trading price of securities
        self.ticker = ticker
        self.oid = 0
        self.mo_buy = []  # queue of buy market orders (for single security)
        self.mo_sell = [] # queue of sell market orders (for single security)
        self.lo_buy = []  # queue of buy limit orders (for single security)
        self.lo_sell = [] # queue of sell limit orders (for single security)
        self.so_buy = []  # queue of buy stop orders (for single security)
        self.so_sell = [] # queue of sell stop orders (for single security)
        self.re_order = re.compile('^((?P<o>\d+):)?(?P<t>(buy|sell|del))( (?P<n>[_a-z]+))? (?P<q>\d+)(\@(?P<p>\d+(\.\d+)?))?(/(?P<s>\d+(\.\d+)?))?$')


    def state(self):
        """
        Clones current state of engine object

        :return: the dictionary that clone the current state of Engine instance
        :rtype: dict
        """
        return dict(price=self.price,oid=self.oid,
                    mo_buy=self.mo_buy,mo_sell=self.mo_sell,
                    lo_buy=self.lo_buy,lo_sell=self.lo_sell,
                    so_buy=self.so_buy,so_sell=self.so_sell)

    def process(self, order_text):
        """
        processes order from order queue

        :param str order_text: the string in format '<order id>:<buy|sell|del> <security ticker> <quantity>@<price>',<user>'

        :return: order id and list of matched order
        :rtype: tuple
        """
        t0=time.time()
        # parse order. owner is the id of the order submitter
        match = self.re_order.match(order_text)
        if not match or not match.group('n') in (None,self.ticker): return None, []
        ticker = match.group('n') or self.ticker
        owner = int(match.group('o') or 0)
        type = match.group('t')
        number = int(match.group('q'))
        if number==0: return None, []
        price = float(match.group('p') or 0)
        stop = float(match.group('s') or 0)
        mo_buy = self.mo_buy
        mo_sell = self.mo_sell
        lo_buy = self.lo_buy
        lo_sell = self.lo_sell
        so_buy = self.so_buy
        so_sell = self.so_sell
        # if this is a delete order remove it from the queue
        if type == 'del':
            for ell in (mo_buy,mo_sell,lo_buy,lo_sell,so_buy,so_sell):
                if [ell.pop(i) for i,item in enumerate(ell) if item[OID] == number and item[OWNER] == owner]:
                    return number, []
        # determine order id for current order
        self.oid += 1
        # this is the order
        order = dict(type=type,quantity=number,price=price,stop=stop,
                     oid=self.oid,owner=owner,timestamp=t0)
        self.logfile.write('%(timestamp)f: [%(oid)s] %(owner)s %(type)s %(quantity)s@%(price)s/%(stop)s\n' % order)

        def insert(queue,order,key,sign=1):
            """
            inserts order and sorts elements.

            :param list queue: the order queue
            :param dict order: the order submitted by user
            :param str key: the key in order
            :param int sign: value of 1 indicates increasing, value of -1 indicates dedcresing in order quantity
            """
            i,value = len(queue)-1,order[key]*sign
            while i>=0:
                if queue[i][key]*sign >= value: break
                i -= 1
            queue.insert(i+1,order)

        # append it to proper queue
        if stop: insert(so_buy,order,STOP,1) if type == 'buy' else insert(so_sell,order,STOP,-1)
        elif price: insert(lo_buy,order,PRICE,1) if type == 'buy' else insert(lo_sell,order,PRICE,-1)
        else: mo_buy.append(order) if type == 'buy' else mo_sell.append(order)

        def match(bo,so):
            """
            matches orders from two give queues (bo,so).

            :param list bo: the list of buy orders
            :param list so: the list of sell order

            :return: matched order
            :rtype: dict
            """
            # get older orders
            b,s = bo[0],so[0]
            # find matching price
            self.price = (b[PRICE] and s[PRICE]) and (b[PRICE]+s[PRICE])/2 or b[PRICE] or s[PRICE] or self.price
            # find matching quantity (for partial fills)
            matched_quantity = min(b[QUANTITY],s[QUANTITY])
            # store match
            match = {'type':'match','quantity':matched_quantity,
                     'price':self.price,'sell_oid':s[OID],
                     'seller':s[OWNER],'buy_oid':b[OID],
                     'buyer':b[OWNER],'timestamp':t0}
            self.logfile.write('%(timestamp)f: match %(quantity)s@%(price)s from %(seller)s(%(sell_oid)s) to %(buyer)s(%(buy_oid)s)\n' % match)
            self.logfile.flush()
            # in case of partial fills resubmit orders
            if b[QUANTITY] == matched_quantity: del bo[0]
            else: bo[0].update({QUANTITY:b[QUANTITY]-matched_quantity})
            if s[QUANTITY] == matched_quantity: del so[0]
            else: so[0].update({QUANTITY:s[QUANTITY]-matched_quantity})
            # return match
            return match

        matches, possible_matches = [], True

        def get(s,k): return s == [] and 1e100 or s[0][k]
        # loop until there are no macthes to perform
        while possible_matches:
            # try perform a match
            if get(lo_buy,PRICE) >= get(lo_sell,PRICE)  and \
                    get(lo_buy,OID)<get(mo_buy,OID) and \
                    get(lo_sell,OID)<get(mo_sell,OID):
                matches.append(match(lo_buy,lo_sell))
            elif get(lo_buy,OID)<get(mo_buy,OID) and mo_sell:
                matches.append(match(lo_buy,mo_sell))
            elif get(lo_sell,OID)<get(mo_sell,OID) and mo_buy:
                matches.append(match(mo_buy,lo_sell))
            elif mo_buy and mo_sell:
                matches.append(match(mo_buy,mo_sell))
            else:
                possible_matches = False
            # check if a stop order kicks in
            while so_buy and self.price <= so_buy[0][PRICE]:
                if so_buy[0][PRICE]: insert(lo_buy,so_buy[0],PRICE,1)
                else: mo_buy.append(so_buy[0])
                del so_buy[0]
                possible_matches = True
            while so_sell and self.price >= so_sell[0][PRICE]:
                if so_sell[0][PRICE]: insert(lo_sell,so_sell[0],PRICE,-1)
                else: mo_sell.append(so_sell[0])
                del so_sell[0]
                possible_matches = True
        return self.oid, matches


TEMPLATE = """
<!DOCTYPE>
<html>
  <head>
    <title>Sample test</title>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.4.2.min.js"></script>
  </head>
<body>
  <h1>Tornado Trading System: %(ticker)s</h1>
  <form method='POST' action='./'>
    <input ticker='order' id="order"/>
    <div><input type='submit'></div>
  </form>
  <pre id="log"></pre>
  <script type="text/javascript" charset="utf-8">
    $(document).ready(function(){
      $('form').submit(function(event){
        var value = $('#order').val();
        $.post("./", { order: value }, function(data){
          $("#order").val('');
        });
        return false;
      });
      if ("WebSocket" in window) {
         var ws = new WebSocket("ws://127.0.0.1:8888/realtime/");
         ws.onopen = function() {};
         ws.onmessage = function (evt) {
           var received_msg = evt.data;
           // var html = $("#log").html();
           // html = received_msg+html;
           $("#log").html(received_msg);
        };
        ws.onclose = function() {};
      } else {
        alert("WebSocket not supported");
      }
    });
  </script>
</body>
</html>
"""

LISTENERS = [] # queue of WebSocketHandler objects

class OrderHandler(tornado.web.RequestHandler):
    """ Hanles orders from clients  """
    def get(self):
        """ Handles GET request, sends back a POST form """
        try:
            self.post() ### for benchmarks
        except: pass
        self.write(TEMPLATE % dict(ticker=engine.ticker))

    def post(self):
        """ Handles POST request, proceses order then sends message to client """
        if hmac_key and not 'signature' in self.request.arguments: return
        if 'order' in self.request.arguments:
            order = self.request.arguments['order'][0].strip()
            if hmac_key:
                signature = self.request.arguments['signature'][0]
                if not hmac.new(hmac_key,order).hexdigest()==signature: return
            oid,matches = engine.process(order)
            if oid:
                message = prettyprint(oid,order,matches,engine.state())
                message = repr({'oid':oid,'order':order,'state':engine.state(),'matches':matches})
                for client in LISTENERS: client.write_message(message)
                self.write(str(oid))

class QuoteHandler(tornado.web.RequestHandler):
    """ Handler to send quote price to clients  """
    def get(self):
        """Handles GET request, sends back ticker price"""
        self.write(str(engine.price))

class QueryHandler(tornado.web.RequestHandler):
    """ Handler to sends current information of the security """

    def get(self):
        """Sends current state of the engine"""
        self.write(repr(engine.state()))

class RealtimeHandler(tornado.websocket.WebSocketHandler):
    """ a Websocket handler to communicate with clients using Websocket protocol """

    def check_origin(self, origin):
        """
        Accepts all cross-origin traffic
        :param origin: is the value of the ``Origin`` HTTP header, the url responsible for initiating this request.
        .. seealso:: `~WebSocketHandler.check_origin <http://www.tornadoweb.org/en/stable/_modules/tornado/websocket.html#WebSocketHandler.check_origin>`
        """
        return True

    def open(self):
        """ Adds RealtimeHandler instance to the queue when new websocket is connected"""
        LISTENERS.append(self)
        print 'client connected via websocket'

    def on_message(self, message):
        """
        Handle incoming messages on the WebSocket
        :param str message: the message to response
        """
        pass

    def on_close(self):
        """ remove RealtimeHandler instance when websocket is closed """
        LISTENERS.remove(self)
        print 'client disconnected'


if __name__ == "__main__":
    usage = "matchingserver -p 8888 -t intc"
    version= ""
    parser = optparse.OptionParser(usage, None, optparse.Option, version)
    parser.add_option('-p',
                      '--port',
                      default='8888',
                      dest='port',
                      help='socket')
    parser.add_option('-t',
                      '--ticker',
                      default='intc',
                      dest='ticker',
                      help='ticker name')
    (options, args) = parser.parse_args()
    urls=[
        (r'/', OrderHandler),
        (r'/quote', QuoteHandler),
        (r'/query', QueryHandler),
        (r'/realtime', RealtimeHandler)]
    engine = Engine(options.ticker)
    application = tornado.web.Application(urls, auto_reload=True)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(int(options.port))
    tornado.ioloop.IOLoop.current().start()
