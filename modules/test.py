import time
db=DAL()
db.define_table('a',Field('b'))
while True:
    t0=time.time()
    id=db.a.insert(b='x'*512)
    db.commit()
    print id, time.time()-t0
