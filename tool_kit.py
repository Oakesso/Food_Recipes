# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 16:36:42 2014

@author: Ninja
"""

#-----------------------------------------------------------------------------#
#                            Import Librairies                                #
#-----------------------------------------------------------------------------#

from BeautifulSoup import BeautifulSoup
import pycurl
from StringIO import StringIO
import time
from stem import Signal
from stem.control import Controller
import os
import random
import pymongo

#-----------------------------------------------------------------------------#
#                          creation des dosssiers                             #
#-----------------------------------------------------------------------------#

def create_path() :
    print "Verifying internal paths", "\n"
    path_list = ["log/", "loginit/"]    
    for i in path_list :        
        if os.path.exists(i) :
            pass
        else :
            print i, "... now Created"
            os.mkdir(i)
    print "\n"

#-----------------------------------------------------------------------------#
#                               dispatch                                      #
#-----------------------------------------------------------------------------#

def dispatch(textfilename, listename, ratio=1) :
    print "#-----------------------------------------------------------------#"
    print "dispatch des liens en sous listes"
    compteur0 = 0
    fichier = open(textfilename, "w")
    list_init =[]
    nbr_lot = int(float(len(listename)) / float(ratio))
    if nbr_lot < float(len(listename)) / float(ratio) :
        nbr_total_lot = nbr_lot + 1
    else :
        nbr_total_lot = nbr_lot
    for x in range(len(listename)) :
        list0 = []
        for i in listename :
            compteur0 += 1
            if compteur0 > ratio :
                compteur0 = 0
                break
            else :
                list0.append(i)
                fichier.write(i + "\n")
                listename.remove(i)
        list_init.append(list0)
    compteur1 = 0
    list_list = []
    for z in list_init :
        compteur1 += 1
        if len(z) != 0 :
            list_list.append(z)
        else :
            pass
    print len(list_list), "ensembles(s) de listes traitees pour" , len(list_init), "liens "
    print "#-----------------------------------------------------------------#"
    print "\n"
    return list_list

#-----------------------------------------------------------------------------#
#                                 Curl                                        #
#-----------------------------------------------------------------------------#

def curl(url, tor="no") :
    m = pycurl.CurlMulti()
    m.handles = []
    for i in url :
        c = pycurl.Curl()
        c.body = StringIO()
        c.http_code = -1
        m.handles.append(c)
        c.setopt(pycurl.URL, str(i))
        c.setopt(pycurl.WRITEFUNCTION, c.body.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.NOSIGNAL, 1)
        c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64) Ubuntu/12.04 Chromium/14.0.835.202')
        c.setopt(pycurl.HTTPHEADER, ['User-agent: %s' % 'Mozilla/5.0 (X11; Linux x86_64) Ubuntu/12.04 Chromium/14.0.835.202 Data Mining and Research'])

        #---------------------------------------------------------------------#
        #                      GET DATA WITH TOR ET DNS :                     #
        #---------------------------------------------------------------------#
        
        if tor == "no" :
            pass
        elif tor == "yes" :
            c.setopt(pycurl.PROXY, '127.0.0.1')
            c.setopt(pycurl.PROXYPORT, 9050)
            c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        else :
            print "You must set a value to tor option 
            break
            

        #---------------------------------------------------------------------#
        #                    Next  ...                                        #
        #---------------------------------------------------------------------#
        
        c.setopt(pycurl.REFERER, 'http://www.google.co.uk/') #http://www.google.co.in/
        m.add_handle(c)
    num_handles = len(m.handles)
    while 1 :
        ret, num_handles = m.perform()
        if ret != pycurl.E_CALL_MULTI_PERFORM :
            break
    while num_handles :
        m.select(1.0)
        while 1 :
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM :
                break
    for c in m.handles :
        c.close()
    m.close()
    return m.handles

#-----------------------------------------------------------------------------#
#              Recuperation des donnees qui contient l ip adress              #
#-----------------------------------------------------------------------------#

def read_ipadress(path_log="loginit/") :
    ip_url = ["http://www.my-ip-address.net", "http://www.mon-ip.com",
              "http://www.adresseip.com", "http://my-ip.heroku.com",
              "http://www.whatsmyip.net", "http://www.geobytes.com/phpdemo.php",
              "http://checkip.dyndns.com", "http://www.myglobalip.com"]
    url = random.choice(ip_url)
    if url == "http://www.my-ip-address.net" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.findAll('h2')[0].text
            s1 = s1.replace("IP Address :", "")
            s1 = s1.replace("Your IP Address is", "")
    elif url == "http://www.mon-ip.com" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.findAll('span', {'class' : 'clip'})[0].text        
    elif url == "http://www.adresseip.com" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.findAll('h2', {'class' : 'title'})[0].text
            s1 = s1.replace("Votre Adresse IP est :", "")
    elif url == "http://www.whatsmyip.net" :
        print "url : ", url,     
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.findAll('h1', {'class' : 'ip'})[0]
            s1 = s1.findAll('input')[0]['value']
    elif url == "http://my-ip.heroku.com" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.text        
    elif url == "http://www.geobytes.com/phpdemo.php" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.findAll('b')[0].text      
    elif url == "http://checkip.dyndns.com" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.text
            s1 = s1.replace("Current IP CheckCurrent IP Address: ", "")
    elif url == "http://www.myglobalip.com" :
        print "url : ", url,
        pool = curl([url])
        for c in pool :
            data = c.body.getvalue()
            soup1 = BeautifulSoup(data)
            s1 = soup1.findAll('h3')
            s1 = s1[0].findAll('span', {'class' :'ip'})
            s1 = s1[0].text
    else :
        print "Problem"
    ip_adress = s1
    return ip_adress

#-----------------------------------------------------------------------------#
#                             New IP Adress                                   #
#-----------------------------------------------------------------------------#

def change_ipadress(passphrase="Femmes125", sleep=5) :
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(passphrase)
        controller.signal(Signal.NEWNYM)  
    time.sleep(sleep)
                
#-----------------------------------------------------------------------------#
#                          Try to read the ip adress                          #
#-----------------------------------------------------------------------------#

def try_read_ipadress() :
    try :
        print read_ipadress()
    except :
        #---------------------------------------------------------------------#
        #                    1er re lancement de read_ipadress                #
        #---------------------------------------------------------------------#
        print "1st time read_ipadress failed to launch"
        print "re start 1 read_ipadress"
        print "\n"
        try :
            print read_ipadress()
        except :
            #-----------------------------------------------------------------#
            #                   2eme re lancement de read_ipadress            #
            #-----------------------------------------------------------------#
            print "2nd time read_ipadress failed to launch"
            print "re start 2 read_ipadress"
            print "\n"   
            try :
                print read_ipadress()
            except :
                #-------------------------------------------------------------#
                #                   3eme re lancement de read_ipadress        #
                #-------------------------------------------------------------#
                print "3rd time read_ipadress failed to launch"
                print "re start 3 read_ipadress"
                print "\n"
                print read_ipadress()    
                                
#-----------------------------------------------------------------------------#
#                          Re-new the ip adress                               #
#-----------------------------------------------------------------------------#

def oldnew_ipadress(ip_adress=read_ipadress()) :
    print "Old : ",
    try_read_ipadress()
    change_ipadress()    
    print "New : ",
    try_read_ipadress()
    print "\n"

#-----------------------------------------------------------------------------#
#                          MongoDB connection                                 #
#-----------------------------------------------------------------------------#
 
def mongo(db_name,collection_name,doc) :
    try :
        cn = pymongo.MongoClient()
    except pymongo.errors.ConnectionFailure, e :
        print "Could not connect to MongoDB %s" % (e)
    db = cn[db_name]
    collection = db[collection_name]
    collection.insert(doc)
