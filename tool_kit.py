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

#cette fonction permet de verifier que les dossier dont on a besoin dans le 
#cadre du programme pour y ecrire des fichiers existent bien. Si ils n'existent 
#pas on le creer.

def create_path() :
    
    print "Verifying internal paths", "\n"
    
    #on met dans une lsite l ensemble des dossiers a verifier.
    
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

#il s agit du fichier permettant de transformer un paquet d url en plusieurs lot
#en fonction d un ratio, puis il est ainsi exploiter par un autre fichier pour
#eviter les goulots d etranglements en cas de traitement global de tout les
#fichier downloader par "CurlMulti".

#-----------------------------------------------------------------------------#

def dispatch(textfilename, listename, ratio=1) :

    print "#-----------------------------------------------------------------#"
    print "dispatch des liens en sous listes"
    compteur0 = 0

    #on ouvre le fichier texte "textfilename" pour y ecrire les urls.

    fichier = open(textfilename, "w")
    list_init =[]
    nbr_lot = int(float(len(listename)) / float(ratio))

    #on determine le nbre de lot dans la liste par une variable.

    if nbr_lot < float(len(listename)) / float(ratio) :
        nbr_total_lot = nbr_lot + 1
    else :
        nbr_total_lot = nbr_lot

    #on alimente une liste par des sous lots de liste de valeur ratio en nombre
    #d items.

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

                #list0 est la liste qui contient les elements i qui vient ce
                #dernier de sp4.lsit_init qui est la liste des urls a traiter.
                #list_init est la liste qui va contenir toutes les listes "list0".
                #dans la boucle précédente on enlève chaque element i qui
                #appartient deja a la liste "list_init" puis on relance le processus
                #jusqu'a la fin de la boucle.

        list_init.append(list0)

        #on charge list0 dans list_init a la fin de cette boucle.
        #on met une liste dans une autre liste.

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

#il s agit de la fonction "CurlMulti" qui recupere les objets de "url".
# "url" est une liste d'urls. si 1 url mettre dans une liste url = ["monurl"] a
#definir avant d'appliquer la fonction.
#ici on fait passer le telechargement des items par Curl via Tor afin que l'adresse
#ip utiliser ne soit pas spammer, par contre cela entraine un ralentissement reseau.

#-----------------------------------------------------------------------------#

def curl(url, tor="no") :
    
#    print "Curl is waiting for data ... ", "\n"

    #phase initialisation des curl multi.

    m = pycurl.CurlMulti()
    m.handles = []
    
    for i in url :

        #on enleve au fur et a mesure les elements de la liste quand il arrive
        #puis sont utilisés.on travail sous pycurl maintenant pour debuter
        #la recolte de l'url et son stockage.
        #creation de l'objet Curl

        c = pycurl.Curl()

        #creation de l'objet qui stockera la page web avec StringIO

        c.body = StringIO()
        c.http_code = -1
        m.handles.append(c)

        #mise en place des option curl
        #on indique l'url a Curl

        c.setopt(pycurl.URL, str(i))
        c.setopt(pycurl.WRITEFUNCTION, c.body.write)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.NOSIGNAL, 1)
        c.setopt(pycurl.USERAGENT, 'Mozilla/5.0 (X11; Linux x86_64) Ubuntu/12.04 Chromium/14.0.835.202')
        c.setopt(pycurl.HTTPHEADER, ['User-agent: %s' % 'Mozilla/5.0 (X11; Linux x86_64) Ubuntu/12.04 Chromium/14.0.835.202 Data Mining and Research'])

        #---------------------------------------------------------------------#
        #                    PROTECTION AVEC TOR ET DNS :                     #
        #---------------------------------------------------------------------#
        
        if tor == "no" :
            pass
        elif tor == "yes" :
            #attention le port ci dessous est le numero 9150 et pas 9151
            
            c.setopt(pycurl.PROXY, '127.0.0.1')
            c.setopt(pycurl.PROXYPORT, 9050)
            c.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5)
        else :
            print "You must set a value to tor option 
            break
            

        #---------------------------------------------------------------------#
        #                    Reprise de la suite ...                          #
        #---------------------------------------------------------------------#
        
        c.setopt(pycurl.REFERER, 'http://www.google.co.uk/') #http://www.google.co.in/
        m.add_handle(c)
    num_handles = len(m.handles)
    
    #mise en activité

    while 1 :
        ret, num_handles = m.perform()
        if ret != pycurl.E_CALL_MULTI_PERFORM :
            break

    #prendre les données.

    while num_handles :
        m.select(1.0)
        while 1 :
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM :
                break
            
#    print "Ok, Curl gets data"

    #fermer les handles.

    for c in m.handles :
        c.close()
    m.close()
    return m.handles

#-----------------------------------------------------------------------------#
#              Recuperation des donnees qui contient l ip adress              #
#-----------------------------------------------------------------------------#

def read_ipadress(path_log="loginit/") :
    
    #cette url permet d'acceder à l'ensemble de la page de départ du site
    #sur laquelle se trouve la majorité des liens qui pourront nous interesser
    #par la suite.

    #cette url permet d'acceder à l'ensemble de la page de départ du site
    #sur laquelle se trouve la majorité des liens qui pourront nous interesser
    #par la suite.

    ip_url = ["http://www.my-ip-address.net", "http://www.mon-ip.com",
              "http://www.adresseip.com", "http://my-ip.heroku.com",
              "http://www.whatsmyip.net", "http://www.geobytes.com/phpdemo.php",
              "http://checkip.dyndns.com", "http://www.myglobalip.com"]
              
    #autres sites a integrer voir fichier "tor_auto_renew_ipadress.py"

    # http://www.myglobalip.com/
    # http://www.whereisip.net/
    # http://www.howtofindmyipaddress.com/
    # http://www.hostip.info/
    # http://www.ipchicken.com/
    # http://myip.dk/
    # http://www.showmyipaddress.com/
    # http://www.tracemyip.org/ 
    # http://www.myipnumber.com/
    # http://en.dnstools.ch/show-my-ip.html
    # http://ifconfig.me/
    # https://www.astrill.com/what-is-my-ip-address.php
    # http://www.cmyip.com/
    # http://ip-detect.net/
    # http://www.dslreports.com/whois
    # http://www.whatismybrowser.com/what-is-my-ip-address
    # http://www.showmemyip.com/
    # http://aboutmyip.com/AboutMyXApp/AboutMyIP.jsp
    # http://www.findmyip.org/
    # https://www.whatsmydns.net/whats-my-ip-address.html

    #on utilise random afin de choisir au hasard un elements parmis la liste 
    #d url de "ip_url". On le met entre crochet car ensuite "curl" lit une url
    #ou serie d urls entre crochet (une liste)
    
    url = random.choice(ip_url)
    
    if url == "http://www.my-ip-address.net" :
        
        print "url : ", url,
        
        pool = curl([url])

        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
    
            s1 = soup1.findAll('h2')[0].text
            s1 = s1.replace("IP Address :", "")
            s1 = s1.replace("Your IP Address is", "")
            
    elif url == "http://www.mon-ip.com" :
        
        print "url : ", url,
            
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
    
            s1 = soup1.findAll('span', {'class' : 'clip'})[0].text        
            
    elif url == "http://www.adresseip.com" :
        
        print "url : ", url,
        
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
    
            s1 = soup1.findAll('h2', {'class' : 'title'})[0].text
            s1 = s1.replace("Votre Adresse IP est :", "")
           
    elif url == "http://www.whatsmyip.net" :
        
        print "url : ", url,     
        
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)

            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
    
            s1 = soup1.findAll('h1', {'class' : 'ip'})[0]
            s1 = s1.findAll('input')[0]['value']
            
    elif url == "http://my-ip.heroku.com" :
        
        print "url : ", url,
            
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
    
            #on obtient le texte directement depuis la page qui est sans 
            #structure.
    
            s1 = soup1.text        

    elif url == "http://www.geobytes.com/phpdemo.php" :
        
        print "url : ", url,
            
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
            
            #on obtient le texte directement depuis la page qui est sans 
            #structure.
    
            s1 = soup1.findAll('b')[0].text      

    elif url == "http://checkip.dyndns.com" :
        
        print "url : ", url,
            
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
            
            #on obtient le texte directement depuis la page qui est sans 
            #structure.
    
            s1 = soup1.text
            s1 = s1.replace("Current IP CheckCurrent IP Address: ", "")
            
    elif url == "http://www.myglobalip.com" :
        
        print "url : ", url,
            
        pool = curl([url])
        
        for c in pool :
            
            #on recupere les url qui n ont pas fonctionner lors du proccessus :
            
            data = c.body.getvalue()
            
            #utilisation de BeautifulSoup
            #on met dans BeautifulSoup le contenu de la page web
    
            soup1 = BeautifulSoup(data)
            
            #on recherche tous les liens du contenu dans le conteneur "li" 
            #dont la class = switch_style du css il y a d'autres liens dans 
            #les autres conteneur. on se place dans le css numero 1 "li" 
            #dont la class = "switch_style".
            
            #on obtient le texte directement depuis la page qui est sans 
            #structure.
    
            s1 = soup1.findAll('h3')
            s1 = s1[0].findAll('span', {'class' :'ip'})
            s1 = s1[0].text
                      
    else :
        print "Problem"
    
    #on retounrne la valeur de s1 qui contient le texte concernant l adresse ip
    #on pourra ainsi imprimer la valeur rendu par la fonction ailleurs dans le 
    #programme.
    
    ip_adress = s1
    
    return ip_adress

#-----------------------------------------------------------------------------#
#                             New IP Adress                                   #
#-----------------------------------------------------------------------------#

#permet grace au module stem "Signal" de changer en tor l'adresse ip 
#des que la fonction est appelee. 
    
def change_ipadress(passphrase="Femmes125", sleep=5) :

    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(passphrase)
        controller.signal(Signal.NEWNYM)  
    
    #on fait patienter une seconde
    
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

#on creer une fonction unique qui ira chercher quelle est l adresse ip actuelle
#puis qui change l etat de tor pour renouveller l ip et enfin, va lire a nouveau
#l adress ip sur le meme site. 

def oldnew_ipadress(ip_adress=read_ipadress()) :
    
#    print "Changing ip address ... ",
        
    #nous renouvellons l adresse ip et on relance la fonction jusqu a deux fois 
    #en cas de necessite :
        
    #-------------------------------------------------------------------------#
    #                           partie 1 de oldnew_ipadress                   #
    #-------------------------------------------------------------------------# 
    
    #affichage de l adresse ip actuelle

    print "Old : ",
    
    #on lance la fonction "try_read_ipadress()" qui tente par trois fois de
    #de lancer le programme si le lancement fait defaut.
    
    try_read_ipadress()

    #-------------------------------------------------------------------------#
    #                           partie 2 de oldnew_ipadress                   #
    #-------------------------------------------------------------------------# 
    
    #changement de l adress ip via thor. Il est a noter que l on pourrait se 
    #debarraser de la 1ere fois du redemarage de "read_ip()". Il a ete utiliser
    #au debut pour verifier le bon changement d adresse entre les deux etats de 
    #tor avant le lancement du signal et apres la nouvelle ip prise.
                
    change_ipadress()    
        
    #-------------------------------------------------------------------------#
    #                           partie 3 de oldnew_ipadress                   #
    #-------------------------------------------------------------------------#  
    
    #affichage de l adresse ip nouvelle.

    print "New : ",
    
    try_read_ipadress()
            
    print "\n"
               
#dev : securite aller chercher l adresse ip de retour sur un autre site
                                
#-----------------------------------------------------------------------------#
#                          MongoDB connection                                 #
#-----------------------------------------------------------------------------#
 
def mongo(db_name,collection_name,doc) :
        
    #connection to mongodb 
    try :
        cn = pymongo.MongoClient()
    except pymongo.errors.ConnectionFailure, e :
        print "Could not connect to MongoDB %s" % (e)
        
    #built of db where we want to store our stuff
    db = cn[db_name]
    
    #creation d une collection ou stocker nos donnees.
    collection = db[collection_name]
    
    #insert your document into the collection
    collection.insert(doc)
