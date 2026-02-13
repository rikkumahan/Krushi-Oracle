"""
Nova AI Service - Flask Application (Python 3.14 Safe)
Handles idea generation, scoring, and verification.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import dataclasses

# Services
from verification.unit_economics import UnitEconomicsSimulator, UnitEconomicsInput
from verification.tech_feasibility import TechFeasibilityService
from services.idea_generator import IdeaGeneratorService
from models.schemas import WizardInput

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Helper to serialize dataclasses
def to_dict(obj):
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    return obj

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "version": "2.0.0-flask", "mode": "TURBO"})

@app.route("/api/v2/verification/economics", methods=["POST"])
def check_unit_economics():
    try:
        data = request.json
        inputs = UnitEconomicsInput(
            arpu_monthly=float(data.get("arpu_monthly", 0)),
            gross_margin_pct=float(data.get("gross_margin_pct", 0)),
            churn_rate_monthly=float(data.get("churn_rate_monthly", 0)),
            cpc=float(data.get("cpc", 0)),
            conversion_rate_landing=float(data.get("conversion_rate_landing", 0)),
            conversion_rate_payment=float(data.get("conversion_rate_payment", 0))
        )
        
        result = UnitEconomicsSimulator.calculate(inputs)
        return jsonify(result.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/v2/verification/feasibility", methods=["POST"])
def check_tech_feasibility():
    try:
        data = request.json
        idea_name = data.get("idea_name")
        description = data.get("description")
        
        if not idea_name or not description:
            return jsonify({"error": "Missing idea_name or description"}), 400
            
        service = TechFeasibilityService()
        report = service.analyze_feasibility(idea_name, description)
        return jsonify(report.to_dict())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/ideas/generate", methods=["POST"])
def generate_ideas():
    try:
        data = request.json
        # Parse WizardInput from JSON
        # Note: Enum conversion happens in WizardInput.from_dict
        wizard_input = WizardInput.from_dict(data.get("wizard_input", {}))
        num_ideas = int(data.get("num_ideas", 5))
        
        service = IdeaGeneratorService()
        response = service.generate_ideas(wizard_input, num_ideas)
        
        return jsonify(response.to_dict())
    except Exception as e:
        print(f"Generation Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
