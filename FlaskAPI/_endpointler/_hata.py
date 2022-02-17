# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from FlaskAPI import app
from flask import make_response, jsonify, send_from_directory
import os

istekler = {}

@app.route('/favicon.ico', methods=['GET'])
def favicon():
    return send_from_directory(directory=os.path.join(app.root_path, 'static'), filename='images/favicon.ico', mimetype='image/x-icon')

@app.errorhandler(404)
def dort_yuz_dort(error):
    return make_response(jsonify(FlaskAPI='Sayfa Bulunamadı..', istekler=istekler), 404)

@app.errorhandler(403)
def dort_yuz_uc(error):
    return make_response(jsonify(FlaskAPI='Bu Sayfaya Erişim İzniniz Yoktur..!', istekler=istekler), 403)

@app.errorhandler(410)
def dort_yuz_on(error):
    return make_response(jsonify(FlaskAPI='Sayfa Taşınmış Olabilir..', istekler=istekler), 410)

@app.errorhandler(500)
def bes_yuz(error):
    return make_response(jsonify(FlaskAPI='Düzgün Argüman Verilmedi.. » (Sunucu Hatası Oluştu!)', istekler=istekler), 500)