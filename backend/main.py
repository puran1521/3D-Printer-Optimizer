# backend/main.py
"""
Main entry point for the backend server.
Handles API requests for topology optimization.
"""

from flask import Flask, request, jsonify
from backend.optimizer import TopologyOptimizer
from backend.config import OptimizationConfig
import logging

app = Flask(__name__)

optimizer = TopologyOptimizer()

@app.route('/api/optimize', methods=['POST'])
def optimize():
    """
    API endpoint to perform topology optimization.
    Expects a JSON request with an STL file path.
    """
    try:
        data = request.get_json()
        stl_path = data.get('stl_path')

        if not stl_path:
            return jsonify({"error": "Missing STL file path"}), 400

        result = optimizer.optimize(stl_path)
        return jsonify({"success": True, "result": result.tolist()}), 200
    except Exception as e:
        logging.error(f"Optimization error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """API health check endpoint."""
    return jsonify({"status": "ok"}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Welcome to the 3D Printer Optimizer API"}), 200

if __name__ == '__main__':
    app.run(debug=True)
    print(app.url_map)
