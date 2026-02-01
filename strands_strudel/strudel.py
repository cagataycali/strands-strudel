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
TRACK_DIR = Path.cwd() / ".strands-strudel"

# ═══════════════════════════════════════════════════════════════
# WebSocket Server
# ═══════════════════════════════════════════════════════════════

_ws_server = None
_ws_clients = set()
_server_thread = None
_event_loop = None


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
    
    _ws_server = await websockets.serve(_handle_client, "127.0.0.1", port)
    print(f"🎵 WebSocket server: ws://127.0.0.1:{port}")
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
    """Generate player HTML."""
    return f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>🎵 Strudel Player</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'JetBrains Mono', monospace;
      background: linear-gradient(135deg, #1a1a2e, #0f3460);
      color: #e94560;
      min-height: 100vh;
      padding: 20px;
    }}
    h1 {{ margin-bottom: 20px; }}
    .status {{ display: flex; align-items: center; gap: 10px; margin-bottom: 20px; }}
    .dot {{
      width: 12px; height: 12px;
      border-radius: 50%;
      background: #ff6b6b;
    }}
    .dot.ok {{ background: #51cf66; }}
    .dot.play {{ background: #ffd43b; animation: pulse 0.5s infinite; }}
    @keyframes pulse {{ 50% {{ opacity: 0.5; }} }}
    pre {{
      background: rgba(0,0,0,0.4);
      padding: 20px;
      border-radius: 12px;
      color: #ffd43b;
      margin-bottom: 20px;
      min-height: 200px;
      overflow: auto;
      white-space: pre-wrap;
    }}
    button {{
      padding: 12px 24px;
      border: 2px solid #e94560;
      background: transparent;
      color: #e94560;
      font-family: inherit;
      border-radius: 8px;
      cursor: pointer;
      margin-right: 10px;
      margin-bottom: 10px;
    }}
    button:hover, button.active {{ background: #e94560; color: #1a1a2e; }}
    button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
    .log {{
      margin-top: 20px;
      background: rgba(0,0,0,0.3);
      padding: 10px;
      border-radius: 8px;
      font-size: 12px;
      color: #888;
      max-height: 150px;
      overflow-y: auto;
    }}
    .loading {{ color: #ffd43b; }}
  </style>
</head>
<body>
  <h1>🎵 Strudel Player</h1>
  <div class="status">
    <div class="dot" id="dot"></div>
    <span id="status">Connecting...</span>
  </div>
  <pre id="code">// Waiting for patterns...
// Click "Start Audio" first, then send patterns from Python:
//   strudel(action="play", code='s("bd sd hh sd")')
//   strudel(action="play", style="techno")</pre>
  <div>
    <button id="start">▶ Start Audio</button>
    <button id="stop">⏹ Stop</button>
  </div>
  <div class="log" id="log"></div>

  <script type="module">
    const WS = 'ws://127.0.0.1:{STRUDEL_WS_PORT}';
    let ws, ready = false, pending = '';
    
    const $ = id => document.getElementById(id);
    const log = (m, ok) => {{
      const d = document.createElement('div');
      d.className = ok === 'loading' ? 'loading' : '';
      d.style.color = ok === true ? '#51cf66' : ok === false ? '#ff6b6b' : ok === 'loading' ? '#ffd43b' : '#888';
      d.textContent = `[${{new Date().toLocaleTimeString()}}] ${{m}}`;
      $('log').appendChild(d);
      $('log').scrollTop = 9999;
    }};
    
    const setStatus = s => {{
      $('dot').className = 'dot' + (s === 'ok' ? ' ok' : s === 'play' ? ' play' : '');
      $('status').textContent = s === 'ok' ? 'Connected' : s === 'play' ? 'Playing' : 'Disconnected';
    }};
    
    // Initialize audio on user click
    $('start').onclick = async () => {{
      if (ready) return;
      $('start').disabled = true;
      $('start').textContent = '⏳ Loading...';
      
      try {{
        log('Loading Strudel from CDN...', 'loading');
        const {{ initStrudel, evaluate: ev, hush: hu }} = await import('https://unpkg.com/@strudel/web@1.3.0/dist/index.mjs');
        
        window.evaluate = ev;
        window.hush = hu;
        
        log('Loading samples (dirt-samples)...', 'loading');
        
        // Initialize with samples prebake
        await initStrudel({{
          prebake: async () => {{
            const {{ samples }} = await import('https://unpkg.com/@strudel/web@1.3.0/dist/index.mjs');
            await samples('github:tidalcycles/dirt-samples');
          }}
        }});
        
        ready = true;
        $('start').textContent = '✓ Ready';
        $('start').classList.add('active');
        log('Audio engine ready! Samples loaded.', true);
        
        // Play pending code if any
        if (pending) {{
          log('Playing pending pattern...', 'loading');
          play(pending);
        }}
      }} catch (e) {{
        log('Init error: ' + e.message, false);
        console.error(e);
        $('start').disabled = false;
        $('start').textContent = '▶ Retry';
      }}
    }};
    
    $('stop').onclick = () => {{
      if (window.hush) {{
        window.hush();
        setStatus('ok');
        log('Stopped playback');
      }}
    }};
    
    async function play(code) {{
      pending = code;
      $('code').textContent = code;
      
      if (!ready) {{
        log('Audio not started - click "Start Audio" first', false);
        return;
      }}
      
      try {{
        log('Evaluating pattern...', 'loading');
        await window.evaluate(code);
        setStatus('play');
        log('Now playing!', true);
        if (ws?.readyState === 1) ws.send(JSON.stringify({{type:'ack',status:'playing'}}));
      }} catch (e) {{
        log('Pattern error: ' + e.message, false);
        console.error('Eval error:', e);
        if (ws?.readyState === 1) ws.send(JSON.stringify({{type:'error',message:e.message}}));
      }}
    }}
    
    function connect() {{
      log('Connecting to ' + WS);
      ws = new WebSocket(WS);
      
      ws.onopen = () => {{
        setStatus('ok');
        log('Connected to Python server!', true);
        ws.send(JSON.stringify({{type:'register',client:'strudel-player'}}));
      }};
      
      ws.onmessage = async e => {{
        try {{
          const d = JSON.parse(e.data);
          if (d.type === 'evaluate' || d.type === 'play') {{
            log('Received pattern from Python');
            await play(d.code);
          }} else if (d.type === 'hush' || d.type === 'stop') {{
            if (window.hush) window.hush();
            setStatus('ok');
            log('Stopped by Python');
          }}
        }} catch {{
          // Raw code string
          if (e.data.trim()) {{
            log('Received raw pattern');
            await play(e.data);
          }}
        }}
      }};
      
      ws.onclose = () => {{
        setStatus('');
        log('Disconnected from server');
        setTimeout(connect, 2000);
      }};
      
      ws.onerror = () => log('WebSocket error', false);
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
    global _ws_server
    
    try:
        # START
        if action == "start":
            if _ws_server:
                return {"status": "success", "content": [{"text": f"🎵 Already running on ws://127.0.0.1:{STRUDEL_WS_PORT}\nPlayers: {len(_ws_clients)}"}]}
            
            _start_server(STRUDEL_WS_PORT)
            
            import time
            time.sleep(0.3)
            
            TRACK_DIR.mkdir(parents=True, exist_ok=True)
            player = TRACK_DIR / "player.html"
            player.write_text(_get_player_html())
            
            if open_browser:
                webbrowser.open(f"file://{player}")
            
            return {
                "status": "success",
                "content": [{
                    "text": f"🎵 Server started!\n\nws://127.0.0.1:{STRUDEL_WS_PORT}\nPlayer: {player}\n\n"
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
            return {"status": "success", "content": [{"text": "🎵 Server stopped"}]}
        
        # STATUS
        elif action == "status":
            return {
                "status": "success",
                "content": [{
                    "text": f"🎵 Status\n\nServer: {'Running' if _ws_server else 'Stopped'}\n"
                           f"Port: {STRUDEL_WS_PORT}\nPlayers: {len(_ws_clients)}"
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
