'''
Created on 01.07.2011

@author: alexander
'''

import random

class Tech:
    
    def __init__(self, VillageHandler, GameAPI):
        self.VillageHandler = VillageHandler
        self.GameAPI = GameAPI
        
        self.techIDs = {'pike': 1, 'schild': 2, 'schwert': 3, 'berserk': 11, 'spy': 4, 'lkav': 5, 'skav': 6, 'shkav': 16, 'turm': 9, 'kata': 8, 'foot': 12, 'horses':13, 'wheels':14}
        
    def writeLog(self, msg):
        self.GameAPI.putLog("[Tech@VID" + str(self.VillageHandler.VillageID) + "] " + msg)

    def run(self, unitArray):
        
        random.shuffle(unitArray)
        
        for unit in unitArray:
            if self.tech(unit):
                break
        
    def tech(self, unitname):
        
        unitid = self.techIDs[unitname]
        
        screen = self.VillageHandler.screen("blacksmith")
        
        if screen.find('blacksmith&command=research&id=' + str(unitid) + '">F') != -1:
            self.VillageHandler.screen("blacksmith&command=research&id=" + str(unitid))
            self.writeLog("Teched " + unitname)
            
            return True
        
        return False