from flask import Flask, request, jsonify
from .optimizer import TopologyOptimizer
from .config import OptimizationConfig
import numpy as np

app = Flask(__name__)

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.json
        if not data or 'stl_path' not in data:
            return jsonify({'error': 'Missing stl_path'}), 400

        config = OptimizationConfig()
        optimizer = TopologyOptimizer(config)
        result = optimizer.optimize(data['stl_path'])
        
        # Convert numpy array to list if needed
        if isinstance(result, np.ndarray):
            result = result.tolist()
            
        return jsonify({'result': result}), 200
    except Exception as e:
        print(f"Error in optimization: {str(e)}")  # Debug logging
        return jsonify({'error': str(e)}), 500