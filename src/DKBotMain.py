'''
Created on 30.06.2011

@author: alexander
'''

from GameAPI import MainAPI
from DKRegister import DKRegister

import time
import json
import argparse
import random
import string
import os.path
import sys

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def main():
    parser = argparse.ArgumentParser()
    # create new
    parser.add_argument("-r", "--register", action="store_true", help="create a new account")
    parser.add_argument("--random-password", action="store_true", help="generate a random password for that account")

    # user login
    parser.add_argument("-u", "--username", type=str, help="username")
    parser.add_argument("-p", "--password", type=str, help="password")

    # cookie login
    parser.add_argument("--cookie-kreuzcookie", type=str, help="value of 'kreuzcookie'")
    parser.add_argument("--cookie-userid", type=str, help="value of 'userid'")
    parser.add_argument("--cookie-sessionid", type=str, help="value of 'sessionid'")

    # server settings
    parser.add_argument("-s", "--server", type=str, default="speed", help="server, eg 'speed'")
    parser.add_argument("-i", "--speed", type=int, default=4000, help="game speed")
    parser.add_argument("--sleep-start", type=int, default=7, help="start sleep mode at N hour of day")
    parser.add_argument("--sleep-duration", type=int, default=4, help="sleep N hours")

    # other settings
    parser.add_argument("--state-file", type=str, default="./state.json", help="location of state file")

    args = parser.parse_args()

    # state file
    stHasRegistered = False
    stRandomPassword = None
    if os.path.isfile(args.state_file):
        print("Reading state file at " + args.state_file)
        fp = open(args.state_file, 'r')
        content = json.load(fp)
        stHasRegistered = content['registered']
        stRandomPassword = content['password']
    else:
        print("No state file found. This is the first run?")

    def writeState(isRegistered, password):
        f = open(args.state_file, 'w')
        f.write(json.dumps({'registered': isRegistered, 'password': password}, sort_keys=True))
        f.close()

    # password check
    if args.password != None and stRandomPassword != None:
        if args.password != stRandomPassword:
            print("--password and password from state.json do not match!")
            sys.exit()

    # create new mode
    if args.register and not stHasRegistered:
        print("Registration flag set and no registration completed.")
        passToUse = None
        if args.password != None:
            passToUse = args.password
        if stRandomPassword != None:
            passToUse = stRandomPassword
        if passToUse == None:
            passToUse = id_generator(12)
        if args.username == None:
            print("No --username provided!")
            sys.exit()
        reg = DKRegister(args.username, passToUse, args.server)
        if not reg.register():
            print("Registration failed.")
            sys.exit()
        if not reg.activate():
            print("Activation failed")
            sys.exit()
        stRandomPassword = passToUse
        stHasRegistered = True
        writeState(True, passToUse)
        print("Created new account " + args.username + " with password " + passToUse)

    player = MainAPI(args.cookie_kreuzcookie, args.cookie_sessionid, args.cookie_userid, args.server)
    player.GameSpeed = args.speed
    player.SleepStartHour = args.sleep_start
    player.SleepDuration = args.sleep_duration

    go = False

    # user pass login
    if args.username != None and (args.password != None or stRandomPassword != None):
        passToUse = None
        if args.password != None:
            passToUse = args.password
        if stRandomPassword != None:
            passToUse = stRandomPassword
        print("Logging in normally")
        writeState(True, passToUse)
        if not player.standardLogin(args.username, passToUse):
            print("Failed to login.")
            sys.exit()
        go = True

    # session hook
    if args.cookie_kreuzcookie != None and args.cookie_sessionid != None and args.cookie_userid != None:
        if not player.makeLogin():
            print("Failed to hook cookie!")
            sys.exit()
        go = True

    if not go:
        print("Invalid invocation! Set all cookie args or a username, server and password or registration")
        sys.exit()

    print("Ready. Current hours of time is " + time.strftime("%H", time.gmtime()))
    player.startNotificator()
    player.getVillages()
    while player.RunApplication:
            time.sleep(5)
    player.putLog("Exit application.")

main()    