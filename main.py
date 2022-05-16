import json
import re
import requests
from bs4 import BeautifulSoup

dictionary = {
    "name": "sathiyajith",
    "rollno": 56,
    "cgpa": 8.6,
    "phonenumber": "9976770500"
}

data = []


def create_json_file(relation):
    pass


# create_json_file(relationentrante, relationsortante)

"Tour Eiffel r_lieu France"


def test(mot1, relation, mot2):
    pass


def getWordId(mot):
    with open('idMot.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if mot == liste[1].replace("\"", ""):
                return liste[0]


def getIdWord(id):
    with open('idMot.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if id == liste[0]:
                return liste[1].replace("\"", "")







def extraction_relation(terme, relation):
    html = requests.get(
        "http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=" + terme + "&rel=" + relation)
    soup = BeautifulSoup(html.content, 'html.parser', from_encoding='iso-8859-1')
    texte_brut = soup.find_all('code')
    lignes_noeuds_et_relations = re.findall('[r];[0-9]*;.*', str(texte_brut))
    print(len(lignes_noeuds_et_relations))
    counter = 0
    filename = getWordId(terme)
    for r in lignes_noeuds_et_relations:
        splitedRelation = r.split(";")
        # print(splitedRelation)
        print(counter)
        counter+=1
        if splitedRelation[2] == str(filename):
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
        elif splitedRelation[3] == str(filename):
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

    with open('Cache/' + filename + '.json', 'w+') as output:
        json.dump(data, output)

# detectInference("Tour Eiffel","","France")
#extraction_relation("Tour Eiffel", "r_lieu")
#extraction_relation("France", "r_lieu")

def detectInference(mot1, relation, mot2):
    idmot1 = getWordId(mot1)
    idmot2 = getWordId(mot2)
    with open('Cache/' + idmot1 + '.json') as relationmot1, open('Cache/' + idmot2 + '.json') as relationmot2:
        data = json.load(relationmot1)
        data2 = json.load(relationmot2)
        for i in data:
            if i["r"] == "sortante":
                for j in data2:
                    if j["r"] == "entrante" and j["node1"] == i["node2"]:
                        print(getIdWord(j["node1"]))
                        print(j["node1"])

#extraction_relation("piston", "r_holo")
#extraction_relation("voiture", "r_holo")
#detectInference("piston","","voiture")
print(getIdWord("5425"))