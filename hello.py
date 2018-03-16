import sys
import random
import organized
import json
from owlready2 import *

from flask import Flask, render_template, jsonify, request

def create_app():
    print("Starting App")
    app = Flask(__name__)
    #onto = organized.init()
    #onto.save(file = "currweb.owl", format = "rdfxml")
    onto = get_ontology("file:///Users/william/Dropbox/BMI210/Final_Project/currweb.owl").load()
    print("Finished Init")
    return app, onto

app, onto = create_app()

BASECOORDS = [-13.9626, 33.7741]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/list-patients', methods=['GET', 'POST'])
def list_patients():
    patients = []
    for pt in onto.Patient.instances():
        pt_loc = {'lat': pt.latitude[0], 'lng': pt.longitude[0]}
        pt_organ = pt.organ[0]
        patient = {'loc': pt_loc, 'organ': pt_organ}
        patients.append(patient)
    return jsonify(patients)

@app.route('/find-matches', methods=['GET'])
def find_matches():
    hla = int(request.args.get('hlatype'))
    blood = request.args.get('bloodtype')
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('long'))
    kidney = True if request.args.get('kidney') else False
    liver = True if request.args.get('liver') else False
    donor = {'kidney': kidney,'liver': liver, 'blood_type': blood, 'hla_dr': hla, 'latitude': lat, 'longitude': lon}

    print("DONOR")
    print(donor)
    
    results = organized.find_matching_patients(onto, donor)
    jsonobj = {"kidney": [], "liver": []}
    for pt, score in results["kidney"]:
        jsonobj["kidney"].append({"name": pt.name, "lat": pt.latitude[0], "long": pt.longitude[0], "score": score,
            "age": pt.age[0], "bloodtype": pt.blood_type[0], "hla_dr": pt.hla_dr[0], "wait": pt.wait_time[0],
            "dialysis": pt.dialysis_time[0], "prior": pt.is_prior_donor[0]})

    for pt, score in results["liver"]:
        jsonobj["liver"].append({"name": pt.name, "lat": pt.latitude[0], "long": pt.longitude[0], "score": score,
            "age": pt.age[0], "bloodtype": pt.blood_type[0], "hla_dr": pt.hla_dr[0], "wait": pt.wait_time[0]})

    if not kidney:
        jsonobj['kidney'] = []

    if not liver:
        jsonobj['liver'] = []

    print(jsonobj)
    return jsonify(jsonobj)


if __name__ == '__main__':
    app.run(debug=True)