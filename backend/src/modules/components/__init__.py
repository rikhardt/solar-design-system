from flask import Blueprint

components = Blueprint('components', __name__)

from . import models, routes
