import sys
for i in xrange(10,0,-1):
    time.sleep(1)
    sys.stdout.write(str(i)+' ')
    sys.stdout.flush()

def timer():
  print 'tasks done, now sleeping for 10 seconds'
  for i in xrange(10,0,-1):
    time.sleep(1)
    print i