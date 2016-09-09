import random, hmac, urllib, time, optparse

def robot_order(price,owner='1,2'):
    """
    submits buy and sell orders randomly
    Order price is fluctuated around quote price

    :param float price: The price gotten back from QuoteHandler.get
    :param str owner: a group/individual owner. Default is random owner
    :return: order information
    :rtype: str
    """
    owners=str(owner).split(',')
    owner=owners[random.randint(0,len(owners)-1)]
    i=random.randint(0,3)
    p=price
    if i is 1:
        p=p-abs(random.gauss(0,10)) # dollars
        if p<=20: p=20+abs(random.gauss(0,20))
    elif i is 3:
        p=p+abs(random.gauss(0,10)) # dollars
        if p>=180: p=180-abs(random.gauss(0,20))
    p = 0.01*int(p*100)
    n=random.randint(1,1000)   # shares
    if i==0: o='%s:buy %i@%s' % (owner,n,0)
    elif i==1: o='%s:buy %i@%s' % (owner,n,p)
    elif i==2: o='%s:sell %i@%s' % (owner,n,0)
    elif i==3: o='%s:sell %i@%s' % (owner,n,p)
    return o

def start_robot(url,owner=0,hmac_key='secret',wait_time=1):
    """
    Starts robot trader

    :param str url: the websocket url endpoint
    :param str hmac_key: the secrect key to encrypt signature
    :param int wait_time: the interval to submit new order
    """
    while True:
        t0 = time.time()
        price = float(urllib.urlopen(url+'/quote').read())
        order = robot_order(price,owner)
        signature = hmac_key and hmac.new(hmac_key,order).hexdigest() or ''
        params = urllib.urlencode({'order': order, 'signature': signature})
        f = urllib.urlopen(url, params)
        oid = int(f.read())
        print "order #%i from %s (%fseconds)" % (oid,order,time.time()-t0)
        time.sleep(float(wait_time))

if __name__=='__main__':
    usage = "robot_trader -p 8888 -o 0 -k <hmac_key>"
    version= ""
    parser = optparse.OptionParser(usage, None, optparse.Option, version)
    parser.add_option('-p',
                      '--port',
                      default='8888',
                      dest='port',
                      help='socket')
    parser.add_option('-o',
                      '--owner',
                      default='0',
                      dest='owner',
                      help='the user id of the robot')
    parser.add_option('-k',
                      '--hmac_key',
                      default='secret',
                      dest='hmac_key',
                      help='the hmac_key to sign orders')
    parser.add_option('-w',
                      '--wait_time',
                      default='1',
                      dest='wait_time',
                      help='time between two trades in seconds')
    (options, args) = parser.parse_args()
    start_robot('http://127.0.0.1:%s' % options.port,owner=options.owner,hmac_key=options.hmac_key,wait_time=options.wait_time)
