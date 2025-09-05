from flask import Blueprint, render_template

core_bp = Blueprint("core", __name__)

@core_bp.get("/home")
def home():
    return render_template("home.html")

@core_bp.get("/about")
def about():
    return render_template("about.html")
