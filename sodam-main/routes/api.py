from flask import Blueprint, request, jsonify
from extensions import db
from models import User, Interest, Region
import pandas as pd
import os

api_bp = Blueprint("api", __name__, url_prefix="/api")

@api_bp.get("/ping")
def ping():
    return jsonify(ok=True, service="sodam", message="pong")

@api_bp.post("/echo")
def echo():
    data = request.get_json(silent=True) or request.form.to_dict()
    return jsonify(received=data), 201

@api_bp.post("/auth/signup")
def signup():
    data = request.get_json() or {}
    email = data.get("email")
    if not email:
        return jsonify(error="email is required"), 400
    if User.query.filter_by(email=email).first():
        return jsonify(error="email already exists"), 409
    user = User(email=email)
    db.session.add(user)
    db.session.commit()
    return jsonify(id=user.id, email=user.email), 201

@api_bp.post("/profile/preferences")
def set_preferences():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    interests = data.get("interests", [])
    regions = data.get("regions", [])

    user = User.query.get(user_id)
    if not user:
        return jsonify(error="user not found"), 404

    interest_objs, region_objs = [], []
    for name in interests:
        obj = Interest.query.filter_by(name=name).first()
        if not obj:
            obj = Interest(name=name)
            db.session.add(obj)
        interest_objs.append(obj)

    for name in regions:
        obj = Region.query.filter_by(name=name).first()
        if not obj:
            obj = Region(name=name)
            db.session.add(obj)
        region_objs.append(obj)

    db.session.commit()
    return jsonify(ok=True, interests=[i.name for i in interest_objs], regions=[r.name for r in region_objs])

@api_bp.get("/trends")
def trends():
    region = request.args.get("region", "강남구")
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "foot_traffic.csv")
    data_path = os.path.abspath(data_path)
    out = []
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        out = (df[df["region"] == region]
                .groupby("hour")["visitors"].sum()
                .reset_index()
                .to_dict(orient="records"))
    return jsonify(region=region, hourly=out)
