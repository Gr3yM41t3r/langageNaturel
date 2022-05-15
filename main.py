
import requests
from bs4 import BeautifulSoup



def htmlscrappin(terme, relation):
    html = requests.get("http://www.jeuxdemots.org/rezo-dump.php?gotermsubmit=Chercher&gotermrel=chat&rel=")
    print(html)
    soup = BeautifulSoup(html.content, 'html.parser', from_encoding='iso-8859-1')
    texte_brut = soup.find_all('code')
    print(texte_brut)


htmlscrappin("","")