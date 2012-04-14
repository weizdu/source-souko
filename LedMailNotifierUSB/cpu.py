import time
import psutil
import sys
import setcolor

try:
    formercolor = 0
    interValSec = 1

    m = setcolor.MailNotifier()
        
    while True:
        cpu =  psutil.cpu_percent()
#        cpu =  psutil.cpu_percent(interval=interValSec, percpu=False)
        if cpu < 30:
            color = 1 #blue
    #        color = 0 #off
    #        color = 4 #cyan
    #        color = 5 #purple
    #        color = 6 #yellow
    #        color = 7 #white
        elif cpu < 60:
            color = 3 #green
        elif cpu <= 100:
            color = 2 #red

        if color != formercolor:
            m.setColor(color)
#        print cpu , color
        formercolor = color
        time.sleep(interValSec)
except:
    print sys.exc_info()[0], sys.exc_info()[1]
    m.setColor(0)
