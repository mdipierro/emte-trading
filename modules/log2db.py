import sys, os, re, time, datetime

ticker=sys.argv[1]

print sys.argv

productid=db.product(name=ticker).id
filename=os.path.join('applications',request.application,'modules',ticker+'.log')
filenameidx=os.path.join('applications',request.application,'modules',ticker+'.idx')
re_match=re.compile('(?P<t>\d+(\.\d+)?)\: match (?P<q>\d+)\@(?P<p>\d+(\.\d+)?) from (?P<s>\d+)\((?P<si>\d+)\) to (?P<b>\d+)\((?P<bi>\d+)\)')

try:
    i=int(open(filenameidx,'rb').read())
except IOError:
    i=0

data = ''
while True:
    watcher = os.stat(filename)    
    j=watcher.st_size
    if j>i:
        file=open(filename,'rb')
        print 'loadin...'
        file.seek(i)
        data += file.read(j-i)
        file.read()
        i=j
        while True:
            match = re_match.search(data)
            if match:
                print match.group()
                now=datetime.datetime.now()
                quantity=int(match.group('q'))
                price=float(match.group('p'))
                seller=match.group('s')
                buyer=match.group('b')
                amount=price*quantity
                db.match.insert(quantity=quantity,
                                product=productid,
                                price=price,
                                seller=seller,
                                buyer=buyer,
                                sell_oid=match.group('si'),
                                buy_oid=match.group('bi'),
                                match_time=match.group('t'),
                                created_on=now)
                db(db.auth_user.id==buyer).update(actual_cash=db.auth_user.actual_cash-amount)
                db(db.auth_user.id==seller).update(actual_cash=db.auth_user.actual_cash+amount)
                db.commit()
                data=data[match.end():]
                open(filenameidx,'wb').write(str(i))
            else:
                break
        time.sleep(0.01)
