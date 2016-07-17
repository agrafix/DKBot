'''
Created on 30.06.2011

@author: alexander
'''

class Builder:
    
    def __init__(self, VillageHandler, GameAPI):
        self.VillageHandler = VillageHandler
        self.GameAPI = GameAPI
        
        self.buildings = {}
        
        self.buildstr = 'versammlung:1;mines:10;headquater:5;barracks:3;mines:15;'
        self.buildstr += 'headquater:10;barracks:5;mines:20;headquater:15;barracks:10;wall:10;tower:5;'
        self.buildstr += 'mines:25;headquater:20;barracks:15;wall:15;mines:30;wall:20;tower:10;blacksmith:20;missio:2;market:1;'
        self.buildstr += 'headquater:25;barracks:25;stable:20;workshop:15;headquater:30;stable:25;workshop:25;storage:30;farm:30;end:0'
        
        self.buildtuple = self.buildstr.split(";")
        
        self.hasBuilt = False
        
        self.shouldTech = False

    def writeLog(self, msg):
        self.GameAPI.putLog("[Build@VID" + str(self.VillageHandler.VillageID) + "] " + msg)        
        
    def build(self, name):
        
        if self.buildings[name]["buildid"] == -1:
            return False
        
        self.writeLog("Will build " + name + " ID: " + str(self.buildings[name]["buildid"]))
        
        beat = self.VillageHandler.getHeartbeat()
        
        r = self.VillageHandler.xajax("buildBuilding", (self.VillageHandler.VillageID, self.buildings[name]["buildid"], beat, 1, 'headquater'))
        
        if r.find('builtID') != False:
            self.writeLog("Added " + name + " to the build queue")
            self.hasBuilt = True
            self.shouldTech = True
            return True
        
        return False
        
    def run(self):
        self.shouldTech = False
        self.hasBuilt = False
        
        screen = self.VillageHandler.screen("headquater")
        
        #&action=([a-z0-9]*)">([^<]*)</a>\s*\([A-Za-z]* ([0-9]*)\)</td><td id="[^<"]*">[0-9]*</td><td id=".*?">[0-9]*</td><td id=".*?">[0-9]*</td><td id=".*?">.*?</td><td><a href="" onclick="if \(heartbeat!=0\) xajax_buildBuilding\([0-9]*,([0-9]*)
        r = self.GameAPI.regex(screen, '&action=([a-z0-9]*)">([^<]*)</a>\s*\([A-Za-z]* ([0-9]*)\)</td>')
        
        # get building levels
        for match in r:
            self.buildings[match[0]] = {'name': match[1], 'internal': match[0], 'level': int(match[2]), 'buildid': -1, 'inloop': False}
            
            d = self.GameAPI.regex(screen, match[1] + '</a>\s*\([A-Za-z]* ([0-9]*)\)</td><td id="[^<"]*">[0-9]*</td><td id="[^"]*">[0-9]*</td><td id="[^"]*">[0-9]*</td><td id="[^"]*">[^<]*</td><td><a href="" onclick="if \(heartbeat!=0\) xajax_buildBuilding\([0-9]*,([0-9]*)')
            if len(d) != 0:
                self.buildings[match[0]]['level'] = int(d[0][0])
                self.buildings[match[0]]['buildid'] = int(d[0][1])
        
        buildLoopCounter = 0
            
        # buildloop
        for building in self.buildings.values():
            s = self.GameAPI.regex(screen, '><td>' + building['name'] + ' \([A-Za-z]* ([0-9]*)\)</td><td( id="timer0")*>[0-9]*')
            
            if len(s) > 0:
                buildLoopCounter += len(s)
                
                self.buildings[building['internal']]['level'] = int(s[len(s)-1][0])
                
                self.buildings[building['internal']]['inloop'] = True
        
        # check for lack of storage
        if screen.find('Speicher zu klein') != -1 and self.buildings['storage']['inloop'] == False:
            self.build("storage")
            
        # check for lack of farm
        m = self.GameAPI.regex(screen, '<div class="statusPeople"><img src="graphic/house\.gif" class="statusBarResImg">([0-9]*)/([0-9]*)</div>')
        if len(m) != 0:
            dif = (int(m[0][1]) - int(m[0][0]))
            if dif <= 20 and self.buildings['farm']['inloop'] == False: # to small, extend
                self.build("farm")
            
            elif dif >= (float(m[0][1]) * 0.5): # to mutch room, build units!!
                self.hasBuilt = True
                
        # if buildloopcounter to big chill
        if buildLoopCounter >= 4:
            self.hasBuilt = True
            return
                
        # now check the levels
        for line in self.buildtuple:
            p = line.split(":")
            
            if p[0] == "end":
                AllDone = True
                # check if still stuff to build :P
                for bcheck in self.buildings.values():
                    if bcheck["buildid"] != -1:
                        AllDone = False
                        self.build(bcheck["internal"])
                        break
                        
                if AllDone:
                    self.hasBuilt = True
                    self.shouldTech = True
                break
            
            if p[0] != "mines":
                if self.buildings.get(p[0], 'd') != 'd' and self.buildings[p[0]]['level'] < int(p[1]):
                    self.build(p[0])
                    break
                    
            else:
                smallest = min(self.buildings["wood"]["level"], self.buildings["stone"]["level"], self.buildings["iron"]["level"])

                if min(self.buildings["wood"]["level"], self.buildings["stone"]["level"], self.buildings["iron"]["level"]) < int(p[1]):
                    if self.buildings["storage"]["level"] < (smallest-3):
                        self.build("storage")
                        break
                    elif self.buildings["wood"]["level"] == smallest:
                        self.build("wood")
                        break
                    elif self.buildings["stone"]["level"] == smallest:
                        self.build("stone")
                        break
                    else:
                        self.build("iron")
                        break
                    