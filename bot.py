#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
origin:
http://xmpppy.sourceforge.net/examples/bot.py
'''

from init_env import USERNAME, PASSWORD, SERVER, PORT
from init_env import HANDLER

import pdb
import sys
import xmpp

########################### user handlers start ##################################
imp_handler = __import__(HANDLER)
commands = imp_handler.commands
i18n = imp_handler.i18n
########################### user handlers stop ###################################

############################ bot logic start #####################################

def message_callback(conn, msg):
    text = msg.getBody()
    user = msg.getFrom()
    user.lang = 'en'      # dup
    if text is None:
        return False
    if text.find(' ')+1: command, args = text.split(' ', 1)
    else: command, args = text, ''
    cmd = command.lower()

    if commands.has_key(cmd): 
    	try: reply = commands[cmd](user, command, args, msg)
        except Exception as e:
            reply = ("COMMAND ERROR", text)
            print "Error:%s" % (str(e))
    else: reply = ("UNKNOWN COMMAND", cmd)

    if type(reply) == type(()):
        key, args = reply
        if i18n[user.lang].has_key(key): pat = i18n[user.lang][key]
        elif i18n['en'].has_key(key): pat = i18n['en'][key]
        else: pat = "%s"
        if type(pat) == type(''): reply = pat%args
        else: reply = pat(**args)
    else:
        try: reply = i18n[user.lang][reply]
        except KeyError:
            try: reply = i18n['en'][reply]
            except KeyError: pass
    if reply: conn.send(xmpp.Message(msg.getFrom(), reply))

############################# bot logic stop #####################################

def StepOn(conn):
    try:
        conn.Process(1)
    except KeyboardInterrupt:
        return False
    return True

def GoOn(conn):
    while StepOn(conn):
        pass

def main():        
    if USERNAME == '' or PASSWORD == '' or SERVER == '':        
        print "Usage: bot.py username@server.net password"
        sys.exit(0)
        
    # jid = xmpp.JID(USERNAME)
    # user, server, password = jid.getNode(), jid.getDomain(), PASSWORD

    # conn = xmpp.Client(server)#, debug = [])
    conn = xmpp.Client(SERVER, debug = ['always'])
    # conres = conn.connect()
    conres = conn.connect(server=(SERVER, PORT))
    if not conres:
        print "Unable to connect to server %s!" % SERVER
        sys.exit(1)

    if conres not in ('tls', 'ssl'):
        print "Warning: unable to estabilish secure connection - both TLS and SSL failed!"
    else:
        print 'Using secure connection - %s' % conres
        
    # authres = conn.auth(user, password)
    authres = conn.auth(USERNAME, PASSWORD)    
    if not authres:
        print "Unable to authorize on %s - check login/password." % SERVER
        sys.exit(1)
        
    if authres != 'sasl':
        print "Warning: unable to perform SASL auth os %s. Old authentication method used!" % SERVER
        
    conn.RegisterHandler('message', message_callback)
    conn.sendInitPresence()
    print "Bot started."
    
    GoOn(conn)

if __name__ == '__main__':
    main()
