# -*- coding: utf-8 -*-

'''
Created on 03.06.2011

@author: alexander
'''

import re, threading, time
import urllib.request, urllib.parse
import http.cookiejar
import random

from VillageHandler import VillageHandler
from DKNotificator import Notificator

class MainAPI:
    
    def __init__(self, kreuzcookie, sessionid, userid, server):
                
        self.userAgent = 'Mozilla/5.0 (X11; U; Linux i686; de; rv:1.9) Gecko/2008060309 Firefox/3.0'
        self.basehost = server + '.die-kreuzzuege.de'
        
        self.dkServer = server;
        
        self.tempVillageID = ''
        self.userID = userid
        
        self.cookiejar = http.cookiejar.CookieJar()
        
        if kreuzcookie != None:
            cookie = http.cookiejar.Cookie(version=0, name='kreuzcookie', value=kreuzcookie, port=None, 
                                           port_specified=False, domain=self.basehost, 
                                           domain_specified=True, domain_initial_dot=False, 
                                           path='/', path_specified=True, secure=False, expires=None, 
                                           discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, 
                                           rfc2109=False)
            self.cookiejar.set_cookie(cookie)
    
        if sessionid != None:    
            cookie = http.cookiejar.Cookie(version=0, name='sessionid', value=sessionid, port=None, 
                                           port_specified=False, domain=self.basehost, 
                                           domain_specified=True, domain_initial_dot=False, 
                                           path='/', path_specified=True, secure=False, expires=None, 
                                           discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, 
                                           rfc2109=False)
            self.cookiejar.set_cookie(cookie)
    
        if userid != None:    
            cookie = http.cookiejar.Cookie(version=0, name='userid', value=userid, port=None, 
                                           port_specified=False, domain=self.basehost, 
                                           domain_specified=True, domain_initial_dot=False, 
                                           path='/', path_specified=True, secure=False, expires=None, 
                                           discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, 
                                           rfc2109=False)
            self.cookiejar.set_cookie(cookie)
        
        
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookiejar))
        urllib.request.install_opener(self.opener)
        self.opener.addheaders = [('User-agent', self.userAgent)]
        
        self.villageHandlers = {}
        self.villageThreads = {}
        
        self.NeedsDef = {}
        self.villageCoords = {}
        
        self.offVillages = []
        
        self.GameSpeed = 0
        
        self.RunApplication = True
        
        self.SleepStartHour = -1 # UTC, dst is always zero. so -2 for german time :)
        self.SleepDuration = 12
        
    def isOffVillage(self, villageID):
        if self.offVillages.count(int(villageID)) != 0:
            return True
        
        return False
    
    def standardLogin(self, Username, Password):
        self.request("http://" + self.basehost + "/index.php")
        
        params = {}
        
        params["name"] = Username
        params["passwort"] = Password
        params["server"] = self.dkServer
        
        source = self.request("http://" + self.basehost + "/index.php?action=login", params)
        
        if source.find('pageGeneration') != False:
            m = self.regex(source, '\?village=([0-9]+)&action=info_player')
            if len(m) == 0:
                self.putLog('Account hooking failed!')
                return False
            self.tempVillageID = m[0]

            m = self.regex(source, '\?village=[0-9]+&action=info_player&id=([0-9]+)')
            if len(m) == 0:
                self.putLog('Account hooking failed! No UserId')
                return False
            self.userID = str(m[0])
            
            self.putLog('Hooked into account! Start VID: ' + str(self.tempVillageID) + ' UserID: ' + self.userID)
            return True
        
        else:
            self.putLog('Account hooking failed!')
        
        
    def makeLogin(self):
        source = self.request("http://" + self.basehost + "/game.php")
        
        sleepSecs = self.sleepCheck(source);
        if sleepSecs != 0:
            time.sleep(sleepSecs)
            source = self.request("http://" + self.basehost + "/game.php")
        
        if source.find('pageGeneration') != False:
            m = self.regex(source, '\?village=([0-9]*)&action=info_player')
            
            if len(m) == 0:
                self.putLog('Account hooking failed!')
                return False
            
            self.tempVillageID = m[0]
            
            self.putLog('Hooked into account! Start VID: ' + str(self.tempVillageID))
            return True
        
        else:
            self.putLog('Account hooking failed!')
            return False
        
    def startNotificator(self):
        Notify = Notificator(self)
        NotificatorThread = threading.Thread(group=None, target=Notify.loop, name='Notificator Thread', args=(), kwargs={})
        NotificatorThread.start()
        
    def getVillages(self):
        source = self.request("http://" + self.basehost + "/game.php?village=" 
                                        + str(self.tempVillageID)
                                        + "&action=info_player&id="
                                        + str(self.userID))
        
        m = self.regex(source, '\?village=[0-9]*&action=info_village&id=([0-9]*)')
        
        for villageID in m:
            
            if self.villageThreads.get(villageID, False) == False:
                self.tempVillageID = villageID
                
                self.villageHandlers[villageID] = VillageHandler(self, villageID, self.userID)
                
                self.villageThreads[villageID] = threading.Thread(group=None, target=self.villageHandlers[villageID].loop, name='Village #'+str(villageID), args=(), kwargs={})
                self.villageThreads[villageID].start()
                
            else:
                if (self.villageThreads[villageID].is_alive() != True):
                    self.villageHandlers[villageID].KeepAlive = False
                    self.NeedsDef[villageID] = False
                    self.putLog(str(villageID) + "'s workerthread crashed. restarting...")
                    
                    self.villageHandlers[villageID] = VillageHandler(self, villageID, self.userID)
                
                    self.villageThreads[villageID] = threading.Thread(group=None, target=self.villageHandlers[villageID].loop, name='Village #'+str(villageID), args=(), kwargs={})
                    self.villageThreads[villageID].start()
                
        doLater = []
        for runningVID in self.villageThreads.keys():
            if m.count(runningVID) == 0:
                self.putLog(str(runningVID) + " doesn't exists anymore. Killing Village Worker Thread!")
                self.NeedsDef[str(runningVID)] = False
                self.villageHandlers[runningVID].KeepAlive = False
                doLater.append(lambda: self.villageHandlers.pop(villageID))
                doLater.append(lambda: self.villageThreads.pop(villageID))
        for action in doLater:
            action()

    def putLog(self, text):
        print('[' + time.strftime("%H:%M:%S", time.gmtime()) + ' DKBOT] ' + text)
        
    def sleepCheck(self, source):
        if source.find('<h3 class=error>Du schläfst !</h3>') != -1:
            m = self.regex(source, '\(([0-9]*):([0-9]*):([0-9]*)\)')
            
            print(m);
            
            if len(m) > 0:
                seconds = int(m[0][0]) * 60 * 60 + int(m[0][1]) * 60 + int(m[0][2]) + random.randint(20, 40);
                hours = seconds / 3600
                self.putLog("Sleep-mode active. Sleep " + str(seconds) + " seconds (" + str(hours) + " hours) until it's off and try again...")
                return seconds
            
        return 0
            
    def regex(self, source, expr):
        compiled = re.compile(expr)
        result = compiled.findall(source)
        return result
        
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
            
        except:
            
            if internalCount >= 10:
                self.putLog("[error] connection error. returning ''");
                return ""
            
            self.putLog("[error] connection error. Sleeping " + str(internalCount) +  " seconds.")
            time.sleep(internalCount)
            data = self.request(url, params, noencode, internalCount+1)
        
        return data
