"""
🎵 strudel - Live coding music with real-time WebSocket playback
"""

import json
import os
import asyncio
import threading
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional
from strands import tool

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

STRUDEL_WS_PORT = int(os.getenv("STRUDEL_WS_PORT", "9999"))
STRUDEL_WS_HOST = os.getenv("STRUDEL_WS_HOST", "0.0.0.0")  # Expose to network for mobile
TRACK_DIR = Path.home() / ".strands-strudel"

# ═══════════════════════════════════════════════════════════════
# WebSocket Server
# ═══════════════════════════════════════════════════════════════

_ws_server = None
_ws_clients = set()
_server_thread = None
_event_loop = None
_http_server = None
_http_thread = None


async def _handle_client(websocket):
    """Handle WebSocket client."""
    global _ws_clients
    _ws_clients.add(websocket)
    addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    print(f"🎵 Player connected: {addr}")
    
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get("type", "")
                if msg_type == "register":
                    print(f"🎵 Player ready: {data.get('client', 'unknown')}")
                elif msg_type == "ack":
                    print(f"🎵 Playing: {data.get('status', 'ok')}")
                elif msg_type == "error":
                    print(f"🎵 Error: {data.get('message', 'unknown')}")
            except json.JSONDecodeError:
                pass
    except:
        pass
    finally:
        _ws_clients.discard(websocket)
        print(f"🎵 Player disconnected: {addr}")


async def _run_server(port: int):
    """Run WebSocket server."""
    global _ws_server
    
    try:
        import websockets
    except ImportError:
        import subprocess
        subprocess.check_call(["pip", "install", "websockets", "-q"])
        import websockets
    
    _ws_server = await websockets.serve(_handle_client, STRUDEL_WS_HOST, port)
    print(f"🎵 WebSocket server: ws://{STRUDEL_WS_HOST}:{port}")
    await _ws_server.wait_closed()


def _start_server(port: int):
    """Start server in background thread."""
    global _event_loop, _server_thread
    
    def run():
        global _event_loop
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_event_loop)
        _event_loop.run_until_complete(_run_server(port))
    
    _server_thread = threading.Thread(target=run, daemon=True)
    _server_thread.start()


async def _broadcast(message: str):
    """Broadcast to all clients."""
    if _ws_clients:
        await asyncio.gather(
            *[c.send(message) for c in _ws_clients],
            return_exceptions=True
        )


def _send_to_players(code: str, action: str = "evaluate") -> int:
    """Send code to players."""
    global _event_loop
    
    if not _ws_clients or not _event_loop:
        return 0
    
    message = json.dumps({"type": action, "code": code})
    
    try:
        future = asyncio.run_coroutine_threadsafe(_broadcast(message), _event_loop)
        future.result(timeout=2)
        return len(_ws_clients)
    except:
        return 0


# ═══════════════════════════════════════════════════════════════
# HTTP Server for Mobile Access
# ═══════════════════════════════════════════════════════════════

_http_server = None
_http_thread = None


def _start_http_server(html_content: str, port: int):
    """Start a simple HTTP server to serve the player."""
    global _http_server, _http_thread
    
    from http.server import HTTPServer, BaseHTTPRequestHandler
    
    class PlayerHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(html_content.encode())
        
        def log_message(self, format, *args):
            pass  # Suppress logs
    
    def run():
        global _http_server
        _http_server = HTTPServer(('0.0.0.0', port), PlayerHandler)
        print(f"🌐 HTTP server: http://0.0.0.0:{port}")
        _http_server.serve_forever()
    
    _http_thread = threading.Thread(target=run, daemon=True)
    _http_thread.start()


# ═══════════════════════════════════════════════════════════════
# Pattern Templates
# ═══════════════════════════════════════════════════════════════

PATTERNS = {
    "techno": '''setcps(1)
stack(
  s("bd*4").gain(1.2),
  s("~ cp ~ cp").gain(0.9),
  s("hh*8").gain(0.5),
  s("~ ~ ~ oh").gain(0.4)
).room(0.15)''',

    "ambient": '''setcps(0.3)
stack(
  note("<[c4,e4,g4] [a3,c4,e4] [f3,a3,c4] [g3,b3,d4]>")
    .sound("triangle")
    .lpf(sine.range(600,3000).slow(16))
    .attack(0.5).release(2)
    .room(0.8).delay(0.4).delaytime(1/3),
  n("0 ~ 4 ~").scale("C:minor").sound("sine").octave(2).gain(0.3)
)''',

    "dnb": '''setcps(1.4)
stack(
  s("[bd ~ ~ bd] [~ ~ bd ~]").gain(1.1),
  s("~ sn:3 ~ sn:3").room(0.15),
  s("hh*16").gain(0.4).pan(sine.range(0.3,0.7)),
  s("~ ~ oh ~").gain(0.3)
)''',

    "house": '''setcps(1)
stack(
  s("bd*4").gain(1.1),
  s("~ cp ~ cp"),
  s("[~ hh]*4").gain(0.6),
  n("0 ~ 3 ~").scale("C:minor").sound("sawtooth").lpf(400).octave(2).gain(0.5)
).room(0.25)''',

    "acid": '''setcps(1.1)
stack(
  s("bd*4"),
  s("~ ~ cp ~"),
  note("[c2 c2 c2 <eb2 g2>](3,8)")
    .sound("sawtooth")
    .lpf(sine.range(200,3000).fast(2))
    .lpq(15).decay(0.1).sustain(0).gain(0.8)
)''',

    "lofi": '''setcps(0.7)
stack(
  s("bd ~ [~ bd] ~, ~ sd ~ sd").gain(0.9),
  note("<[e4,g4,b4] [d4,f#4,a4] [c4,e4,g4] [b3,d4,g4]>/2")
    .sound("triangle").lpf(2000).decay(0.3).room(0.4),
  s("hh*8?0.6").gain(0.3).pan(rand)
).lpf(4000)''',

    "minimal": '''setcps(1)
stack(
  s("bd*4"),
  s("hh(3,8)").gain(0.4),
  s("~ cp ~ ~").degradeBy(0.3),
  note("c2(5,16)").sound("sawtooth").lpf(300).gain(0.6)
)''',

    "breakbeat": '''setcps(1.2)
stack(
  s("[bd ~ bd ~] [~ ~ bd ~]").gain(1.1),
  s("~ sn ~ [~ sn]"),
  s("hh*8").gain(0.5).pan(sine),
  s("~ ~ oh ~").gain(0.35)
).room(0.2)''',

    "dub": '''setcps(0.8)
stack(
  s("bd ~ ~ bd:1, ~ ~ sn ~").room(0.3),
  note("[c2 ~ ~ c2] [~ ~ g1 ~]").sound("sawtooth").lpf(250).decay(0.2).gain(0.7),
  s("hh(3,8)").gain(0.35).delay(0.6).delaytime(1/3).delayfeedback(0.5)
).room(0.5)''',

    "trance": '''setcps(1.1)
stack(
  s("bd*4").gain(1.2),
  s("~ ~ cp ~"),
  s("hh*8").gain(0.4),
  note("<[c4,e4,g4] [a3,c4,e4] [f3,a3,c4] [g3,b3,d4]>")
    .sound("supersaw").detune(0.1).lpf(sine.range(500,4000).slow(8)).gain(0.5)
).room(0.3)''',

    "jungle": '''setcps(1.3)
stack(
  s("[bd ~ bd ~] [~ bd ~ bd]").gain(1.1),
  s("~ [sn sn] ~ sn").sometimes(x=>x.speed(1.5)),
  s("hh*16?0.8").gain(0.35),
  note("c2 ~ g1 ~").sound("sawtooth").lpf(200).gain(0.6)
).room(0.15)''',

    "chillout": '''setcps(0.5)
stack(
  s("bd ~ ~ bd, ~ ~ sd ~").gain(0.8),
  note("<[e3,g3,b3] [d3,f#3,a3] [c3,e3,g3] [b2,d3,f#3]>")
    .sound("triangle").attack(0.3).release(1.5).room(0.7),
  n("0 2 4 7").scale("E:minor:pentatonic").sound("sine").octave(4).gain(0.3).delay(0.5)
)''',

    "industrial": '''setcps(1)
stack(
  s("bd*4").distort(2).gain(1),
  s("~ sd:4 ~ sd:4").crush(6),
  s("hh*8").gain(0.4).coarse(8),
  note("c1*2").sound("sawtooth").lpf(150).distort(3).gain(0.5)
)''',
}


# ═══════════════════════════════════════════════════════════════
# Player HTML
# ═══════════════════════════════════════════════════════════════

def _get_player_html() -> str:
    """Generate player HTML with glass morphism and pattern timeline."""
    # Get local IP for mobile access
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        local_ip = "localhost"
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover, user-scalable=no">
  <title>🎵 Strudel DJ</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="theme-color" content="#000000">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎵</text></svg>">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #000;
      color: #fff;
      min-height: 100vh;
      min-height: 100dvh;
      overflow-x: hidden;
      -webkit-font-smoothing: antialiased;
      -webkit-tap-highlight-color: transparent;
    }}
    
    ::-webkit-scrollbar {{ width: 4px; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.15); border-radius: 2px; }}
    
    .app {{
      display: flex;
      flex-direction: column;
      min-height: 100vh;
      min-height: 100dvh;
      padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
    }}
    
    /* Header */
    .header {{
      padding: 16px 20px;
      background: rgba(255,255,255,0.03);
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border-bottom: 1px solid rgba(255,255,255,0.08);
      display: flex;
      align-items: center;
      gap: 12px;
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    
    .logo {{
      font-size: 24px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    
    .status {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-left: auto;
      font-size: 13px;
      font-weight: 600;
      color: rgba(255,255,255,0.6);
    }}
    
    .status-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: rgba(255,255,255,0.3);
      transition: all 0.3s;
    }}
    
    .status-dot.connected {{ background: #4ade80; box-shadow: 0 0 12px #4ade80; }}
    .status-dot.playing {{ background: #fbbf24; animation: pulse 1s infinite; box-shadow: 0 0 12px #fbbf24; }}
    
    @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
    
    /* Now Playing Card */
    .now-playing {{
      margin: 20px;
      padding: 24px;
      background: rgba(255,255,255,0.04);
      backdrop-filter: blur(30px);
      -webkit-backdrop-filter: blur(30px);
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 20px;
      transition: all 0.3s;
    }}
    
    .now-playing:hover {{
      background: rgba(255,255,255,0.06);
      border-color: rgba(255,255,255,0.15);
    }}
    
    .section-title {{
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: rgba(255,255,255,0.4);
      margin-bottom: 12px;
    }}
    
    .code-display {{
      background: rgba(0,0,0,0.4);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px;
      padding: 16px;
      font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
      font-size: 13px;
      line-height: 1.6;
      color: #fbbf24;
      max-height: 200px;
      overflow-y: auto;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    
    /* Controls */
    .controls {{
      display: flex;
      gap: 12px;
      padding: 0 20px;
      margin-bottom: 20px;
    }}
    
    .btn {{
      flex: 1;
      padding: 16px 24px;
      border-radius: 14px;
      border: 1px solid rgba(255,255,255,0.12);
      background: rgba(255,255,255,0.06);
      color: #fff;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
    }}
    
    .btn:hover {{ background: rgba(255,255,255,0.1); transform: translateY(-1px); }}
    .btn:active {{ transform: scale(0.98); }}
    .btn:disabled {{ opacity: 0.4; cursor: not-allowed; transform: none; }}
    
    .btn-primary {{
      background: #fff;
      color: #000;
      border-color: #fff;
    }}
    
    .btn-primary:hover {{ background: rgba(255,255,255,0.9); }}
    .btn-primary.active {{ background: #4ade80; border-color: #4ade80; }}
    
    /* Timeline */
    .timeline-section {{
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 0 20px 20px;
      overflow: hidden;
    }}
    
    .timeline-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }}
    
    .timeline-count {{
      font-size: 13px;
      color: rgba(255,255,255,0.4);
      font-weight: 500;
    }}
    
    .timeline {{
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding-bottom: 100px;
    }}
    
    .timeline-item {{
      padding: 16px;
      background: rgba(255,255,255,0.03);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid rgba(255,255,255,0.06);
      border-radius: 14px;
      cursor: pointer;
      transition: all 0.2s;
      position: relative;
    }}
    
    .timeline-item:hover {{
      background: rgba(255,255,255,0.06);
      border-color: rgba(255,255,255,0.12);
      transform: translateX(4px);
    }}
    
    .timeline-item.active {{
      background: rgba(251,191,36,0.1);
      border-color: rgba(251,191,36,0.3);
    }}
    
    .timeline-item.active::before {{
      content: '';
      position: absolute;
      left: 0;
      top: 50%;
      transform: translateY(-50%);
      width: 3px;
      height: 60%;
      background: #fbbf24;
      border-radius: 0 2px 2px 0;
    }}
    
    .timeline-time {{
      font-size: 11px;
      font-weight: 600;
      color: rgba(255,255,255,0.35);
      margin-bottom: 6px;
      font-family: 'SF Mono', monospace;
    }}
    
    .timeline-code {{
      font-family: 'SF Mono', 'Monaco', monospace;
      font-size: 12px;
      color: rgba(255,255,255,0.7);
      line-height: 1.5;
      max-height: 60px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: pre-wrap;
    }}
    
    .timeline-item:hover .timeline-code {{
      color: rgba(255,255,255,0.9);
    }}
    
    /* Mobile IP Banner */
    .mobile-banner {{
      margin: 0 20px 16px;
      padding: 14px 16px;
      background: rgba(74,222,128,0.1);
      border: 1px solid rgba(74,222,128,0.2);
      border-radius: 12px;
      font-size: 13px;
      color: rgba(255,255,255,0.8);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    
    .mobile-banner code {{
      background: rgba(0,0,0,0.3);
      padding: 4px 8px;
      border-radius: 6px;
      font-family: 'SF Mono', monospace;
      font-size: 12px;
      color: #4ade80;
    }}
    
    /* Empty State */
    .empty-state {{
      text-align: center;
      padding: 60px 20px;
      color: rgba(255,255,255,0.3);
    }}
    
    .empty-state-icon {{
      font-size: 48px;
      margin-bottom: 16px;
      opacity: 0.5;
    }}
    
    /* Loading overlay */
    .loading-overlay {{
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.8);
      backdrop-filter: blur(10px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      flex-direction: column;
      gap: 16px;
    }}
    
    .loading-overlay.active {{ display: flex; }}
    
    .spinner {{
      width: 40px;
      height: 40px;
      border: 3px solid rgba(255,255,255,0.1);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }}
    
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    
    .loading-text {{
      font-size: 14px;
      color: rgba(255,255,255,0.6);
    }}
  </style>
</head>
<body>
  <div class="app">
    <header class="header">
      <div class="logo">🎵 Strudel DJ</div>
      <div class="status">
        <div class="status-dot" id="statusDot"></div>
        <span id="statusText">Connecting...</span>
      </div>
    </header>
    
    <div class="mobile-banner">
      📱 Open on mobile:
      <code>http://{local_ip}:{STRUDEL_WS_PORT + 1}</code>
    </div>
    
    <div class="now-playing">
      <div class="section-title">Now Playing</div>
      <div class="code-display" id="currentCode">// Waiting for beats...
// Start audio below, then patterns will appear here</div>
    </div>
    
    <div class="controls">
      <button class="btn btn-primary" id="startBtn">▶ Start Audio</button>
      <button class="btn" id="stopBtn">⏹ Stop</button>
    </div>
    
    <div class="timeline-section">
      <div class="timeline-header">
        <div class="section-title">Pattern History</div>
        <div class="timeline-count" id="historyCount">0 patterns</div>
      </div>
      <div class="timeline" id="timeline">
        <div class="empty-state">
          <div class="empty-state-icon">🎹</div>
          <div>Patterns will appear here as DJ plays</div>
        </div>
      </div>
    </div>
  </div>
  
  <div class="loading-overlay" id="loadingOverlay">
    <div class="spinner"></div>
    <div class="loading-text" id="loadingText">Loading Strudel...</div>
  </div>

  <script type="module">
    const WS_URL = 'ws://' + window.location.hostname + ':{STRUDEL_WS_PORT}';
    let ws, ready = false, history = [], currentIndex = -1;
    
    const $ = id => document.getElementById(id);
    
    function setStatus(status) {{
      const dot = $('statusDot');
      const text = $('statusText');
      dot.className = 'status-dot' + (status === 'connected' ? ' connected' : status === 'playing' ? ' playing' : '');
      text.textContent = status === 'connected' ? 'Ready' : status === 'playing' ? 'Playing' : 'Disconnected';
    }}
    
    function showLoading(show, text) {{
      $('loadingOverlay').classList.toggle('active', show);
      if (text) $('loadingText').textContent = text;
    }}
    
    function formatTime(date) {{
      return date.toLocaleTimeString('en-US', {{ hour: '2-digit', minute: '2-digit', second: '2-digit' }});
    }}
    
    function addToHistory(code) {{
      const entry = {{ code, time: new Date(), id: Date.now() }};
      history.unshift(entry);
      currentIndex = 0;
      renderTimeline();
      $('currentCode').textContent = code;
      $('historyCount').textContent = history.length + ' pattern' + (history.length !== 1 ? 's' : '');
    }}
    
    function renderTimeline() {{
      const timeline = $('timeline');
      if (history.length === 0) {{
        timeline.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🎹</div><div>Patterns will appear here as DJ plays</div></div>';
        return;
      }}
      
      timeline.innerHTML = history.map((entry, i) => `
        <div class="timeline-item ${{i === currentIndex ? 'active' : ''}}" data-index="${{i}}">
          <div class="timeline-time">${{formatTime(entry.time)}}</div>
          <div class="timeline-code">${{entry.code.substring(0, 200)}}${{entry.code.length > 200 ? '...' : ''}}</div>
        </div>
      `).join('');
      
      // Add click handlers
      timeline.querySelectorAll('.timeline-item').forEach(item => {{
        item.addEventListener('click', () => {{
          const idx = parseInt(item.dataset.index);
          playFromHistory(idx);
        }});
      }});
    }}
    
    async function playFromHistory(index) {{
      if (!ready || index < 0 || index >= history.length) return;
      
      currentIndex = index;
      const code = history[index].code;
      $('currentCode').textContent = code;
      renderTimeline();
      
      try {{
        await window.evaluate(code);
        setStatus('playing');
      }} catch (e) {{
        console.error('Playback error:', e);
      }}
    }}
    
    async function play(code) {{
      addToHistory(code);
      
      if (!ready) {{
        console.log('Audio not ready');
        return;
      }}
      
      try {{
        await window.evaluate(code);
        setStatus('playing');
        if (ws?.readyState === 1) ws.send(JSON.stringify({{type:'ack',status:'playing'}}));
      }} catch (e) {{
        console.error('Eval error:', e);
        if (ws?.readyState === 1) ws.send(JSON.stringify({{type:'error',message:e.message}}));
      }}
    }}
    
    // Initialize audio
    $('startBtn').onclick = async () => {{
      if (ready) return;
      
      const btn = $('startBtn');
      btn.disabled = true;
      showLoading(true, 'Loading Strudel engine...');
      
      try {{
        const {{ initStrudel, evaluate: ev, hush: hu }} = await import('https://unpkg.com/@strudel/web@1.3.0/dist/index.mjs');
        
        window.evaluate = ev;
        window.hush = hu;
        
        showLoading(true, 'Loading samples...');
        
        await initStrudel({{
          prebake: async () => {{
            const {{ samples }} = await import('https://unpkg.com/@strudel/web@1.3.0/dist/index.mjs');
            await samples('github:tidalcycles/dirt-samples');
          }}
        }});
        
        ready = true;
        btn.textContent = '✓ Ready';
        btn.classList.add('active');
        setStatus('connected');
        showLoading(false);
        
        // Play pending if any
        if (history.length > 0) {{
          playFromHistory(0);
        }}
      }} catch (e) {{
        console.error('Init error:', e);
        btn.disabled = false;
        btn.textContent = '▶ Retry';
        showLoading(false);
      }}
    }};
    
    $('stopBtn').onclick = () => {{
      if (window.hush) {{
        window.hush();
        setStatus('connected');
      }}
    }};
    
    // WebSocket connection
    function connect() {{
      console.log('Connecting to', WS_URL);
      ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {{
        setStatus(ready ? 'connected' : 'connected');
        ws.send(JSON.stringify({{type:'register',client:'strudel-player-v2'}}));
      }};
      
      ws.onmessage = async e => {{
        try {{
          const d = JSON.parse(e.data);
          if (d.type === 'evaluate' || d.type === 'play') {{
            await play(d.code);
          }} else if (d.type === 'hush' || d.type === 'stop') {{
            if (window.hush) window.hush();
            setStatus('connected');
          }}
        }} catch {{
          if (e.data.trim()) await play(e.data);
        }}
      }};
      
      ws.onclose = () => {{
        setStatus('');
        setTimeout(connect, 2000);
      }};
      
      ws.onerror = () => console.log('WebSocket error');
    }}
    
    connect();
  </script>
</body>
</html>'''


# ═══════════════════════════════════════════════════════════════
# Tool
# ═══════════════════════════════════════════════════════════════

@tool
def strudel(
    action: str,
    code: Optional[str] = None,
    style: Optional[str] = None,
    open_browser: bool = False,
) -> Dict[str, Any]:
    """
    🎵 Live coding music with Strudel patterns - a JavaScript port of TidalCycles.

    Args:
        action: Action to perform:
            - "start": Start server and open player
            - "play": Send pattern to player  
            - "hush": Stop playback
            - "stop": Stop server
            - "status": Show server status
            - "styles": List available styles
        code: Strudel pattern code to play (see syntax below)
        style: Use preset style (techno, ambient, dnb, house, acid, lofi, minimal, breakbeat, dub)
        open_browser: Auto-open player in browser

    ═══════════════════════════════════════════════════════════════════════════════
    STRUDEL PATTERN SYNTAX GUIDE
    ═══════════════════════════════════════════════════════════════════════════════

    ─────────────────────────────────────────────────────────────────────────────
    SOUND SOURCES
    ─────────────────────────────────────────────────────────────────────────────
    
    SAMPLES (from dirt-samples):
      s("bd")           - bass drum
      s("sd")           - snare drum  
      s("hh")           - hi-hat
      s("oh")           - open hi-hat
      s("cp")           - clap
      s("sn")           - snare variants
      s("mt lt ht")     - mid/low/high tom
      s("ride")         - ride cymbal
      s("crash")        - crash cymbal
      s("808")          - 808 sounds
      s("piano")        - piano
      s("bass")         - bass sounds
      s("arpy")         - arpeggio sounds
      s("jvbass")       - JV bass
      s("casio")        - casio sounds
      s("space")        - space sounds
      s("numbers")      - spoken numbers
      
    Sample variations: s("bd:0 bd:1 bd:2")  // different samples in bank
    
    SYNTHESIZERS (built-in, no loading needed):
      .sound("sine")       - sine wave
      .sound("triangle")   - triangle wave
      .sound("sawtooth")   - sawtooth wave  
      .sound("square")     - square wave
      .sound("pulse")      - pulse wave (use .pw() for width)
      .sound("supersaw")   - detuned saws (use .unison(), .detune())
      .sound("supersquare")- detuned squares
      .sound("white")      - white noise
      .sound("pink")       - pink noise
      .sound("brown")      - brown noise
      .sound("crackle")    - crackle noise
      
    NOTES & FREQUENCIES:
      note("c4 d4 e4 g4")           - note names (c0-c9, with # or b)
      note("60 62 64 67")           - MIDI numbers
      n("0 2 4 7").scale("C:minor") - scale degrees
      freq("440 880")               - frequencies in Hz
      
    ─────────────────────────────────────────────────────────────────────────────
    MINI-NOTATION (Pattern Syntax)
    ─────────────────────────────────────────────────────────────────────────────
    
    BASIC:
      "a b c d"          - sequence (4 equal parts per cycle)
      "a b [c d]"        - subdivision: c and d share one slot
      "a b [c d e]"      - 3 in one slot
      "a*4"              - repeat 4 times
      "a!4"              - replicate 4 times (different from *)
      "a/2"              - play every 2 cycles
      "a b ~ d"          - rest/silence
      "a b?"             - 50% chance of playing
      "a b?0.3"          - 30% chance
      
    ALTERNATION:
      "<a b c>"          - one per cycle: a, then b, then c
      "<a b c>/2"        - change every 2 cycles
      
    STACKING:
      "a,b,c"            - play simultaneously (chord)
      "[a,b] [c,d]"      - chords in sequence
      
    ELONGATION:
      "a@3 b"            - a takes 3/4 of cycle, b takes 1/4
      "a@2 b@2 c"        - 2:2:1 ratio
      
    EUCLIDEAN:
      "a(3,8)"           - 3 hits spread over 8 steps
      "a(5,8,2)"         - with rotation
      
    ─────────────────────────────────────────────────────────────────────────────
    EFFECTS & MODIFIERS
    ─────────────────────────────────────────────────────────────────────────────
    
    FILTERS:
      .lpf(1000)         - lowpass filter (cutoff Hz)
      .hpf(200)          - highpass filter  
      .bpf(500)          - bandpass filter
      .lpq(10)           - filter resonance (0-50)
      .lpenv(4)          - filter envelope depth
      .cutoff(sine.range(200,2000).slow(4))  - modulated filter
      
    AMPLITUDE:
      .gain(0.8)         - volume (0-1+)
      .velocity(0.7)     - velocity (multiplies with gain)
      .amp(0.5)          - linear amplitude
      
    ENVELOPE (ADSR):
      .attack(0.1)       - attack time (seconds)
      .decay(0.2)        - decay time
      .sustain(0.5)      - sustain level (0-1)
      .release(0.3)      - release time
      .adsr(".1:.2:.5:.3") - all at once
      
    SPATIAL:
      .pan(0.5)          - stereo position (0=left, 1=right)
      .room(0.5)         - reverb amount
      .roomsize(2)       - reverb size
      .delay(0.5)        - delay amount
      .delaytime(0.25)   - delay time (cycles)
      .delayfeedback(0.5)- delay feedback
      
    PITCH:
      .speed(2)          - playback speed (affects pitch)
      .transpose(7)      - transpose semitones
      .octave(4)         - set octave
      .detune(0.1)       - detune amount
      .vibrato(4)        - vibrato speed Hz
      
    DISTORTION & SATURATION:
      .distort(2)        - waveshaper distortion
      .shape(0.5)        - soft saturation
      .crush(8)          - bit crusher (bits)
      .coarse(4)         - sample rate reduction
      
    ─────────────────────────────────────────────────────────────────────────────
    PATTERN TRANSFORMATIONS
    ─────────────────────────────────────────────────────────────────────────────
    
    TIME:
      .fast(2)           - speed up 2x
      .slow(2)           - slow down 2x
      .hurry(2)          - fast + speed (pitch shift)
      
    STRUCTURE:
      .rev()             - reverse pattern
      .palindrome()      - forward then backward
      .iter(4)           - rotate through divisions
      .chunk(4, f)       - apply f to 1/4 each cycle
      .every(4, f)       - apply f every 4 cycles
      
    RANDOMNESS:
      .degrade()         - randomly drop 50% events
      .degradeBy(0.3)    - drop 30%
      .shuffle(4)        - shuffle 4 parts
      .scramble(4)       - scramble (with repeats)
      .sometimes(f)      - 50% chance to apply f
      .often(f)          - 75% chance
      .rarely(f)         - 25% chance
      
    LAYERING:
      .stack(pat2)       - play together
      .superimpose(f)    - layer with transformation
      .jux(rev)          - stereo split with function
      .off(1/8, f)       - offset layer
      .echo(3, 1/8, 0.5) - echo effect
      
    ─────────────────────────────────────────────────────────────────────────────
    SCALES & CHORDS  
    ─────────────────────────────────────────────────────────────────────────────
    
    SCALES (use with n() and .scale()):
      "C:major", "C:minor", "C:dorian", "C:phrygian", "C:lydian",
      "C:mixolydian", "C:locrian", "C:pentatonic", "C:minor:pentatonic",
      "C:blues", "C:chromatic", "C:whole", "C:diminished", "C:bebop"
      
    Example: n("0 2 4 5 7").scale("D:minor")
    
    CHORDS:
      chord("<C Am F G>").voicing()  - chord progressions with voicing
      note("[c3,e3,g3]")             - manual chord
      
    ─────────────────────────────────────────────────────────────────────────────
    CONTINUOUS SIGNALS (for modulation)
    ─────────────────────────────────────────────────────────────────────────────
    
      sine              - 0 to 1 sine wave
      cosine            - 0 to 1 cosine  
      saw               - 0 to 1 sawtooth
      tri               - 0 to 1 triangle
      square            - 0 to 1 square
      rand              - random 0-1
      perlin            - smooth random (perlin noise)
      
    MODIFIERS:
      sine.range(200, 2000)     - scale to range
      sine.slow(4)              - 4x slower
      sine.fast(2)              - 2x faster
      sine.segment(8)           - sample 8 times per cycle
      
    Example: .lpf(sine.range(200, 4000).slow(8))
    
    ─────────────────────────────────────────────────────────────────────────────
    COMPLETE EXAMPLES
    ─────────────────────────────────────────────────────────────────────────────
    
    BASIC BEAT:
      stack(
        s("bd*4"),
        s("~ sd ~ sd"),
        s("hh*8").gain(0.6)
      )
    
    MELODIC:
      n("0 2 4 <5 7>")
        .scale("C:minor")
        .sound("sawtooth")
        .lpf(800)
        .attack(0.01)
        .release(0.2)
    
    AMBIENT:
      note("<[c3,e3,g3] [d3,f3,a3]>")
        .sound("triangle")
        .lpf(sine.range(400, 2000).slow(8))
        .room(0.8)
        .delay(0.4)
    
    COMPLEX RHYTHM:
      stack(
        s("bd(3,8)").gain(1.2),
        s("sd:2(2,8,3)"),
        s("hh*8?0.7").gain(0.5),
        n("0 3 <5 7>(3,8)").scale("C:minor").sound("bass").lpf(400)
      ).room(0.2)
    
    GENERATIVE:
      n(irand(8).segment(16))
        .scale("D:minor:pentatonic")
        .sound("piano")
        .room(0.4)
        .delay(0.3)
        .delaytime(1/6)
    
    ═══════════════════════════════════════════════════════════════════════════════

    Basic Examples:
        strudel(action="start", open_browser=True)
        strudel(action="play", code='s("bd sd hh sd")')
        strudel(action="play", style="techno")
        strudel(action="hush")
    """
    global _ws_server, _http_server, _http_thread
    
    try:
        # START
        if action == "start":
            if _ws_server:
                return {"status": "success", "content": [{"text": f"🎵 Already running on ws://0.0.0.0:{STRUDEL_WS_PORT}\nPlayers: {len(_ws_clients)}"}]}
            
            _start_server(STRUDEL_WS_PORT)
            
            import time
            time.sleep(0.3)
            
            TRACK_DIR.mkdir(parents=True, exist_ok=True)
            player = TRACK_DIR / "player.html"
            html_content = _get_player_html()
            player.write_text(html_content)
            
            # Start HTTP server for mobile access
            http_port = STRUDEL_WS_PORT + 1
            if not _http_server:
                from http.server import HTTPServer, BaseHTTPRequestHandler
                
                class PlayerHandler(BaseHTTPRequestHandler):
                    def do_GET(self):
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(html_content.encode())
                    
                    def log_message(self, format, *args):
                        pass
                
                def run_http():
                    global _http_server
                    _http_server = HTTPServer(('0.0.0.0', http_port), PlayerHandler)
                    _http_server.serve_forever()
                
                _http_thread = threading.Thread(target=run_http, daemon=True)
                _http_thread.start()
            
            # Get local IP for mobile
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "localhost"
            
            if open_browser:
                webbrowser.open(f"http://localhost:{http_port}")
            
            return {
                "status": "success",
                "content": [{
                    "text": f"🎵 Server started!\n\n"
                           + f"📱 Mobile: http://{local_ip}:{http_port}\n"
                           + f"💻 Local: http://localhost:{http_port}\n"
                           + f"🔌 WebSocket: ws://0.0.0.0:{STRUDEL_WS_PORT}\n\n"
                           + ("✅ Opened in browser\n\n" if open_browser else "")
                           + "Now use: strudel(action='play', code='s(\"bd sd\")')"
                }]
            }
        
        # PLAY
        elif action == "play":
            if not code and not style:
                return {"status": "error", "content": [{"text": "Provide 'code' or 'style'"}]}
            
            if style:
                if style.lower() not in PATTERNS:
                    return {"status": "error", "content": [{"text": f"Unknown style. Available: {', '.join(PATTERNS.keys())}"}]}
                code = PATTERNS[style.lower()]
            
            # Auto-start if needed
            if not _ws_server:
                _start_server(STRUDEL_WS_PORT)
                import time
                time.sleep(0.3)
            
            n = _send_to_players(code, "evaluate")
            
            if n > 0:
                return {"status": "success", "content": [{"text": f"🎵 Playing on {n} player(s)\n\n```js\n{code}\n```"}]}
            else:
                TRACK_DIR.mkdir(parents=True, exist_ok=True)
                player = TRACK_DIR / "player.html"
                player.write_text(_get_player_html())
                return {"status": "success", "content": [{"text": f"🎵 No players connected!\n\nOpen: file://{player}\n\n```js\n{code}\n```"}]}
        
        # HUSH
        elif action == "hush":
            n = _send_to_players("", "hush")
            return {"status": "success", "content": [{"text": f"🔇 Stopped {n} player(s)"}]}
        
        # STOP
        elif action == "stop":
            if _ws_server:
                _send_to_players("", "hush")
                _event_loop.call_soon_threadsafe(_ws_server.close)
                _ws_server = None
            # Stop HTTP server too
            if _http_server:
                _http_server.shutdown()
                _http_server = None
            return {"status": "success", "content": [{"text": "🎵 Server stopped"}]}
        
        # STATUS
        elif action == "status":
            # Get local IP for mobile
            import socket
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                s.close()
            except:
                local_ip = "localhost"
            
            http_port = STRUDEL_WS_PORT + 1
            return {
                "status": "success",
                "content": [{
                    "text": f"🎵 Status\n\n"
                           f"Server: {'Running' if _ws_server else 'Stopped'}\n"
                           f"📱 Mobile: http://{local_ip}:{http_port}\n"
                           f"💻 Local: http://localhost:{http_port}\n"
                           f"🔌 WebSocket: ws://0.0.0.0:{STRUDEL_WS_PORT}\n"
                           f"Players: {len(_ws_clients)}"
                }]
            }
        
        # STYLES
        elif action == "styles":
            txt = "🎵 Available styles:\n\n"
            for name in PATTERNS:
                txt += f"  • {name}\n"
            txt += "\nUse: strudel(action='play', style='techno')"
            return {"status": "success", "content": [{"text": txt}]}
        
        else:
            return {"status": "error", "content": [{"text": f"Unknown action: {action}\n\nValid: start, play, hush, stop, status, styles"}]}
    
    except Exception as e:
        return {"status": "error", "content": [{"text": f"Error: {e}"}]}
