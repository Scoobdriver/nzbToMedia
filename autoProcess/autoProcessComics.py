import sys
import urllib
import os.path
import time
import ConfigParser
import logging
import socket

from nzbToMediaEnv import *
from nzbToMediaUtil import *
from nzbToMediaSceneExceptions import process_all_exceptions

Logger = logging.getLogger()
socket.setdefaulttimeout(int(TimeOut)) #initialize socket timeout.

class AuthURLOpener(urllib.FancyURLopener):
    def __init__(self, user, pw):
        self.username = user
        self.password = pw
        self.numTries = 0
        urllib.FancyURLopener.__init__(self)
    
    def prompt_user_passwd(self, host, realm):
        if self.numTries == 0:
            self.numTries = 1
            return (self.username, self.password)
        else:
            return ('', '')

    def openit(self, url):
        self.numTries = 0
        return urllib.FancyURLopener.open(self, url)


def processEpisode(dirName, nzbName=None, status=0, inputCategory=None):

    config = ConfigParser.ConfigParser()
    configFilename = os.path.join(os.path.dirname(sys.argv[0]), "autoProcessMedia.cfg")
    Logger.info("Loading config from %s", configFilename)
    
    if not os.path.isfile(configFilename):
        Logger.error("You need an autoProcessMedia.cfg file - did you rename and edit the .sample?")
        return 1 # failure
    
    config.read(configFilename)

    section = "Mylar"
    if inputCategory != None and config.has_section(inputCategory):
        section = inputCategory
    host = config.get(section, "host")
    port = config.get(section, "port")
    username = config.get(section, "username")
    password = config.get(section, "password")
    try:
        ssl = int(config.get(section, "ssl"))
    except (ConfigParser.NoOptionError, ValueError):
        ssl = 0
    
    try:
        web_root = config.get(section, "web_root")
    except ConfigParser.NoOptionError:
        web_root = ""

    try:
        watch_dir = config.get(section, "watch_dir")
    except ConfigParser.NoOptionError:
        watch_dir = ""
    params = {}

    nzbName, dirName = converto_to_ascii(nzbName, dirName)

    if dirName == "Manual Run" and watch_dir != "":
        dirName = watch_dir
    
    params['nzb_folder'] = dirName
    if nzbName != None:
        params['nzb_name'] = nzbName
        
    myOpener = AuthURLOpener(username, password)
    
    if ssl:
        protocol = "https://"
    else:
        protocol = "http://"

    url = protocol + host + ":" + port + web_root + "/post_process?" + urllib.urlencode(params)
    
    Logger.debug("Opening URL: %s", url)
    
    try:
        urlObj = myOpener.openit(url)
    except:
        Logger.exception("Unable to open URL")
        return 1 # failure
    
    result = urlObj.readlines()
    for line in result:
         Logger.info("%s", line)
    
    time.sleep(60) #wait 1 minute for now... need to see just what gets logged and how long it takes to process
    return 0 # Success        
