#!/usr/bin/python
import sys
import os


filelist = ["libarm71.so", "libarm50.so", "50", "71", "70"]
lib50 = ["libarm50.so", "50/libvplayer.so", "50/libffmpeg.so"]
lib71 = ["libarm71.so", "71/libvplayer.so", "71/libffmpeg.so"]
libfiles = [ "50/libvplayer.so", "50/libffmpeg.so", "71/libvplayer.so", "71/libffmpeg.so"]
[INIT, CHECK, UPDATE, EXTRACT]=[0, 1, 2, 3]

[ITEMS, KEY, SIZE, SYMBOL]=['items', 'key', 'size', 'symbol']
[FAIL, SUCCESS]=[0,1]
PARSE_INFO = 'parse.info'

g_info = {}

def help(ret):
    print '''should follow the command format:
    command --check/update/extract path
        check: check with default comparing file
        update: create one default comparing file
        extract: extract file and create libarm71.so, libarm50.so
        path: directory contains libarm.so
    '''
    exit(ret)

def checkParameters():
    if len(sys.argv) < 3:
        help(-1)


def rmfiles(path):
    pass

def checkMainFile(path):
    if not (os.path.isfile(path)):
        help(-1)

def myremove(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        l = os.listdir(path)
        for f in l:
            myremove(path + "/" + f)
        os.rmdir(path)

def removeold(path):
    for p in filelist:
        f = path + "/" + p
        #print f
        myremove(f)

def extractFile(path, file):
    if not file:
        help(-1)
    dir = os.getcwd()
    os.chdir(path)
    cmd = "7zr x " + os.path.basename(file)
    print(cmd)
    try:
        if os.system(cmd) != 0:
            print("error in extractFile")
            exit(-1)
    finally:
        os.chdir(dir)

def createNewLib(path, liblist):
    curdir = os.getcwd()
    try:
        os.chdir(path)
        libname = liblist[0]
        params = liblist[1:]
        cmd = "7zr a " + libname + " " + " ".join(params)
        print(cmd)
        os.system(cmd)
    finally:
        os.chdir(curdir)


def checkAndCreateStructure(mainpath, mainfile):
    removeold(mainpath)
    extractFile(mainpath, mainfile)
    createNewLib(mainpath, lib50)
    createNewLib(mainpath, lib71)


def getSize(file):
    return os.path.getsize(file)

def getSymbol(file):
    cmd = 'readelf -s ' + file + '|awk \'{print $8}\''
    f = os.popen(cmd)
    s = " ".join(f.readlines())
    s = s.replace("\n", "")
    return s

def checkHandle(params):
    if KEY not in params:
        print("internal error checking, should specify key" + params)
        return False
    key = params[KEY]

    global g_info
    item = []
    for i in g_info[ITEMS]:
        k = i[KEY]
        if k == key:
            item = i
            break
    if not item:
        print("can't find item " + key)
        return False
    
    for i in params:
        if i == KEY:
            continue
        if params[i] != item[i]:
            if i == SIZE:
                s = key + ":\n\torigin " + " size = " + str(item[i])
                s += "\n\tcurrent " + " size = " + str(params[i])
                print(s)
            else:
                s = " ".join([key, i, "---fail"])
                print s
                return False
        else:
            s = " ".join([key, i, "---ok"])
            print s
    return True


def updateHandle(params):
    if KEY not in params:
        print("internal error update, should specify key" + params)
        return False
    key = params[KEY]

    global g_info
    item = []
    for i in g_info[ITEMS]:
        k = i[KEY]
        if k == key:
            item = i
            break
    if not item:
        g_info[ITEMS].append(params)
    else:
        for i in params:
            if i == KEY:
                continue
            item[i] = params[i]

    return True

def parseFile(filename, callback):
    '''
    callback to handle, FAIL, SUCCESS
    '''
    size = getSize(filename)
    if callback:
        callback({KEY:filename, SIZE:size})

    symbol = getSymbol(filename)
    if callback:
        callback({KEY:filename, SYMBOL:symbol})

def checking(mainpath):
    print("checking")
    def initInfo():
        global g_info
        g_info = {}
        f = open(PARSE_INFO, 'r')
        s = "".join(f.readlines())
        g_info = eval(s)
        #print g_info
    initInfo()
    dowork(checkHandle)

def update(mainpath):
    print("update")
    def initInfo():
        global g_info
        g_info = {}
        g_info['items'] = []
    def saveInfo():
        f = open(PARSE_INFO, 'wa+')
        f.truncate(0)
        f.write(str(g_info))

    initInfo()
    dowork(updateHandle)
    saveInfo()

def dowork(handler):
    curdir = os.getcwd()
    try:
        os.chdir(mainpath)
        for i in libfiles:
            parseFile(i, handler)
    finally:
        os.chdir(curdir)

if __name__ == '__main__':
    checkParameters()
    mode = INIT
    if sys.argv[1] == '--check':
        mode = CHECK
    elif sys.argv[1] == '--update':
        mode = UPDATE
    elif sys.argv[1] == '--extract':
        mode = EXTRACT

    mainpath = sys.argv[2]
    mainfile = mainpath + "/libarm.so"
    checkMainFile(mainfile)
    if mode == CHECK:
        checking(mainpath)
    elif mode == UPDATE:
        update(mainpath)
    elif mode == INIT:
        help(-1)
    elif mode == EXTRACT:
        checkAndCreateStructure(mainpath, mainfile)


