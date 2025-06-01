# routes/eda_routes.py

from flask import Blueprint
from flask_cors import CORS
from controllers.eda_controller import EDAController

eda_controller = EDAController()
eda_bp = Blueprint("eda_bp", __name__)
CORS(eda_bp, supports_credentials=True)

# Register EDA-related endpoints
eda_bp.add_url_rule("/eda_visual", view_func=eda_controller.generate_plot, methods=["POST"])


eda_bp.add_url_rule(
    "/save_plot", 
    view_func=eda_controller.save_plot, 
    methods=["POST"]
)

eda_bp.add_url_rule(
    "/get_plots/<user_id>", 
    view_func=eda_controller.get_plots, 
    methods=["GET"]
)

eda_bp.add_url_rule(
    "/delete_plot/<plot_id>", 
    view_func=eda_controller.delete_plot, 
    methods=["DELETE"]
)
