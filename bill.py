#!/usr/bin/env python
# vim: set fileencoding=utf-8

from get_ip import get_ip
from init_env import WHITE_LIST_USERS,BILL_PASSWORD
from datetime import datetime
import MySQLdb
import re
import logging

logger = logging.getLogger('bill')

commands = {}

i18n = {
    'zh_CN': {},
    'en': {}
    }

i18n['en']['HELP'] = "This is example jabber bot.\nAvailable commands: %s"
i18n['en']["UNKNOWN COMMAND"] = 'Unknown command "%s". Try "help"'
i18n['en']["UNKNOWN USER"] = "I do not know you. Register first."
i18n['en']["COMMAND ERROR"] = 'Error durning processing input: "%s".'
i18n['en']["SYNTAX ERROR"] = 'Usage:%s'
i18n['en']['EMPTY'] = "%s"


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

def bill_view(user, command, args, msg):
    return bill(user.getNode()+'@'+user.getDomain(), 'view', args.split(' '));
commands['billview'] = bill_view

def bill_add(user, command, args, msg):
    return bill(user.getNode()+'@'+user.getDomain(), 'add', args.split(' '));
commands['bill'] = bill_add

def bill_agent(sql,show_idx=[]):
    res = "";
    logger.debug(sql)
    db = MySQLdb.connect(host="localhost",
                         user="bill",
                         passwd=BILL_PASSWORD,
                         db="bill",
                         charset="utf8",
                         use_unicode=True)
    cur = db.cursor(MySQLdb.cursors.DictCursor)
    try:
        cur.execute(sql)
        db.commit()
        if sql.upper().find('SELECT') != -1:
            results = cur.fetchall()
            res = u"\n"
            for row in results:
                for col in show_idx:
                    try: res += u" " + unicode(row[col])
                    except: logger.WARNING("AGENT: cannot unicode %s for %s " % (str(type(row[col])), col))
                res += u"\n"
    except Exception as e:
        logger.error("AGENT:%s" %(str(e)))
        res = "DB execution error"
    db.close()
    return res

def bill(user, command, args):
    if (command == 'view'):
        if (len(args) != 1): return "SYNTAX ERROR", "billview reason"
        return bill_agent("SELECT * FROM billitem WHERE user='%s' AND reason='%s' ORDER BY date DESC LIMIT 8" % (user, args[0]), ["date", "source", "value", "data"])
    elif (command == 'add'):
        source = u'现金'
        data = ''
        date = datetime.now().strftime("%Y-%m-%d")

        # [date], reason, [source], value, [data]
        if (len(args) < 2): return "SYNTAX ERROR", "bill [date] reason [source] value [data]"
        elif (len(args) == 2):
            reason, value = args
        else:
            i = 0
            if re.match(r"\d{4}-\d{2}-\d{2}", args[i]):
                date, reason = args[i:i+2]
                i = i + 2
            else:
                reason = args[i]
                i = i + 1
            if re.match(r"^\d*.?\d*$", args[i]):
                value = args[i]
                i = i + 1
            else:
                source, value = args[i:i+2]
                i = i + 2

            if (len(args) > i):
                data = args[i]

            if not re.match(r"^\d*.?\d*$", value):
                return "COMMAND ERROR", "%s is not a number" % (value)
            
        return bill_agent("INSERT into `billitem` (data,date,reason,source,user,value) VALUES ('%s','%s','%s','%s','%s',%s)" % (data, date, reason, source, user, value));
