#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
origin:
http://xmpppy.sourceforge.net/examples/bot.py
'''

from init_env import USERNAME, PASSWORD, SERVER, PORT
from init_env import HANDLER

import os
import pdb
import sys
import xmpp
import getopt
import logging

########################### user handlers start ##################################
imp_handler = __import__(HANDLER)
commands = imp_handler.commands
i18n = imp_handler.i18n
########################### user handlers stop ###################################

############################ bot logic start #####################################
pipe_name = "/tmp/xmpp-bot-fifo"
pipein = None

def disconnect_callback():
    logging.error("disconnected from server!")
    sys.exit(1)

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
def SrvCmdOn(conn, cmd_string):
    if cmd_string.find(' ')+1:
        command, args = cmd_string.split(' ',1)
    else:
        command, args = cmd_string, ''
    if (command == 'TO' and args != ''):
        user, msg = args.split(' ',1)
        conn.send(xmpp.Message(user, msg))

def StepOn(conn):
    global pipein
    try:
        conn.Process(1)
	cmdin = os.read(pipein, 512)
	SrvCmdOn(conn, cmdin.strip())
	if (cmdin == ''):
	    os.close(pipein)
	    pipein = os.open(pipe_name, os.O_RDONLY|os.O_NONBLOCK)
    except KeyboardInterrupt:
        return False
    except OSError as err:
	#print os.strerror(err.errno)
	return True
    return True

def GoOn(conn):
    i = 0;
    while StepOn(conn):
        i = i + 1
        if (i >= 10*60):
            conn.sendInitPresence()
            i = 0

def main():        
    log = "WARNING"
    try: opts, args = getopt.getopt(sys.argv[1:], "l:", ["log="])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)
    for o, a in opts:
        if o in ("-l", "--log"):
            log = a
        else: assert False, "unhanndled option"

    log_level = getattr(logging, log.upper(), None)
    if not isinstance(log_level, int):
        print "Invalid log level: %s" % log
        sys.exit(2)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=log_level)

    if USERNAME == '' or PASSWORD == '' or SERVER == '':        
        print "Please set USERNAME, PASSWORD and SERVER in init_env.py"
        sys.exit(1)
        
    # jid = xmpp.JID(USERNAME)
    # user, server, password = jid.getNode(), jid.getDomain(), PASSWORD

    # conn = xmpp.Client(server)#, debug = [])
    xmpp_debug = []
    if log_level == logging.DEBUG:
        xmpp_debug.append('always')
    conn = xmpp.Client(SERVER, debug = xmpp_debug)
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
    conn.RegisterDisconnectHandler(disconnect_callback)
    conn.sendInitPresence()
    print "Bot started."

    if not os.path.exists(pipe_name):
        print "make fifo:%s" % pipe_name
        os.mkfifo(pipe_name)
    global pipein
    pipein = os.open(pipe_name, os.O_RDONLY|os.O_NONBLOCK)

    GoOn(conn)

if __name__ == '__main__':
    main()
# vim: ts=4 expandtab sw=4 sts=4 :
