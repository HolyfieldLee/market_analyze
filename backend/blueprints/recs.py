
from flask import Blueprint, request, jsonify
from ..services.recsys import compute_score

recs_bp = Blueprint("recs", __name__)

@recs_bp.post("/score")
def score():
    data = request.get_json() or {}
    features = data.get("features", {})
    result = compute_score(features)
    return jsonify(result), 200

@recs_bp.get("/sample")
def sample():
    # Dummy sample list for FE integration (React / SwiftUI)
    candidates = [
        {
            "area_id": "A-101",
            "area_name": "강남역 11번 출구",
            "features": {"foot_traffic": 0.9, "competitors_500m": 0.3, "avg_income": 0.8, "rent_cost": 0.6, "age_20s_ratio": 0.7}
        },
        {
            "area_id": "A-202",
            "area_name": "홍대입구역 2번 출구",
            "features": {"foot_traffic": 0.85, "competitors_500m": 0.4, "avg_income": 0.7, "rent_cost": 0.5, "age_20s_ratio": 0.8}
        },
        {
            "area_id": "A-303",
            "area_name": "서면역 1번 출구",
            "features": {"foot_traffic": 0.75, "competitors_500m": 0.35, "avg_income": 0.6, "rent_cost": 0.45, "age_20s_ratio": 0.65}
        }
    ]
    enriched = []
    for c in candidates:
        result = compute_score(c["features"])
        enriched.append({
            **c,
            "score": result["score"],
            "breakdown": result["breakdown"]
        })
    return jsonify({"items": enriched}), 200

