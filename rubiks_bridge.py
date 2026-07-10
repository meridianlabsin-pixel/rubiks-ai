"""
RUBIKS Bridge Server v1.0 (fixed)
"""

import queue
import json
import time
import threading
from flask import Flask, request, Response, jsonify, make_response

app = Flask(__name__)

# ── Shared queues ───────────────────────────────────────────────────────────
command_queue = queue.Queue()    # HTML → main.py
_subscribers  = []
_sub_lock     = threading.Lock()

def push_output(text: str):
    """Called by main.py to stream a line of output to the HUD."""
    payload = json.dumps({"text": text, "ts": time.time()})
    with _sub_lock:
        dead = []
        for q in _subscribers:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for d in dead:
            _subscribers.remove(d)

def _is_speaking():
    """Helper to check if RUBIKS is currently playing audio"""
    try:
        import pygame
        if pygame.mixer.get_init():
            if pygame.mixer.music.get_busy():
                return True
    except:
        pass
    return False

# ── CORS helper ─────────────────────────────────────────────────────────────
def cors(resp):
    r = make_response(resp)
    r.headers['Access-Control-Allow-Origin']  = '*'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    r.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return r

# ── Routes ──────────────────────────────────────────────────────────────────
@app.route('/command', methods=['POST', 'OPTIONS'])
def receive_command():
    if request.method == 'OPTIONS':
        return cors(('', 204))
    
    data = request.get_json(silent=True)
    if data is None:
        print("[Bridge] Error: Received POST without valid JSON body.")
        data = {}
        
    cmd = data.get('command', '').strip()
    if cmd:
        print(f"[Bridge] Received command from HUD: {cmd}")
        command_queue.put(cmd)
    else:
        print("[Bridge] Warning: Received empty command.")
        
    return cors(jsonify(ok=True))

@app.route('/stream')
def stream():
    q = queue.Queue(maxsize=100)
    with _sub_lock:
        _subscribers.append(q)

    def generate():
        yield 'data: {"type":"connected"}\n\n'
        while True:
            try:
                payload = q.get(timeout=15)
                yield f'data: {payload}\n\n'
            except queue.Empty:
                yield ': ping\n\n'

    r = Response(generate(), mimetype='text/event-stream')
    r.headers['Cache-Control']       = 'no-cache'
    r.headers['X-Accel-Buffering']   = 'no'
    r.headers['Access-Control-Allow-Origin'] = '*'
    return r

@app.route('/status')
def status():
    return cors(jsonify(speaking=_is_speaking()))

def run_bridge():
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='127.0.0.1', port=7474, threaded=True, use_reloader=False)
