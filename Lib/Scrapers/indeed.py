# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from requests import Session
from parsel import Selector
from time import sleep

oturum = Session()
oturum.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"})

def indeed_maas_ver(sirket:str, ulke_kodu:str=None):
    if not ulke_kodu:
        salary_istek  = oturum.get(f"https://www.indeed.com/cmp/{sirket}/salaries")
    else:
        salary_istek  = oturum.get(f"https://{ulke_kodu.lower()}.indeed.com/cmp/{sirket}/salaries")
    salary_secici = Selector(salary_istek.text)

    # veri = {
    #     "average": {
    #         ortalama.xpath("normalize-space(./h3)").get(): {
    #             maas.xpath("normalize-space(./a/span)").get(): maas.xpath("normalize-space(./a/div)").get()
    #             for maas in ortalama.xpath("./div[contains(@class, 'SalaryCategoryCard')]")
    #         }
    #         for ortalama in salary_secici.xpath("//section[contains(@class, 'SalaryCategorySummary')]/h2/following::div[contains(@data-tn-element, 'salary-v2-category')]")
    #     },
    #     "category": {
    #         kategori.xpath("normalize-space(./h2)").get(): {
    #             maas.xpath("normalize-space(.//div[contains(@class, 'SalarySummaryTitle')]/div/div)").get(): maas.xpath("normalize-space(.//div[contains(@class, 'SalarySummary-columnsAverage')]/div/span)").get().split("}")[-1].strip()
    #             for maas in kategori.xpath("./following::a[contains(@class, 'SalarySummary')]")
    #         }
    #         for kategori in salary_secici.xpath("//div[contains(@class, 'SalaryCategory')]")
    #     }
    # }

    # veri = {"average": veri['average'], "category" : dict(reversed(list(veri['category'].items())))}

    # temp = []
    # res  = {}
    # for master in veri['category'].keys():
    #     for key, val in veri['category'][master].items():
    #         if key not in temp and key:
    #             temp.append(key)
    #             try:
    #                 res[master][key] = veri['category'][master][key]
    #             except KeyError:
    #                 res[master] = {}
    #                 res[master][key] = veri['category'][master][key]

    # return {"average": veri['average'], "category" : dict(reversed(list(res.items())))}

    veri = {
        maas.xpath("normalize-space(.//div[contains(@class, 'SalarySummaryTitle')]/div/div)").get(): maas.xpath("normalize-space(.//div[contains(@class, 'SalarySummary-columnsAverage')]/div/span)").get().split("}")[-1].strip()
            for maas in salary_secici.xpath("//div/following::a[contains(@class, 'SalarySummary')]")
    }

    meslek_kaegoriler = salary_secici.xpath("//a[@data-tn-element='salary-category-filter-under-group']/@href").getall()
    if not meslek_kaegoriler:
        return veri

    for kategori_point in meslek_kaegoriler:
        if not ulke_kodu:
            kategori_istek  = oturum.get(f"https://www.indeed.com{kategori_point}")
        else:
            kategori_istek  = oturum.get(f"https://{ulke_kodu.lower()}.indeed.com{kategori_point}")
        kategori_secici = Selector(kategori_istek.text)

        veri.update({
            maas.xpath("normalize-space(.//div[contains(@class, 'SalarySummaryTitle')]/div/div)").get(): maas.xpath("normalize-space(.//div[contains(@class, 'SalarySummary-columnsAverage')]/div/span)").get().split("}")[-1].strip()
                for maas in kategori_secici.xpath("//div/following::a[contains(@class, 'SalarySummary')]")
        })

        sleep(3)

    return veri

import json
with open("SETTINGS.json", "r+") as dosya:
    indeed_ulkeler = json.load(dosya)["Indeed_Countries"]

def indeed_ver(sirket:str, proxi=None):
    if proxi:
        proxi_part = proxi.split(":")
        if len(proxi_part) == 4:
            p_ip, p_port, p_user, p_pass = proxi_part
            proxi = {
                'http'  : f'http://{p_user}:{p_pass}@{p_ip}:{p_port}',
                'https' : f'http://{p_user}:{p_pass}@{p_ip}:{p_port}',
            }
        elif len(proxi_part) == 2:
            p_ip, p_port = proxi_part
            proxi = {
                'http'  : f'http://{p_ip}:{p_port}',
                'https' : f'http://{p_ip}:{p_port}',
            }
        oturum.proxies.update(proxi)

    snapshot_istek  = oturum.get(f"https://www.indeed.com/cmp/{sirket}")
    if snapshot_istek.status_code != 200:
        return None

    snapshot_secici = Selector(snapshot_istek.text)

    veri = {
        "company_name"       : snapshot_secici.xpath("//div[@itemprop='name']/text()").get(),
        "founded"            : snapshot_secici.xpath("//div[text()='Founded']/following::div/text()").get(),
        "industry"           : snapshot_secici.xpath("//div[text()='Industry']/following::div/text()").get(),
        "overall_rating"     : snapshot_secici.xpath("//span[contains(text(), 'out of 5 stars.')]/following::span/text()").get(),
        "rating_by_category" : {
            "work_life_balance"         : snapshot_secici.xpath("normalize-space(//span[text()='Work & Life Balance']/preceding-sibling::div//text())").get(),
            "compensation_and_benefits" : snapshot_secici.xpath("normalize-space(//span[text()='Compensation & Benefits']/preceding-sibling::div//text())").get(),
            "job_security_advancement"  : snapshot_secici.xpath("normalize-space(//span[text()='Job Security & Advancement']/preceding-sibling::div//text())").get(),
            "management"                : snapshot_secici.xpath("normalize-space(//span[text()='Management']/preceding-sibling::div//text())").get(),
            "culture"                   : snapshot_secici.xpath("normalize-space(//span[text()='Culture']/preceding-sibling::div//text())").get(),
        },
        "salary_by_countries": {"us" : indeed_maas_ver(sirket)}
    }

    # for ulke in indeed_ulkeler:
    #     ulke_maas = indeed_maas_ver(sirket, ulke)
    #     sleep(3)
    #     # if not ulke_maas["average"] and not ulke_maas["category"]:
    #     if not ulke_maas:
    #         continue

    #     veri["salary_by_countries"][ulke] = ulke_maas

    #     # print("-"*50 + f" {ulke} " + "-"*50)
    #     # print(ulke_maas)
    #     # print("-"*104)

    return veri