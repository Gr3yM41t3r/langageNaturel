import json
import re
import requests
from bs4 import BeautifulSoup
import os.path
import time

data = []

relatiuon_deductive = ['r_isa', 'r_holo']
relatiuon_inductive = ['r_hypo', 'r_has_part']
relation_inductive_interdis=['r_lieu']
relatiuon_transitive = ['r_lieu', 'r_lieu-1', 'r_isa', 'r_hypo']


def getWordId(mot):
    with open('Cache/searchLog.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if mot == liste[1]:
                return liste[0]
    return 0


def ismotandrelation_searched(mot, relation):
    with open('Cache/searchLog.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if len(liste) > 1:
                if mot == liste[1].replace("\"", "") and relation == liste[3].replace("\"", ""):
                    return True
    return False


def getRealationId(relation):
    with open('Cache/searchLog.txt') as listedemot:
        for i in listedemot:
            liste = i.split(";")
            if relation == liste[3]:
                return liste[2]
    return 0


def getIdWord(idrelation, origin, id):
    with open('Cache/' + idrelation + "/" + origin + ".json") as listedemot:
        data = json.load(listedemot)
        for i in data:
            if i['id'] == "e":
                if i['eid'] == id:
                    return i['mot'].replace("'", "")


def extraction_relation_html(word, relation):
    html = requests.get(
        "http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=" + word + "&rel=" + relation)
    soup = BeautifulSoup(html.content, 'html.parser')
    texte_brut = soup.find_all('code')
    data.clear()
    lignes_noeuds_et_relations = re.findall('[re];[0-9]*;.*', str(texte_brut))
    id_relation = ''
    id_terme = lignes_noeuds_et_relations[0].split(";")[1]
    with open('Cache/Texte/'+word+"_"+relation+".txt",'a+') as output:
        output.write(str(texte_brut))
        output.close()
    for r in lignes_noeuds_et_relations:
        splitedRelation = r.split(";")
        if splitedRelation[0] == "r":
            if splitedRelation[2] == str(id_terme):
                data.append(
                    {
                        "id": splitedRelation[0],
                        "r": "sortante",
                        "rid": splitedRelation[1],
                        "node1": splitedRelation[2],
                        "node2": splitedRelation[3],
                        "type": splitedRelation[4],
                        "w": splitedRelation[5]
                    }
                )
                id_relation = splitedRelation[4]
            elif splitedRelation[3] == str(id_terme):
                data.append(
                    {
                        "id": splitedRelation[0],
                        "r": "entrante",
                        "rid": splitedRelation[1],
                        "node1": splitedRelation[2],
                        "node2": splitedRelation[3],
                        "type": splitedRelation[4],
                        "w": splitedRelation[5]
                    }
                )
                id_relation = splitedRelation[4]
        elif splitedRelation[0] == "e":
            data.append(
                {
                    "id": splitedRelation[0],
                    "eid": splitedRelation[1],
                    "mot": splitedRelation[2],
                }
            )

    if id_relation == '':
        return False
    if os.path.isdir('Cache/' + id_relation + '/'):
        with open('Cache/' + id_relation + '/' + id_terme + '.json', 'a+') as output:
            json.dump(data, output)
    else:
        os.mkdir('Cache/' + id_relation + '/')
        with open('Cache/' + id_relation + '/' + id_terme + '.json', 'a+') as output:
            json.dump(data, output)
    with  open('Cache/searchLog.txt', 'a+') as listedemot:
        listedemot.write(id_terme + ";" + word + ";" + id_relation + ";" + relation + ";" + "\n")
        listedemot.close()
    return True


def createCache(terme, relation):
    if ismotandrelation_searched(terme, relation):
        return True
    else:
        return extraction_relation_html(terme, relation)


def transitive(mot1, relation, mot2, maxsolutions):
    idmot1 = getWordId(mot1)
    idmot2 = getWordId(mot2)
    idrelation = getRealationId(relation)

    with open('Cache/' + idrelation + '/' + idmot1 + '.json') as relationmot1, open(
            'Cache/' + idrelation + '/' + idmot2 + '.json') as relationmot2:
        data = json.load(relationmot1)
        data2 = json.load(relationmot2)
        transitive_array1 = []
        transitive_array2 = []
        weight = {}
        for i in data:
            if i['id'] == "r" and int(i['w'])>0:
                if i['r'] == "sortante":
                    transitive_array1.append(i['node2'])
        for j in data2:
            if j['id'] == "r":
                if j['r'] == "entrante" and int(j['w'])>0:
                    transitive_array2.append(j['node1'])
                    weight.update({j['node1']: j['w']})

        intersection = list(set(transitive_array1) & set(transitive_array2))
        search_dico = {}
        printing_dic = {}
        counter = 0
        with open('Cache/' + idrelation + "/" + idmot2 + ".json") as dddd:
            vv = json.load(dddd)
            for n in vv:
                if n['id'] == "e":
                    search_dico.update({n['eid']: n['mot']})
        for l in intersection:
            counter += 1
            jnode1 = search_dico.get(l)
            printing_dic.update({
                str(counter) + ") oui parceque " + mot1 + " " + relation + " " + jnode1 + " and " + jnode1 + " " + relation + " " + mot2 + "  --weigth: " + weight.get(
                    l): int(weight.get(l))})

        for i in sorted(printing_dic, key=printing_dic.get, reverse=True):
            if maxsolutions > 0:
                print(i)
                maxsolutions -= 1
        ''' for i in data:
                if i['id'] == "r":
                    if i['r'] == "sortante":
                        for j in data2:
                            if j['id'] == "r":
                                if j["r"] == "entrante" and j["node1"] == i["node2"]:
                                    jnode1 = getIdWord(idrelation, idmot1, i["node2"])
                                    print(
                                        "oui parceque " + mot1 + " " + relation + " " + jnode1 + " et " + jnode1 + " " + relation + " " + mot2 + " w" +
                                        j['w'])'''


def deductive(mot1, relation, mot2, maxsolutions):
    start = time.process_time()
    idmot1 = getWordId(mot1)
    idmot2 = getWordId(mot2)
    idrelation = getRealationId(relation)
    for i in relatiuon_deductive:
        if not createCache(mot1, i): return
        deductive_relation_id = getRealationId(i)

        with open('Cache/' + deductive_relation_id + '/' + idmot1 + '.json') as relationmot1, open(
                'Cache/' + idrelation + '/' + idmot2 + '.json') as relationmot2:
            data = json.load(relationmot1)
            data2 = json.load(relationmot2)
            first = []
            second = []
            weight = {}
            for j in data:
                if j['id'] == "r":
                    if int(j['w']) > 0 and j['r'] == "sortante":
                        first.append(j['node2'])
                        weight.update({j['node2']: j['w']})
            for k in data2:
                if k['id'] == "r" and int(k['w']) > 0:
                    second.append(k['node1'])

            intersection = list(set(first) & set(second))
            printing_dic = {}
            counter = 0
            search_dico = {}
            with open('Cache/' + idrelation + "/" + idmot2 + ".json") as dddd:
                vv = json.load(dddd)
                for n in vv:
                    if n['id'] == "e":
                        search_dico.update({n['eid']: n['mot']})
            for l in intersection:
                counter += 1
                jnode1 = search_dico.get(l)
                printing_dic.update({
                    str(counter) + ") oui parceque " + mot1 + " " + i + " " + jnode1 + " and " + jnode1 + " " + relation + " " + mot2 + "  --weigth: " + weight.get(
                        l): int(weight.get(l))})
            for i in sorted(printing_dic, key=printing_dic.get, reverse=True):
                if maxsolutions > 0:
                    print(i)
                    maxsolutions -= 1


def inductive(mot1, relation, mot2, maxsolutions):
    idmot1 = getWordId(mot1)
    idmot2 = getWordId(mot2)
    idrelation = getRealationId(relation)
    for i in relatiuon_inductive:
        if not createCache(mot1, i): return
        deductive_relation_id = getRealationId(i)
        with open('Cache/' + deductive_relation_id + '/' + idmot1 + '.json') as relationmot1, open(
                'Cache/' + idrelation + '/' + idmot2 + '.json') as relationmot2:
            data = json.load(relationmot1)
            data2 = json.load(relationmot2)
            first = []
            second = []
            weight = {}
            for j in data:
                if j['id'] == "r":
                    if int(j['w']) > 0 and j['r'] == "sortante":
                        first.append(j['node2'])
                        weight.update({j['node2']: j['w']})

            for k in data2:
                if k['id'] == "r" and int(k['w']) > 0:
                    second.append(k['node1'])
            intersection = list(set(first) & set(second))
            printing_dic = {}
            counter = 0
            search_dico = {}
            with open('Cache/' + idrelation + "/" + idmot2 + ".json") as dddd:
                vv = json.load(dddd)
                for n in vv:
                    if n['id'] == "e":
                        search_dico.update({n['eid']: n['mot']})
            for l in intersection:
                counter += 1
                jnode1 = search_dico.get(l)
                printing_dic.update({
                    str(counter) + ") oui parceque " + mot1 + " " + i + " " + jnode1 + " and " + jnode1 + " " + relation + " " + mot2 + "  --weigth: " + weight.get(
                        l): int(weight.get(l))})
            for i in sorted(printing_dic, key=printing_dic.get, reverse=True):
                if maxsolutions > 0:
                    print(i)
                    maxsolutions -= 1


def detectInfernce(mot1, relation, mot2, maxsolutions):
    if not createCache(mot2, relation):
        return
    if not createCache(mot1, relation):
        return
    print("_______________________transitive___________________________")
    transitive(mot1, relation, mot2, maxsolutions)
    print("_______________________inductive___________________________")
    inductive(mot1, relation, mot2, maxsolutions)
    print("_______________________deductive___________________________")
    deductive(mot1, relation, mot2, maxsolutions)


print("************************Mini projet sur les inférences************************")
while True:
    mot1 = input("entrez le 1er mot  : ")
    if mot1 == '' :
        break
    relation = input("entrez la relation  :  ")
    if relation == '':
        break

    mot2 = input("entrez le 2eme mot  :  ")
    if mot2 == '':
        break
    maxsolution = input("entrez le nombre maximum de solution(vide = toutes les solutions)  :  ")
    if mot1 == '' or mot2 == '' or relation == '':
        break
    if maxsolution == '':
        maxsolution = 10000
    detectInfernce(mot1, relation, mot2, int(maxsolution))
print("************************The End************************")
