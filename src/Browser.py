import time
import urllib.request, urllib.parse
import http.cookiejar

class Browser:
    def __init__(self):
        self.userAgent = 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9) Gecko/2008060309 Firefox/3.0'
        self.cookiejar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
        urllib.request.install_opener(self.opener)
        self.opener.addheaders = [('User-agent', self.userAgent)]
    def request(self, url, params={}, noencode=False, internalCount=1):
        data = ""
        try:
            if len(params) != 0:
                if noencode:
                    req = params["query"].encode('utf-8')
                else:
                    req = urllib.parse.urlencode(params).encode('utf-8')
                sock = self.opener.open(url, req)
            else:
                sock = self.opener.open(url)
                
            data = sock.read().decode('utf-8')
            sock.close()
        except Exception as inst:
            if internalCount >= 10:
                return ""
            print("[Browser] something bad happened while requesting '" + url + "' Will try again!")
            print(inst)
            time.sleep(internalCount)
            data = self.request(url, params, noencode, internalCount+1)
        
        return data
