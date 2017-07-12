# -*- coding: utf-8 -*-


from flask import Blueprint

from models.role import Permission

main = Blueprint('main', __name__)


@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)


@main.context_processor
def inject_enumerate():
    return dict(enumerate=enumerate)
