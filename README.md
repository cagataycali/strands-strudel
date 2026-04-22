# 🎵 strands-strudel

[![Awesome Strands Agents](https://img.shields.io/badge/Awesome-Strands%20Agents-00FF77?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjkwIiBoZWlnaHQ9IjQ2MyIgdmlld0JveD0iMCAwIDI5MCA0NjMiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik05Ny4yOTAyIDUyLjc4ODRDODUuMDY3NCA0OS4xNjY3IDcyLjIyMzQgNTYuMTM4OSA2OC42MDE3IDY4LjM2MTZDNjQuOTgwMSA4MC41ODQzIDcxLjk1MjQgOTMuNDI4MyA4NC4xNzQ5IDk3LjA1MDFMMjM1LjExNyAxMzkuNzc1QzI0NS4yMjMgMTQyLjc2OSAyNDYuMzU3IDE1Ni42MjggMjM2Ljg3NCAxNjEuMjI2TDMyLjU0NiAyNjAuMjkxQy0xNC45NDM5IDI4My4zMTYgLTkuMTYxMDcgMzUyLjc0IDQxLjQ4MzUgMzY3LjU5MUwxODkuNTUxIDQxMS4wMDlMMTkwLjEyNSA0MTEuMTY5QzIwMi4xODMgNDE0LjM3NiAyMTQuNjY1IDQwNy4zOTYgMjE4LjE5NiAzOTUuMzU1QzIyMS43ODQgMzgzLjEyMiAyMTQuNzc0IDM3MC4yOTYgMjAyLjU0MSAzNjYuNzA5TDU0LjQ3MzggMzIzLjI5MUM0NC4zNDQ3IDMyMC4zMjEgNDMuMTg3OSAzMDYuNDM2IDUyLjY4NTcgMzAxLjgzMUwyNTcuMDE0IDIwMi43NjZDMzA0LjQzMiAxNzkuNzc2IDI5OC43NTggMTEwLjQ4MyAyNDguMjMzIDk1LjUxMkw5Ny4yOTAyIDUyLjc4ODRaIiBmaWxsPSIjRkZGRkZGIi8+CjxwYXRoIGQ9Ik0yNTkuMTQ3IDAuOTgxODEyQzI3MS4zODkgLTIuNTc0OTggMjg0LjE5NyA0LjQ2NTcxIDI4Ny43NTQgMTYuNzA3NEMyOTEuMzExIDI4Ljk0OTIgMjg0LjI3IDQxLjc1NyAyNzIuMDI4IDQ1LjMxMzhMNzEuMTcyNyAxMDMuNjcxQzQwLjcxNDIgMTEyLjUyMSAzNy4xOTc2IDE1NC4yNjIgNjUuNzQ1OSAxNjguMDgzTDI0MS4zNDMgMjUzLjA5M0MzMDcuODcyIDI4NS4zMDIgMjk5Ljc5NCAzODIuNTQ2IDIyOC44NjIgNDAzLjMzNkwzMC40MDQxIDQ2MS41MDJDMTguMTcwNyA0NjUuMDg4IDUuMzQ3MDggNDU4LjA3OCAxLjc2MTUzIDQ0NS44NDRDLTEuODIzOSA0MzMuNjExIDUuMTg2MzcgNDIwLjc4NyAxNy40MTk3IDQxNy4yMDJMMjE1Ljg3OCAzNTkuMDM1QzI0Ni4yNzcgMzUwLjEyNSAyNDkuNzM5IDMwOC40NDkgMjIxLjIyNiAyOTQuNjQ1TDQ1LjYyOTcgMjA5LjYzNUMtMjAuOTgzNCAxNzcuMzg2IC0xMi43NzcyIDc5Ljk4OTMgNTguMjkyOCA1OS4zNDAyTDI1OS4xNDcgMC45ODE4MTJaIiBmaWxsPSIjRkZGRkZGIi8+Cjwvc3ZnPgo=&logoColor=white)](https://github.com/cagataycali/awesome-strands-agents)

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
