from flask import Flask, request, jsonify app = Flask(name)
PERMANENT_KEY = 'live_1234abcd'
@app.route('/') def api(): key = request.args.get('key') if key != PERMANENT_KEY: return jsonify({'status': 'error', 'message': 'Invalid key'}) return jsonify({ 'status': 'success', 'key': PERMANENT_KEY, 'expires': 'never', 'message': '✅ Permanent API key is active!' })
if name == 'main': app.run(host='0.0.0.0', port=10000)
