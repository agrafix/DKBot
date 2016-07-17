'''
Created on 30.06.2011

@author: alexander
'''

import time, random

class Attack:
    
    def __init__(self, VillageHandler, GameAPI):
        self.VillageHandler = VillageHandler
        self.GameAPI = GameAPI
        
        self.units = {}
        
        self.unitnames = 'pike;schild;schwert;berserk;spy;esel;lkav;skav;shkav;kata;turm;schiff;siedler;missio;hero'.split(";")
        
        self.x = 0
        self.y = 0

    def writeLog(self, msg):
        self.GameAPI.putLog("[Attack@VID" + str(self.VillageHandler.VillageID) + "] " + msg)        
        
    def run(self):
        
        screen = self.VillageHandler.screen("versammlung")
        
        matches = self.GameAPI.regex(screen, 'village=[0-9]*&action=villages" class="villageNameLink">[^<]*</a> \(([-]?[0-9]*)\|([-]?[0-9]*)\)</div>')
        
        if len(matches) == 0:
            return False
        
        self.x = int(matches[0][0])
        self.y = int(matches[0][1])
            
        matches = self.GameAPI.regex(screen, 'javascript:setValues\("units\[\]","([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*),([0-9]*)"\);')
            
        if len(matches) == 0:
            return False
        
        i = 0
                
        for unit in self.unitnames:
            self.units[unit] = int(matches[0][i])
            i += 1
                
        
        if self.units["siedler"] >= 1:
            directions = []
            for dx in range(-4, 4):
                for dy in range(-4, 4):
                    if not (dx == 0 and dy == 0):
                        directions.append((dx, dy))
            for dir in directions:
                if self.sendAway(self.x+dir[0], self.y+dir[1], "settle", {'siedler':1}):
                    self.writeLog("Settled. Waiting 20 secs, then going again :)")
                    time.sleep(random.randint(190,210) / 10)
                    self.GameAPI.getVillages()
                    break
                
                
    def PullBackAllDefense(self):
        
        screen = self.VillageHandler.screen("versammlung&mode=units")
        
        tableMatches = self.GameAPI.regex(screen, "<h3>Truppen in anderen Burgen</h3><table class='vis'><tr><td colspan=18 align=right>weiterschicken</td></tr><tr><td colspan=16 align=right>Zurückschicken</td><td>[^<]*</td><td>[^<]*</td></tr>(.*?)</table>")
        
        if len(tableMatches) == 0:
            return False
        
        lines = tableMatches[0].split("</tr><tr>")
        
        for line in lines:
            matches = self.GameAPI.regex(line, "<form action='game\.php\?village=[0-9]*&action=versammlung&mode=command&id=([0-9]*)' method='POST'><input type='hidden' name='command' value='back'>")
        
            if len(matches) != 0:
                cmdID = int(matches[0])
                
                sendAway = {}
                unitmatches = self.GameAPI.regex(line, "<td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td>")
                
                
                i = 0
                
                for unit in self.unitnames:
                    sendAway[unit] = int(unitmatches[0][i])
                    i += 1
                    
                if self.sendAway(-1, -1, "back", sendAway, cmdID) == False:
                    self.writeLog("Failed pulling back units")
                    
                    
    def PutAllDefenseTo(self, x, y):
        
        # send all availible shit
        if (self.units["pike"] + self.units["schild"] + self.units["skav"]) > 200:
            self.writeLog("defending " + str(x) + "|" + str(y))
            self.sendAway(x, y, "help", {"pike": self.units["pike"], "schild": self.units["schild"], "skav": self.units["skav"], "hero": self.units["hero"]})
        
        # now forward units
        screen = self.VillageHandler.screen("versammlung&mode=units")
        
        tableMatches = self.GameAPI.regex(screen, "<h3>Truppen in anderen Burgen</h3><table class='vis'><tr><td colspan=18 align=right>weiterschicken</td></tr><tr><td colspan=16 align=right>Zurückschicken</td><td>[^<]*</td><td>[^<]*</td></tr>(.*?)</table>")
        
        if len(tableMatches) == 0:
            return False
        
        lines = tableMatches[0].split("</tr><tr>")
        
        for line in lines:
            matches = self.GameAPI.regex(line, "<form action='game\.php\?village=[0-9]*&action=versammlung&mode=command&id=([0-9]*)' method='POST'><input type='hidden' name='command' value='back'>")
        
            if len(matches) != 0:
                cmdID = int(matches[0])
                
                sendAway = {}
                unitmatches = self.GameAPI.regex(line, "<td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td><td>([0-9]*)</td>")
                
                
                i = 0
                
                for unit in self.unitnames:
                    sendAway[unit] = int(unitmatches[0][i])
                    i += 1
                    
                targetMatches = self.GameAPI.regex(line, "game\.php\?village=[0-9]*&action=info_village&id=([0-9]*)")
                
                if len(targetMatches) != 0:
                    
                    if self.GameAPI.NeedsDef[targetMatches[0]] == False:
                    
                        if self.sendAway(x, y, "next", sendAway, cmdID) == False:
                            self.writeLog("Failed forwarding")
            
    def sendAway(self, x, y, type, sendAwayDict={}, id=0):
        
        idStr = ""
        
        if id != 0:
            idStr = "&id=" + str(id)
        
        if type == "back" or type == "next":
            screen = self.VillageHandler.screen("versammlung&mode=command" + idStr, {"command": type})
        else:
            screen = self.VillageHandler.screen("versammlung&mode=command" + idStr)
        
        if type == "back":
            xymatch = self.GameAPI.regex(screen, '\(([-]?[0-9]*)\|([-]?[0-9]*)\)</h1>')
            
            print(xymatch)
            
            if len(xymatch) == 0:
                return False
            
            x = int(xymatch[0][0])
            y = int(xymatch[0][1])
        
        matches = self.GameAPI.regex(screen, '<input type="hidden" name="id" value="([0-9]*)">')
        
        if len(matches) == 0:
            print("IDMATCH")
            return False
        
        cmdID = matches[0]
        
        unitStr = ""
        
        for unit in self.unitnames:
            if sendAwayDict.get(unit, 'd') == 'd' or sendAwayDict[unit] == 0:
                unitStr += "units[]=&"
            else:
                unitStr += "units[]=" + str(sendAwayDict[unit]) +"&"
        
        params = {}
        params["query"] = "command=&id=" + cmdID + "&" + unitStr + "command=" + str(type) + "&x=" + str(x) + "&y=" +str(y)
        
        reply = self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.VillageHandler.VillageID) + "&action=versammlung&mode=command&try=confirm", params, True)
        
        if reply.find('xajax_sendTroops') == -1:
            return False
        
        
        unitStr = ""
        for unit in self.unitnames:
            if  sendAwayDict.get(unit, 'd') == 'd' or sendAwayDict[unit] == 0:
                unitStr += ","
            else:
                unitStr += str(sendAwayDict[unit]) + ","
        
        
        s = self.VillageHandler.xajax('sendTroops', (self.VillageHandler.VillageID, x, y, type, unitStr, 0, 0, 0, 0, 0, 0, cmdID, self.VillageHandler.getHeartbeat()))
        
        if s.find('action=versammlung') != -1:
            self.writeLog("Send (" + type + ") units from " + str(self.VillageHandler.VillageID))
            return True
        
        print("GENERALERROR: " + s)
        return False
        