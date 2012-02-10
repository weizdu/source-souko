import mechanize
import re
import getopt, sys

################################################
# This is the AirStation log File.
#       Model   = WHR-G301N Ver1.70
#       Model   = WZR-HP-G302H Ver1.81

def fetchLog(url, userName, password):

    try:
        br = mechanize.Browser()
        br.add_password(url, userName, password)

        resp = br.open(url + 'cgi-bin/cgi?req=frm&frm=log_disp.html')
        br.select_form(nr=1)
        resp = br.submit()

        r =  resp.read()
        return r
    except mechanize._mechanize.FormNotFoundError:
        sys.exit()

def mergeLog(oldLog, newLog):
    r = ''
    oldLogLines = oldLog.split('\n')
    if len(oldLogLines)==0:
        oldLogLineTop = ''
    else:
        oldLogLineTop = oldLogLines[0]
        
    newLogLines = newLog.split('\n')

    for s in newLogLines:
        if oldLogLineTop == s:
#            print oldLogLines + ':' + s
            break
        else:
            r = r + s + '\n'

    return r + oldLog

def mergeLogBySet(oldLog, newLog):
    r = ''
    oldLogLines = oldLog.split('\n')
    newLogLines = newLog.split('\r\n')

    newLogLines = oldLogLines + newLogLines

    l = list(set(newLogLines))
    l.sort()
    return l

def mergeLogByDiffer(oldLog, newLog):
    r = ''
    oldLogLines = oldLog.split('\n')
    if len(oldLogLines)==0:
        oldLogLineTop = ''
    else:
        oldLogLineTop = oldLogLines[0]
        
    newLogLines = newLog.split('\n')

    import difflib
    d = difflib.Differ()
    result = list(difflib.unified_diff(oldLogLines, newLogLines))
    from pprint import pprint
    pprint(result)
    
    for s in newLogLines:
        if oldLogLineTop == s:
#            print oldLogLines + ':' + s
            break
        else:
            r = r + s + '\n'

    return r + oldLog

ouiCache = {}

def searchOUI(machex, ouiLines):
    if ouiCache.has_key(machex):
        return ouiCache[machex]
    
    for i in ouiLines:
        if i.find(machex) > -1:
            company = i.split('\t')[1]
            ouiCache[machex] = company
            return company

    return False

def countMAC(log):
    cLog = {}
    r = re.compile('.+ ([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}).*')
#    r = re.compile('.+ WIRELESS .+([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}).*')
    for i in log:
        result = r.match(i)
        if result:
            if cLog.has_key(result.group(1)):
                cLog[result.group(1)] = cLog[result.group(1)] + 1
            else:
                cLog[result.group(1)] = 1

    return cLog

def appendCompany(log):

    ouiLines = ''
    
    try:
        ouiLines = open('oui2.txt').read().split('\n')
    except:
        return log

    newLog = []
    r = re.compile('.+ ([0-9a-f]{2}):([0-9a-f]{2}):([0-9a-f]{2}):[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}.*')
    for i in log:
        result = r.match(i)
        if result:
            comp = result.group(1).upper() + '-' + result.group(2).upper() + '-' + result.group(3).upper()
            company = searchOUI(comp,ouiLines)
            if company:
                newLog.append(i + ' (' + company + ')')
            else:
                print comp
    return newLog

def appendCount(log, count):
    newLog = []
    r = re.compile('.+ ([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}).*')
    for i in log:
        result = r.match(i)
        if result and count.has_key(result.group(1)):
            newLog.append(i + ' (' + str(count[result.group(1)]) + ')')
        else:
            newLog.append(i)
    return newLog


def usage():
    print "Usage: python fetchlog.py -u username -p password rooter_ip_address"
    print "       -c append CompanyName from MacAddress and Count appearence"
    print "example : python fetchlog.py -u root 192.168.11.1"
    
def main():

    loginName = 'root'
    password = ''
    routerUrl = ''
    appendCompanyFlag = False
    
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:p:c", ["user", "password"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-u", "--user"):
            loginName = a
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        if o in ("-p", "--password"):
            password = a
        if o in ("-c"):
            appendCompanyFlag = True

    if args:
        ipAdress = args[0]
        routerUrl = 'http://' + ipAdress + '/'
    else:
        usage()
        sys.exit()

    try:
        f = open(ipAdress + '.log', 'r')
        oldLog = f.read()
        f.close()
    except IOError:
        print 'Log init...'
        oldLog = ''

    newLog = fetchLog(routerUrl, loginName, password)
    mergedLog = mergeLogBySet(oldLog, newLog)
    count = countMAC(mergedLog)
    
    f = open(ipAdress + '.log', 'w')
    f.write('\n'.join(mergedLog))
    f.close()

    if appendCompanyFlag:
        mergedLog = appendCompany(mergedLog)
        mergedLogWithCount = appendCount(mergedLog, count)

        for i in mergedLogWithCount:
            print i


if __name__ == "__main__":
    main()
