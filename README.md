# 🎵 strands-strudel

Live coding music with real-time WebSocket playback using [Strudel](https://strudel.cc) patterns.

A [Strands Agents](https://github.com/strands-agents/strands-agents) tool for algorithmic music composition with a beautiful mobile-friendly player UI.

## Features

- 🎧 **Real-time WebSocket streaming** - Send patterns to connected players instantly
- 📱 **Mobile-friendly player** - Glass morphism UI accessible from any device on your network
- 🎹 **13 preset styles** - Techno, ambient, DnB, house, acid, lofi, and more
- 📜 **Pattern history** - Timeline of all played patterns with one-click replay
- 🔌 **Multi-client support** - Broadcast to multiple players simultaneously

## Installation

```bash
pip install strands-strudel
```

## Quick Start

### With Strands Agent

```python
from strands import Agent
from strands_strudel import strudel

agent = Agent(tools=[strudel])

# Start the server and open player
agent("Start strudel and open the browser")

# Play a beat
agent("Play a techno beat")

# Create custom pattern
agent("Play s('bd*4') with some hi-hats")
```

### Direct Tool Usage

```python
from strands_strudel import strudel

# Start server and open player in browser
strudel(action="start", open_browser=True)

# Play by style
strudel(action="play", style="techno")

# Play custom code
strudel(action="play", code='s("bd sd hh sd")')

# Stop playback
strudel(action="hush")

# Check status
strudel(action="status")

# List available styles
strudel(action="styles")

# Stop server
strudel(action="stop")
```

## Actions

| Action | Description |
|--------|-------------|
| `start` | Start WebSocket + HTTP servers, optionally open browser |
| `play` | Send pattern code or preset style to connected players |
| `hush` | Stop all playback |
| `stop` | Stop servers |
| `status` | Show server status and connected players |
| `styles` | List available preset styles |

## Available Styles

| Style | Description |
|-------|-------------|
| `techno` | Four-on-the-floor kick with classic drums |
| `ambient` | Atmospheric pads with reverb and delay |
| `dnb` | Fast drum and bass patterns (140 BPM feel) |
| `house` | Classic house groove with bass |
| `acid` | 303-style acid basslines with filter sweeps |
| `lofi` | Lo-fi hip hop beats |
| `minimal` | Sparse minimal techno |
| `breakbeat` | Syncopated breakbeat patterns |
| `dub` | Dubby rhythms with heavy delay |
| `trance` | Uplifting trance with supersaw |
| `jungle` | Fast jungle/breakcore patterns |
| `chillout` | Relaxed downtempo vibes |
| `industrial` | Distorted industrial sounds |

## Architecture

```
┌─────────────────┐     WebSocket      ┌─────────────────┐
│  Strands Agent  │ ────────────────▶  │  Browser Player │
│                 │    Port 9999       │  (Strudel.js)   │
└─────────────────┘                    └─────────────────┘
                                              │
                          HTTP                │
                        Port 10000            ▼
                    ┌─────────────────────────────┐
                    │  Mobile / Other Browsers   │
                    │  http://<your-ip>:10000    │
                    └─────────────────────────────┘
```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `STRUDEL_WS_PORT` | `9999` | WebSocket server port |
| `STRUDEL_WS_HOST` | `0.0.0.0` | WebSocket bind address |

## Strudel Pattern Syntax

### Sound Sources

**Samples** (from dirt-samples):
```javascript
s("bd")           // bass drum
s("sd")           // snare drum
s("hh")           // hi-hat
s("cp")           // clap
s("808")          // 808 sounds
s("piano")        // piano
s("bd:0 bd:1")    // sample variations
```

**Synthesizers** (built-in):
```javascript
note("c4").sound("sine")       // sine wave
note("c4").sound("sawtooth")   // sawtooth wave
note("c4").sound("triangle")   // triangle wave
note("c4").sound("square")     // square wave
note("c4").sound("supersaw")   // detuned saws
```

### Mini-Notation

```javascript
"a b c d"       // sequence (4 equal parts)
"[a b] c"       // subdivide: a and b share one slot
"a*4"           // repeat 4 times
"a/2"           // play every 2 cycles
"~"             // rest/silence
"a?"            // 50% chance
"<a b c>"       // one per cycle
"a,b,c"         // play simultaneously (chord)
"a(3,8)"        // Euclidean: 3 hits over 8 steps
```

### Effects

```javascript
.lpf(1000)      // lowpass filter
.hpf(200)       // highpass filter
.gain(0.8)      // volume
.pan(0.5)       // stereo position
.room(0.5)      // reverb
.delay(0.5)     // delay amount
.distort(2)     // distortion
.speed(2)       // playback speed
```

### Example Patterns

**Basic Beat:**
```javascript
stack(
  s("bd*4"),
  s("~ sd ~ sd"),
  s("hh*8").gain(0.6)
)
```

**Melodic:**
```javascript
n("0 2 4 <5 7>")
  .scale("C:minor")
  .sound("sawtooth")
  .lpf(800)
```

**Ambient:**
```javascript
note("<[c3,e3,g3] [d3,f3,a3]>")
  .sound("triangle")
  .lpf(sine.range(400, 2000).slow(8))
  .room(0.8)
```

## Links

- [Strudel REPL](https://strudel.cc) - Browser-based live coding
- [Strudel Docs](https://strudel.cc/workshop/getting-started/) - Full documentation
- [TidalCycles](https://tidalcycles.org) - The original Haskell version
- [Strands Agents](https://github.com/strands-agents/sdk-python) - Strands Agents SDK

## License

MIT
