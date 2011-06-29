import urllib2, sys, json
from StringIO import StringIO
from xml.dom.minidom import parse, parseString

import xml

def getXmlString(url):
    response = urllib2.urlopen(url)
    return StringIO(response.read())

def elementtodict(parent):
    child = parent.firstChild
    if (not child):
        return None
    elif (child.nodeType == xml.dom.minidom.Node.TEXT_NODE):
        return child.nodeValue

    d={}
    while child is not None:
        if (child.nodeType == xml.dom.minidom.Node.ELEMENT_NODE):
            try:
                d[child.tagName]
            except KeyError:
                d[child.tagName]=[]
            d[child.tagName].append(elementtodict(child))
        child = child.nextSibling
    return d

class HiphopStats:

    def __init__(self, server, port):
        self.server = server
        self.port = port

    def getLatestInfo(self):
        """gets the data from the current time interval"""
        stats = getXmlString("http://%s:%s/stats.xml?from=-600" % (self.server, self.port))
        dom = parse(stats)
        slots = dom.getElementsByTagName("slot")
        lastSlot = slots[-1]
        stats = {}
        pages = lastSlot.getElementsByTagName("page")
        for page in pages:
            entries = page.getElementsByTagName("entry")
            stat = {}
            stat["code_200"] = 0
            stat["code_500"] = 0
            stat["page.cpu.all"] = 0
            for entry in entries:
                entry = elementtodict(entry)
                name = entry['key'][0]
                value =  entry['value'][0]
                if name == 'url':
                    #scriptname = value.split("/")[-1][0:-4]
                    scriptname = value
                    stat['name'] = value
                elif name == 'code':
                    code = value
                else:
                    stat[name] = int(value)

            stat["code_%s" % (code, )] = stat["hit"]

            if scriptname in stats:
                statWithSameName = stats[scriptname]
                for keyName, value in stat.iteritems():
                    if keyName[0:3] == 'code':
                        statWithSameName[keyName] = value
                    elif keyName == 'name':
                        pass
                    else:
                        if statWithSameName.has_key(keyName):
                            statWithSameName[keyName] = statWithSameName[keyName] + value
                        else:
                            statWithSameName[keyName] = value
            else:
                stats[scriptname] = stat

        return stats


def main(argv):
    stats = HiphopStats(argv[0])
    print stats.getLatestInfo()

if __name__=='__main__':
    main(sys.argv[1:])
