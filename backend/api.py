import cProfile
import io
import pstats
from flask import Flask, request, jsonify
from backend.optimizer import TopologyOptimizer
from backend.config import OptimizationConfig
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

optimizer = TopologyOptimizer()

def profile_function(func):
    """Decorator to profile an endpoint."""
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        result = func(*args, **kwargs)
        pr.disable()

        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(10)  # Show the top 10 slowest calls
        logger.info(f"Performance stats for {func.__name__}:\n{s.getvalue()}")

        return result
    return wrapper

@app.route('/optimize', methods=['POST'])
@profile_function
def optimize():
    try:
        data = request.get_json()
        stl_path = data.get('stl_path')
        if not stl_path:
            return jsonify({'error': 'Missing STL file path'}), 400

        result = optimizer.optimize(stl_path)
        return jsonify({'success': True, 'result': result}), 200
    except Exception as e:
        logger.error(f"Optimization error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True)