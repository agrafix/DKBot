'''
Created on 30.06.2011

@author: alexander
'''

class Train:
    
    def __init__(self, VillageHandler, GameAPI):
        self.VillageHandler = VillageHandler
        self.GameAPI = GameAPI

    def writeLog(self, msg):
        self.GameAPI.putLog("[Train@VID" + str(self.VillageHandler.VillageID) + "] " + msg)
        
    def settlerRun(self):
        
        self.build('missio', {'siedler': 1}, ('siedler', 'missio'))
        
    
    def build(self, building, unitDict, unitsAvailible):

        _buildunits = {}

        screen = self.VillageHandler.screen(building)
        
        matches = self.GameAPI.regex(screen, '<form action="game\.php\?village=[0-9]*&action='+building+'&command=train&bid=([0-9]*)" method="POST">')
        
        if len(matches) == 0:
            return False
        
        bid = matches[0]
        
        tableMatches = self.GameAPI.regex(screen, 'method="POST"><table class="vis buildingTable">(.*?)</table></form>')
        
        if len(tableMatches) == 0:
            return False
        
        rows = tableMatches[0].split("<tr><td><table><tr><td rowspan=2")
        
        for row in rows:
            
            infoMatches = self.GameAPI.regex(row, 'unit=([a-z]*)", 520, 520\).>[^<]*</a><font size=1> \(Stufe ([0-9]*)\)</font>')
            
            if len(infoMatches) != 0:

                _buildunits[infoMatches[0][0]] = {'internal': infoMatches[0][0], 'level': int(infoMatches[0][1]), 'max': -1}
                
                if infoMatches[0][0] == 'siedler':
                    if row.find('keine weiteren möglich') != -1:
                        self.VillageHandler.CanBuildSettler = False
                
                buildMatches = self.GameAPI.regex(row, '<input name="buildunit\[\]" type="text" size="5" maxlength="5">\(max\. ([0-9]*)\)')
                
                if len(buildMatches) != 0:
                    _buildunits[infoMatches[0][0]]["max"] = int(buildMatches[0])
        
        
        total = 0
        params = {}
        params["query"] = ""
        logstr = ""
                    
        for u in unitsAvailible:
            if unitDict.get(u, 'd') != 'd' and _buildunits.get(u, 'd') != 'd' and _buildunits[u]["level"] != 0 and _buildunits[u]["max"] > 0:
                amount = int(float(unitDict[u]) * _buildunits[u]["max"])
                total += amount
                
                logstr += str(amount) + " " + u + " "
                
                params["query"] += 'buildunit[]=' + str(amount) + '&'
                
            else:
                if _buildunits.get(u, 'd') != 'd' and _buildunits[u]["max"] != -1:
                    params["query"] += 'buildunit[]=&'
                
        if total > 0:
            params["query"] += "submit=Rekrutieren"  
            
            print(params["query"])
            
            r = self.VillageHandler.screen(building + "&command=train&bid=" + str(bid), params, True)
            
            self.writeLog("Trained " + logstr)
        
    def run(self):
        
        if self.GameAPI.isOffVillage(self.VillageHandler.VillageID) == False:
            self.build('barracks', {'pike': 0.33, 'schild': 0.33}, ('pike', 'schild', 'schwert', 'berserk'))
            self.build('stable', {'skav': 0.5}, ('spy', 'esel', 'lkav', 'skav', 'shkav'))
        else:
            self.build('stable', {'spy': 0.05, 'shkav': 0.23}, ('spy', 'esel', 'lkav', 'skav', 'shkav'))
            self.build('barracks', {'berserk': 0.33}, ('pike', 'schild', 'schwert', 'berserk'))
            self.build('garage', {'kata': 0.33, 'turm': 0.33}, ('kata', 'turm'))
                