# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from FlaskAPI import app, FlaskAPIDB
from flask import request, render_template, jsonify, abort

@app.route('/')
def ana_sayfa():
    return abort(403)
    # return render_template('_davetsiz.html')

@app.route('/data')
def data():
    sirket = request.args.get('company')
    ulke   = request.args.get('location')

    if not sirket:
        return abort(404)

    # if sirket != "Google":
    #     return abort(403)

    db = FlaskAPIDB()
    arama_sonucu = db.data_ver(sirket)

    if not arama_sonucu:
        return abort(404)

    if not ulke:
        return jsonify(arama_sonucu)

    veri = arama_sonucu.copy()
    if arama_sonucu["glassdoor"]:
        if ulke in arama_sonucu["glassdoor"]["overall_rating_by_countries"].keys():
            veri["glassdoor"]["overall_rating"] = arama_sonucu["glassdoor"]["overall_rating_by_countries"][ulke]
        else:
            veri["glassdoor"]["overall_rating"] = None

        if ulke in arama_sonucu["glassdoor"]["rating_by_category_by_countries"].keys():
            veri["glassdoor"]["rating_by_category"] = arama_sonucu["glassdoor"]["rating_by_category_by_countries"][ulke]
        else:
            veri["glassdoor"]["rating_by_category"] = None

        del veri["glassdoor"]["overall_rating_by_countries"]
        del veri["glassdoor"]["rating_by_category_by_countries"]

    return jsonify(veri)

@app.route('/companies')
def companies():
    db = FlaskAPIDB()
    return jsonify(adet=len(db.sirketler), sirketler=db.sirketler)