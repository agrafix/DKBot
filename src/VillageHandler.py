'''
Created on 30.06.2011

@author: alexander
'''

from DKBuilder import Builder
from DKTrain import Train
from DKAttack import Attack
from DKTech import Tech

import time, random

class VillageHandler:
    
    def __init__(self, GameAPI, VillageID, PlayerID):
        
        self.GameAPI = GameAPI
        self.VillageID = VillageID
        self.PlayerID = PlayerID
        
        self.builder = Builder(self, GameAPI)
        self.train = Train(self, GameAPI)
        self.attack = Attack(self, GameAPI)
        
        self.tech = Tech(self, GameAPI)
        
        self.CanBuildSettler = True
        
        self.KeepAlive = True

    def writeLog(self, msg):
        self.GameAPI.putLog("[VillageHandler@VID" + str(self.VillageID) + "] " + msg)
        
    def loop(self):
        # main loooop
        
        self.writeLog("Started VillageHandler")
        self.GameAPI.NeedsDef[str(self.VillageID)] = False

        while self.KeepAlive:
            self.builder.run()
            
            tryBuildingSettler = False
            if self.CanBuildSettler == True and self.builder.buildings.get('missio', 'd') != 'd' and self.builder.buildings['missio']['level'] >= 1 and self.builder.buildings['missio']['inloop'] == False:
                # try to build settler
                self.writeLog("Will try to build a settler")
                tryBuildingSettler = True
                self.train.settlerRun()
            
            if self.builder.hasBuilt and not tryBuildingSettler:
                if self.builder.buildings['farm']['level'] >= 29:
                    if self.CanBuildSettler and (self.builder.buildings.get('missio', 'd') == 'd' or self.builder.buildings['missio']['level'] < 2):
                        self.writeLog("Won't build any more units until settler is built!")
                    else:
                        self.train.run()
                else:
                    self.train.run()

            if self.builder.shouldTech:
                if self.GameAPI.isOffVillage(self.VillageID) == False:
                    self.tech.run(['pike', 'schild', 'skav', 'foot', 'horses'])
                else:
                    self.tech.run(['berserk', 'shkav', 'kata', 'turm', 'foot', 'horses', 'wheels'])
                
            self.attack.run()
            
            # check if another village needs defense
            if self.GameAPI.NeedsDef.get(str(self.VillageID), False):
                self.writeLog("pulling back defenses")
                self.attack.PullBackAllDefense()
            else:
                for dvid in self.GameAPI.NeedsDef.keys():
                    state = self.GameAPI.NeedsDef[dvid]
                    
                    if state == True and str(dvid) != str(self.VillageID):
                        self.writeLog("sending defenses for " + str(self.GameAPI.villageCoords[str(dvid)]['x']) + "|" + str(self.GameAPI.villageCoords[str(dvid)]['x']))
                        self.attack.PutAllDefenseTo(self.GameAPI.villageCoords[str(dvid)]['x'], self.GameAPI.villageCoords[str(dvid)]['y'])
            
            sl = random.randint(50, 100) / 10
            sl /= (self.GameAPI.GameSpeed / 1000)
            time.sleep(sl)
            
        self.wroteLog("KILLED VillageHandler")
        
    
    def getHeartbeat(self):
        
        heartbeat = self.xajax("getHeartbeat", ())
        beat = 0
        
        m = self.GameAPI.regex(heartbeat, 'heartbeat=([0-9]*)')
        if (len(m) != 0):
            beat = int(m[0])
            return beat
            
        return 0
        
    def xajax(self, cmd, input):
        params = {'query': ""}
        
        params["query"] += "xajax=" + cmd + "&"
        params["query"] += "xajaxr=" + str(int(time.time())) + "&"
        
        for inp in input:
            params["query"] += "xajaxargs[]=" + str(inp) + "&"
        
        return self.GameAPI.request("http://" + self.GameAPI.basehost + "/game_ajax.php", params, True)
        
    def screen(self, name, postData={}, NoEncoding=False):
        source = self.GameAPI.request("http://" + self.GameAPI.basehost + "/game.php?village=" + str(self.VillageID) + "&action=" + name, postData, NoEncoding)
        
        if source.find('statusbar statusbarattacked') != -1:
            self.GameAPI.NeedsDef[str(self.VillageID)] = True
            
        sleepSecs = self.GameAPI.sleepCheck(source)
        
        if sleepSecs != 0:
            time.sleep(sleepSecs)
            self.screen(name, postData, NoEncoding)
        
        return source