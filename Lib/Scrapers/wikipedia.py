# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from Lib.wikisearch.wikisearcher import WikiSearcher
from re import sub

def wiki_ver(sirket:str):
    wiki = WikiSearcher()

    try:
        arama_sonucu = wiki.search(sirket)
    except Exception:
        return None
    if not isinstance(arama_sonucu, str):
        return None

    temiz_metin = arama_sonucu.replace("\n", " ").strip()
    return sub(' +', ' ', temiz_metin)
