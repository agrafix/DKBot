from Guerrilla import GuerrillaMail

from Browser import Browser
import time
import re

class DKRegister(object):
    def __init__(self, username, password, server):
        self.browser = Browser()
        self.mail = GuerrillaMail()
        self.username = username
        self.password = password
        self.server = server

    def register(self):
        if self.mail.email == None:
            return False
        params = {
            "name": self.username,
            "mail": self.mail.email,
            "password": self.password,
            "password2": self.password,
            "AGB": "on",
            "submit": "Anmelden",
            "server": self.server + "."
        }
        self.browser.request('http://' + self.server + '.die-kreuzzuege.de/index.php?register=true&action=adduser&refid=&language=de', params)
        return True

    def activate(self, maxTries=5):
        allMail = self.mail.getEmails()
        dkId = None
        for mail in allMail:
            if "die-kreuzzuege" in mail['mail_from']:
                dkId = mail['mail_id']
                break
        if dkId == None:
            if maxTries == 0:
                print("Damn, retried too much! Activation failed.")
                return False
            print("No activation mail recieved yet. Retrying in 10 secs!")
            time.sleep(10)
            return self.activate(maxTries-1)
        else:
            activationMail = self.mail.fetchEmail(dkId)
            self.mail.removeSelf()
            if activationMail == None:
                print("Damn, invalid activation mail :-(")
                return False
            else:
                compiled = re.compile('http://[a-z]*\.die-kreuzzuege\.de//activate\.php\?id=([0-9]+)&amp;code=([0-9]+)')
                m = compiled.search(activationMail['mail_body'])
                if m == None:
                    print("Did not found activation link!")
                    return False
                else:
                    aid = m.group(1)
                    code = m.group(2)
                    res = self.browser.request('http://' + self.server + '.die-kreuzzuege.de/activate.php?id=' + aid + "&code=" + code)
                    return (res.find("freigeschaltet") >= 0)

#reg = DKRegister("nanosimbawa", "sananosimbawa1", "speed")
#reg.register()      
#reg.activate()