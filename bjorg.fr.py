# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------#
#                            Import Librairies                                #
#-----------------------------------------------------------------------------#

import tool_kit as tk

#-----------------------------------------------------------------------------#
#                           Recuperation des urls                             #
#-----------------------------------------------------------------------------#

urla = ["http://www.bjorg.fr/recettes/crepes-avec-boissons-vegetales.html", 
        "http://www.bjorg.fr/recherche/recette-video.html", 
        "http://www.bjorg.fr/produits/gamme-galettes.html", 
        "http://www.bjorg.fr/produits/sirop-agave.html",
        "http://www.bjorg.fr/recherche/recettes-vegetariennes.html", 
        "http://www.bjorg.fr/recherche/recettes-sans-gluten.html",
        "http://www.bjorg.fr/recherche/recettes-minceur.html"]
        
urlb = ["http://www.bjorg.fr/recettes/tofu.html"]

#on dispatch les url pour controler le flux de donnees envoyee au serveur
#et ne pas etre bannis.
urls = tk.dispatch(textfilename="dispatch.txt", listename=urla, ratio=100)  

#on ecrit la liste dans un fichier pour avoir 
#un backup en cas de plantage du telechergement ou blocage 
#par le site (etre bannis).

url_file = open("url_file.txt", "w")      

for url in urls :
    
    print "url : ", url, "\n"
    
    #on passe les urls dans curl pour les recuperer.
    pool =tk.curl(url)
    
    #on change a chaque fois d 'adresse ip pour ne pas etre bannis.
    tk.oldnew_ipadress()
    
    #la liste ou l on va stocker les urls.
    url_list = []
    
    for c in pool :
        
        data = c.body.getvalue()
        soup = tk.BeautifulSoup(data)
    #    print soup
        s = soup.findAll('h2')
        
        for i in s :
            a = i.findAll('a')
            if a == [] :
                pass
            else :
                a = a[0].get('href')
                a = a.split("?")[0]
                a = "http://www.bjorg.fr/" + a
                url_list.append(a)
                
                print a
        print '\n'
         
    #on ecrit dans le fichier ".txt" les urls.
    for i in url_list :
        url_file.write(i + "\n") 

#on ferme le fichier en ecriture. 
url_file.close()
print "\n"
    
#-----------------------------------------------------------------------------#
#                         Recuperation url                                    #
#-----------------------------------------------------------------------------#

#on re ouvre le fichier en lecture.
recipe = open("url_file.txt", "r").readlines()
print "len(recipe) : ", len(recipe)

#-----------------------------------------------------------------------------#
#                          Recuperation des donnees                           #
#-----------------------------------------------------------------------------#

urls = [i.replace('\n', '') for i in recipe]

urls = tk.dispatch(textfilename="dispatch_niv2.txt", listename=urls, ratio=1)

counta = 0
for url in urls :
    
    print "url : ", url
    
    counta += 1

    print counta, "/", len(urls)
    
    pool = tk.curl(url)
    
    #on change d adresse ip apres chaue download de donnees. 
    tk.oldnew_ipadress()
    
    countb = 0
    
    for c in pool :
        data = c.body.getvalue()
        soup = tk.BeautifulSoup(data)
        s = soup.findAll('div', {'id' : 'recette'})
    
        #-------------------------------------------------------------------------#
        #                                 Titre                                   #
        #-------------------------------------------------------------------------#
        
        title = s[0].findAll('h1')
        title = title[0].text
    
        #-------------------------------------------------------------------------#
        #                                 Nbr_peron                               #
        #-------------------------------------------------------------------------#
         
        person = s[0].findAll('div', {'class' : 'infos'})
        person = person[0].findAll('span', {'class' : 'yield'})
        person = person[0].text
        person = person.replace(' personne', '')
        person = person.replace('s', '')
    
        #-------------------------------------------------------------------------#
        #                                 Temps_prepa                             #
        #-------------------------------------------------------------------------#
    
        prep_time = s[0].findAll('span', {'class' : 'prepTime'})
        prep_time = prep_time[0].text
    
        print "title : ", title
        print "person : ", person
        print "prep_time : ", prep_time, "minutes"
        
        #-------------------------------------------------------------------------#
        #                                 Ingredients                             #
        #-------------------------------------------------------------------------#
        
        print "ingredients : ", 
        ingredient = s[0].findAll('div', {'class' : 'ingredient'})
        ingredient = ingredient[0].findAll('div')
        ingredient = ingredient[0].findAll('li')
    #    ingredient = ingredient[0]
        
        #liste des items a filtrer dans la loop
        #suivante.
        avoid_list = ["<br />", ".", "- "]
        
        for i in ingredient :
            #on evite <br/> en passant par 
            # la chaine de caractere de "i".
            if str(i) in avoid_list :
                pass
            else :
                a = str(i).replace('&bull; ', '')
                a = a.replace('&nbsp;', '')
                a = a.replace("&agrave;", "a")
                a = a.replace('&eacute;', 'e')               
                a = a.replace(' de', '')
                a = a.replace(" d'", "")
                a = a.replace(".", "")
                a = a.replace("- ", "")
                a = a.replace("&laquo;", "")
                a = a.replace("&raquo;", "")
                a = a.replace('&ucirc;', 'u')
                a = a.replace("&acirc;", "a")
                a = a.replace("<li>", "").replace("</li>", "")
                a = a.split("<a")[0]
    #            a = a.replace("</a", "") 
                print a, ";",
                 
        #-------------------------------------------------------------------------#
        #                                 Preparation                             #
        #-------------------------------------------------------------------------#
        
        print "preparation : "
        prepa = s[0].findAll('div', {'class' : 'preparation instructions'})
        prepa = prepa[0].findAll('p')
        for i in prepa :
            a = i.text
            a = a.replace('&agrave;', 'a')
            a = a.replace('&eacute;', 'e')
            a = a.replace('&acirc;', 'a')
            a = a.replace('&ecirc;', 'e')
            a = a.replace('&deg', ' degres celcius')
            a = a.replace('&nbsp;', '')
            a = a.replace('!nbsp;', '')
            a = a.replace('&iuml;', 'i')
            a = a.replace(" rsquo;", "'")
            print a
        
        print "\n"
