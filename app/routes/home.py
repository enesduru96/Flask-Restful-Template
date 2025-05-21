from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity

home_bp = Blueprint("home", __name__)

@home_bp.route("/home")
@jwt_required()
def home():
    username = get_jwt_identity()
    return render_template("home.html", username=username)