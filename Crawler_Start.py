# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from FlaskAPI import konsol, FlaskAPIDB
from Lib import wiki_ver, indeed_ver, glassdoor_ver

from time import sleep

import json
with open("SETTINGS.json", "r+") as dosya:
    sirketler = json.load(dosya)["Companies"]

from random import choice
with open("proxies.txt", "r+") as dosya:
    PROXILER = [satir.replace("\n", "").strip() for satir in dosya]

def sirket_ekle(sirket:str):
    db = FlaskAPIDB()
    # if db.data_ver(sirket):
    #     return False

    konsol.log(f"[yellow][💾] {sirket} Crawl Ediliyor")

    try:
        glass_veri = glassdoor_ver(sirket, choice(PROXILER) if PROXILER else None)
    except Exception:
        glass_veri = None

    veri = {
        "company"   : sirket,
        "wikipedia" : wiki_ver(sirket),
        "indeed"    : indeed_ver(sirket, choice(PROXILER) if PROXILER else None),
        "glassdoor" : glass_veri
    }

    db.ekle(veri)

    konsol.log(f"[green][✅] {sirket} Database'e Eklendi")

    return True

def crawler_func():
    for sirket in sirketler:
        eklendi = sirket_ekle(sirket)
        # break
        if eklendi:
            sleep(15)

import schedule
from time import sleep

schedule.every(7).days.do(crawler_func)

if __name__ == "__main__":
    try:
        crawler_func()
    except Exception as hata:
        konsol.log(f'[bold red]{type(hata).__name__} | {hata}[/]')

    while True:
        try:
            schedule.run_pending()
        except Exception as hata:
            konsol.log(f"[bold red]{type(hata).__name__} | {hata}[/]")
            continue
        finally:
            sleep(1)