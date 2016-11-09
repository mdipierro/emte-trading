#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import random
import string
import os
import subprocess
import time

def register_user(name,is_manager=False):
    balance = round(random.randint(1,100)*1000.00, 2)
    if db(db.auth_user.username == name).count() < 1:
        db.auth_user.insert(username=name,
                    first_name=name,
                    last_name=name,
                    email='{}@web2py.com'.format(name),
                    password=db.auth_user.password.validate(name)[0],
                    manager=is_manager,
                    actual_cash=balance,
                    virtual_cash=balance)
        db.commit()
        print 'Register user: ', name

def register_product(ticker, port ,managerid):
    price = round(random.uniform(100,200),2)
    if db(db.product.name == ticker).count() < 1:
        db.product.insert(name=ticker,
                          description=ticker,
                          unit_price=price,
                          post_url='http://127.0.0.1:{}'.format(port),
                          quote_url='http://127.0.0.1:{}/quote'.format(port),
                          ws_url='ws://127.0.0.1:{}/realtime'.format(port),
                          modified_by = managerid,
                          created_by=managerid)
        db.commit()
        print 'Register ticker: {} at port {}'.format(ticker,port)

random.seed(1)
register_user('manager1', is_manager=True) # signup manager
# Signup traders
traders=['trader{}'.format(i) for i in xrange(1,10)]
for trader in traders:
    register_user(trader)

random.seed(5)
tickers_ports = {''.join(random.choice(string.ascii_lowercase) for _ in range(4)):port for port in random.sample(range(9000,10000),10)}

# register product
managerid = db.auth_user(username='manager1').id
for ticker,port in tickers_ports.items():
    register_product(ticker,port,managerid)

owners = [db.auth_user(username=trader).id for trader in traders]
for ticker,port in tickers_ports.items():
    matchingserver_cmd = 'python applications/emte/modules/matchingserver.py -p {} -t {} -f applications/{}/modules/{}.log'.format(port,ticker,request.application,ticker)
    robot_cmd1 = 'python applications/emte/modules/robot_trader.py -p {} -o {} -w 1.0'.format(port, owners[random.randint(0,len(owners)-1)])
    robot_cmd2 = 'python applications/emte/modules/robot_trader.py -p {} -o {} -w 1.0'.format(port, owners[random.randint(0,len(owners)-1)])
    log_cmd = 'python web2py.py -S {} -M -R applications/{}/modules/log2db.py -A {}'.format(request.application,request.application,ticker)
    with open(os.devnull,'w') as devnull:
        process1 = subprocess.Popen(matchingserver_cmd, shell=True,  preexec_fn=os.setsid, stdout=devnull)
        print "Running matchingserver for {} at port {}".format(ticker,port)
        time.sleep(2)
        process2 = subprocess.Popen(robot_cmd1, shell=True, preexec_fn=os.setsid, stdout=devnull)
        print "Running robot trader 1"
        process3 = subprocess.Popen(robot_cmd2, shell=True, preexec_fn=os.setsid, stdout=devnull)
        print "Running robot trader 2"
        process4 = subprocess.Popen(log_cmd, shell=True, preexec_fn=os.setsid, stdout=devnull)
        print "Running logging utilities for ", ticker
