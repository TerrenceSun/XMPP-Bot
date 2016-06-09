#!/usr/bin/env python

from get_ip import get_ip
from init_env import WHITE_LIST_USERS

i18n = {
    'zh_CN': {},
    'en': {}
    }
i18n['en']['HELP'] = "This is example jabber bot.\nAvailable commands: %s"
i18n['en']["UNKNOWN COMMAND"] = 'Unknown command "%s". Try "help"'
i18n['en']["UNKNOWN USER"] = "I do not know you. Register first."
i18n['en']["COMMAND ERROR"] = 'Error durning processing input: "%s".'
i18n['en']['EMPTY'] = "%s"

commands = {}

def helpHandler(user, command, args, msg):
    lst = commands.keys()
    lst.sort()
    return "HELP", ',  '.join(lst)
commands['help'] = helpHandler

i18n['en']['HOOK1'] = 'Responce 1: %s'
def hook1Handler(user, command, args, msg):
    return "HOOK1", 'You requested: %s'%args
commands['hook1'] = hook1Handler

i18n['en']['HOOK2'] = 'Responce 2: %s'
def hook2Handler(user, command, args, msg):
    return "HOOK2", "hook2 called with %s"%(`(user, command, args, msg)`)
commands['hook2'] = hook2Handler

i18n['en']['HOOK3'] = 'Responce 3: static string'
def hook3Handler(user, command, args, msg):
    return "HOOK3"*int(args)
commands['hook3'] = hook3Handler

def get_ip_hook(user, command, args, msg):
    # print '>>> get_ip_hook'
    # print 'user:', user
    # print 'command:', command
    # print 'args:', args
    # print 'msg:', msg
    for i in WHITE_LIST_USERS:
        if str(user).find(i) != -1:
            return "IP of bot: %s" % (str(get_ip()).strip())
    return "COMMAND ERROR", 'User "%s" is not authortied to cmd "%s"' % (user, command)
        
commands['ip'] = get_ip_hook
