# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------#
#                            Import Librairies                                #
#-----------------------------------------------------------------------------#
import tool_kit as tk
#-----------------------------------------------------------------------------#
#                                get urls                                     #
#-----------------------------------------------------------------------------#

urla = ["http://www.bjorg.fr/recettes/crepes-avec-boissons-vegetales.html", 
        "http://www.bjorg.fr/recherche/recette-video.html", 
        "http://www.bjorg.fr/produits/gamme-galettes.html", 
        "http://www.bjorg.fr/produits/sirop-agave.html",
        "http://www.bjorg.fr/recherche/recettes-vegetariennes.html", 
        "http://www.bjorg.fr/recherche/recettes-sans-gluten.html",
        "http://www.bjorg.fr/recherche/recettes-minceur.html"]
urlb = ["http://www.bjorg.fr/recettes/tofu.html"]
urls = tk.dispatch(textfilename="dispatch.txt", listename=urla, ratio=100)  
url_file = open("url_file.txt", "w")      

for url in urls :
    print "url : ", url, "\n"
    pool =tk.curl(url)
    tk.oldnew_ipadress()
    url_list = []
    for c in pool :
        data = c.body.getvalue()
        soup = tk.BeautifulSoup(data)
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
    for i in url_list :
        url_file.write(i + "\n") 
url_file.close()
print "\n"
    
#-----------------------------------------------------------------------------#
#                                get url                                      #
#-----------------------------------------------------------------------------#
recipe = open("url_file.txt", "r").readlines()
print "len(recipe) : ", len(recipe)

#-----------------------------------------------------------------------------#
#                               get data                                      #
#-----------------------------------------------------------------------------#

urls = [i.replace('\n', '') for i in recipe]
urls = tk.dispatch(textfilename="dispatch_niv2.txt", listename=urls, ratio=1)
counta = 0
for url in urls :
    print "url : ", url
    counta += 1
    print counta, "/", len(urls)
    pool = tk.curl(url)
    tk.oldnew_ipadress()
    countb = 0
    for c in pool :
        data = c.body.getvalue()
        soup = tk.BeautifulSoup(data)
        s = soup.findAll('div', {'id' : 'recette'})
        #-------------------------------------------------------------------------#
        #                                 Title                                   #
        #-------------------------------------------------------------------------#
        title = s[0].findAll('h1')
        title = title[0].text
        #-------------------------------------------------------------------------#
        #                                 Nbr_person                              #
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
        avoid_list = ["<br />", ".", "- "]
        for i in ingredient :
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
                print a, ";",
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
