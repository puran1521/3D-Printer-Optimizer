from flask import Flask, request, jsonify
from .optimizer import TopologyOptimizer
from .config import OptimizationConfig
import logging
from functools import lru_cache  # Simple in-memory cache example

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize optimizer globally (if configuration is fixed)
optimizer = TopologyOptimizer()

# Optionally, cache optimization results (if the same STL is re-used)
@lru_cache(maxsize=10)
def cached_optimization(stl_path):
    config = OptimizationConfig()
    opt = TopologyOptimizer(config)
    result = opt.optimize(stl_path)
    return result.tolist()

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        stl_path = data.get('stl_path')
        if not stl_path:
            return jsonify({'error': 'Missing STL file path'}), 400

        # Use cache if available; otherwise run optimization
        result = cached_optimization(stl_path)
        return jsonify({'success': True, 'result': result}), 200
    except Exception as e:
        logger.error(f"Optimization error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)