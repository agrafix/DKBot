'''
Created on 01.07.2011

@author: alexander
'''

import time, random

class Notificator:
    
    def __init__(self, GameAPI):
        
        self.GameAPI = GameAPI
        
        self.KeepAlive = True
        
        
    def loop(self):
        
        self.GameAPI.putLog("Notificator and Defmanager Started")
        
        self.GameAPI.putLog("Sleemode Settings: Activate at " + str(self.GameAPI.SleepStartHour) + " hour for " + str(self.GameAPI.SleepDuration) + " hours")
        
        while self.KeepAlive:
            self.check()
            
            st = random.randint(50, 100) / 10
            st /= (self.GameAPI.GameSpeed / 1000)
            
            time.sleep(st)
            
    def activateSM(self, duration):
        source = self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.GameAPI.tempVillageID) + "&action=settings")
         
        if source.find("command=sleep") != -1:
            params = {}
            
            params["sleeptime"] = str(duration)
             
            rply = self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.GameAPI.tempVillageID) + "&action=settings&command=sleep", params)
            
            if rply.find("h2 class='error'") == -1:
                self.GameAPI.putLog("sleepmode activated!")
                return True
        
        return False
        
    def check(self):
        
        # check if i need to activate sleep mode
        if self.GameAPI.SleepStartHour != -1 and self.GameAPI.SleepStartHour == int(time.strftime("%H", time.gmtime())):
            if self.activateSM(self.GameAPI.SleepDuration):
                self.GameAPI.SleepStartHour = -1
        
        source = self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.GameAPI.tempVillageID) + "&action=villages")
        
        sleepSecs = self.GameAPI.sleepCheck(source)
        
        if sleepSecs != 0:
            time.sleep(sleepSecs)
            source = self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.GameAPI.tempVillageID) + "&action=villages")
        
        
        # check for reports
        if source.find("graphic/new_report.gif") != -1:
            self.GameAPI.putLog("new report")
            self.GameAPI.getVillages()
            self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.GameAPI.tempVillageID) + "&action=report")
            
        
        # check for attacks
        villageTableMatches = self.GameAPI.regex(source, "<div class='buildingTitle'>Burgen</div><div class=.buildingRest.><div class='selectorRest'><table class='vis'>(.*?)</table></div></div></div>")
        
        if len(villageTableMatches) > 0:
            lines = villageTableMatches[0].split("</tr><tr>")
            
            for line in lines:
                match = self.GameAPI.regex(line, "game\.php\?village=([0-9]*)&action=overview'>[^\(]* \(([-]?[0-9]*)\|([-]?[0-9]*)\)</a>")
                
                if len(match) != 0:
                    
                    self.GameAPI.villageCoords[match[0][0]] = {'x': int(match[0][1]), 'y': match[0][2]}
                    
                    if line.find("graphic/attack.gif") != -1:
                        self.GameAPI.putLog("Village " + match[0][0] + " in serious troubles")
                        self.GameAPI.NeedsDef[match[0][0]] = True
                    else:
                        self.GameAPI.NeedsDef[match[0][0]] = False
        
            