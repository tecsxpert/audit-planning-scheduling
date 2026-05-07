from flask import Flask

from .categorise import categorise_bp
from .generate_report import report_bp
from .health import health_bp
from .query import query_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(health_bp)
    app.register_blueprint(categorise_bp)
    app.register_blueprint(query_bp)
    app.register_blueprint(report_bp)
