import json
import re
import requests
from bs4 import BeautifulSoup
import os.path


data = []

relatiuon_deductive = ['r_isa', 'r_holo']




def getWordId(mot):
    with open('idMot.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if mot == liste[1].replace("\"", ""):
                return liste[0]


def getRealationId(relation):
    with open('idRel.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if str(relation) == str(liste[1].replace("\"", "").replace("\n","")):
                return liste[0]


def getIdWord(id):
    with open('idMot.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if id == liste[0]:
                return liste[1].replace("\"", "")


def extraction_relation_html(word_id, relation_id, word, relation):
    html = requests.get(
        "http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=" + word + "&rel=" + relation)
    soup = BeautifulSoup(html.content, 'html.parser', from_encoding='iso-8859-1')
    texte_brut = soup.find_all('code')
    lignes_noeuds_et_relations = re.findall('[r];[0-9]*;.*', str(texte_brut))
    counter = 0
    for r in lignes_noeuds_et_relations:
        splitedRelation = r.split(";")
        counter += 1
        if splitedRelation[2] == str(word_id):
            data.append(
                {
                    "r": "sortante",
                    "rid": splitedRelation[1],
                    "node1": splitedRelation[2],
                    "node2": splitedRelation[3],
                    "type": splitedRelation[4],
                    "w": splitedRelation[5]
                }
            )
        elif splitedRelation[3] == str(word_id):
            data.append(
                {
                    "r": "entrante",
                    "rid": splitedRelation[1],
                    "node1": splitedRelation[2],
                    "node2": splitedRelation[3],
                    "type": splitedRelation[4],
                    "w": splitedRelation[5]
                }
            )

    with open('Cache/' + relation_id + '/' + word_id + '.json', 'a+') as output:
        json.dump(data, output)


def createCache(terme, relation):
    word_id = getWordId(terme)
    relation_id = getRealationId(relation)
    if os.path.isdir('Cache/' + relation_id + '/'):
        if os.path.isfile('Cache/' + relation_id + '/' + word_id + '.json'):
            return
        else:
            extraction_relation_html(word_id, relation_id, terme, relation)
    else:
        os.mkdir('Cache/' + relation_id + '/')
        extraction_relation_html(word_id, relation_id, terme, relation)





def detectInfernce(mot1, relation, mot2):
    createCache(mot1, relation)
    createCache(mot2, relation)
    transitive(mot1, relation, mot2)



def transitive(mot1, relation, mot2):
    idmot1 = getWordId(mot1)
    idmot2 = getWordId(mot2)
    idrelation = getRealationId(relation)
    with open('Cache/' + idrelation +'/'+idmot1+ '.json') as relationmot1, open('Cache/' +idrelation+'/'+ idmot2 + '.json') as relationmot2:
        data = json.load(relationmot1)
        data2 = json.load(relationmot2)
        for i in data:
            if i["r"] == "sortante":
                for j in data2:
                    if j["r"] == "entrante" and j["node1"] == i["node2"]:
                        print(getIdWord(j["node1"]))
                        print(j["node1"])


# extraction_relation("Tour Eiffel", "r_lieu")
# extraction_relation("France", "r_lieu")
detectInfernce("Tour Eiffel","r_lieu","France")


def deductive(mot1, relation, mot2):
    idmot1 = getWordId(mot1)
    idmot2 = getWordId(mot2)
    idrelation = getRealationId(relation)
    createCache(mot2, relation)
    for i in relatiuon_deductive:
        createCache(mot1,i)
        deductive_relation_id =getRealationId(i)
        with open('Cache/' + deductive_relation_id + '/' + idmot1 + '.json') as relationmot1, open('Cache/' + idrelation + '/' + idmot2 + '.json') as relationmot2:
            data = json.load(relationmot1)
            data2 = json.load(relationmot2)
            for j in data:
                pass




