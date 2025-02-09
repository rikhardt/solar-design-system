from flask import jsonify, request
from . import components
from .models import Manufacturer, SolarPanel, Inverter, Battery, MountingStructure, ShadowAnalysis
from src import db

@components.route('/test', methods=['GET'])
def test():
    """Endpoint de prueba"""
    return jsonify({"message": "El servidor está funcionando correctamente"})

@components.route('/manufacturers', methods=['GET'])
def get_manufacturers():
    """Listar todos los fabricantes"""
    manufacturers = Manufacturer.query.all()
    return jsonify([m.to_dict() for m in manufacturers])

@components.route('/panels', methods=['GET'])
def get_panels():
    """Listar todos los paneles solares"""
    panels = SolarPanel.query.all()
    return jsonify([p.to_dict() for p in panels])

@components.route('/inverters', methods=['GET'])
def get_inverters():
    """Listar todos los inversores"""
    inverters = Inverter.query.all()
    return jsonify([i.to_dict() for i in inverters])

@components.route('/batteries', methods=['GET'])
def get_batteries():
    """Listar todas las baterías"""
    batteries = Battery.query.all()
    return jsonify([b.to_dict() for b in batteries])

@components.route('/mounting-structures', methods=['GET'])
def get_mounting_structures():
    """Listar todas las estructuras de montaje"""
    structures = MountingStructure.query.all()
    return jsonify([s.to_dict() for s in structures])

@components.route('/shadow-analyses', methods=['GET'])
def get_shadow_analyses():
    """Listar todos los análisis de sombras"""
    analyses = ShadowAnalysis.query.all()
    return jsonify([a.to_dict() for a in analyses])
