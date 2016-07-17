#
# Guerrilla Mail Client
#

import json
from Browser import Browser

class GuerrillaMail(object):
    email = None

    def __init__(self):
        self.browser = Browser()

        data = self.browser.request('http://api.guerrillamail.com/ajax.php?f=get_email_address&ip=127.0.0.1&agent=Firefox')
        if data == "":
            return None
        parsed = json.loads(data)
        self.email = parsed['email_addr']

    def getEmails(self):
        data = self.browser.request('http://api.guerrillamail.com/ajax.php?f=check_email&seq=0')
        if data == "":
            return None
        parsed = json.loads(data)
        return parsed['list']

    def fetchEmail(self, emailId):
        data = self.browser.request('http://api.guerrillamail.com/ajax.php?f=fetch_email&email_id=' + emailId)
        if data == "":
            return None
        return json.loads(data)

    def removeSelf(self):
        self.browser.request('http://api.guerrillamail.com/ajax.php?f=forget_me&email_id=' + self.email)

#g = GuerrillaMail()
#print(g.email)
#g.getEmails()
#g.fetchEmail("1")