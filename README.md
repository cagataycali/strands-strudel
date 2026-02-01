# 🎵 strands-strudel

AI-powered live coding music generation with Strudel patterns.

A [Strands Agents](https://github.com/strands-agents/strands-agents) tool that generates and manipulates [Strudel](https://strudel.cc) patterns for algorithmic music composition.

## Installation

```bash
pip install strands-strudel
```

## Usage

### With Strands Agent

```python
from strands import Agent
from strands_strudel import strudel

agent = Agent(tools=[strudel])

# Generate a techno pattern
agent("Generate me a techno beat")

# Open pattern in browser
agent("Create an ambient soundscape and open it in strudel.cc")
```

### Direct Tool Usage

```python
from strands_strudel import strudel

# Generate by style
result = strudel(action="generate", style="techno")
print(result["code"])

# Open in browser
strudel(action="open", code='s("bd sd hh sd")', open_browser=True)

# Get syntax guide
result = strudel(action="guide")
print(result["content"][0]["text"])

# List available styles
result = strudel(action="examples")
```

## Available Styles

| Style | Description |
|-------|-------------|
| `techno` | Four-on-the-floor kick with TR-909 sounds |
| `ambient` | Atmospheric pads with reverb |
| `dnb` | Fast drum and bass patterns |
| `house` | Classic house groove |
| `acid` | 303-style acid basslines |
| `lofi` | Lo-fi hip hop beats |
| `breakbeat` | Chopped breakbeats |
| `minimal` | Sparse minimal techno |
| `jazz` | Jazz chord progressions |
| `generative` | Algorithmic/random patterns |
| `tetris` | The classic theme! |

## Actions

- **generate** - Create patterns by style or prompt
- **examples** - List available pattern styles
- **open** - Open code in strudel.cc browser
- **guide** - Show mini-notation syntax reference
- **explain** - Explain pattern syntax

## Mini-Notation Quick Reference

```
"a b c d"     - sequence (4 events per cycle)
"[a b] c"     - subdivide time
"a*4"         - multiply (speed up)
"a/4"         - divide (slow down)
"<a b c>"     - one per cycle
"~"           - rest/silence
"a,b,c"       - chord/polyphony
"a(3,8)"      - Euclidean rhythm
"a?"          - 50% chance
"a|b"         - random choice
```

## Links

- [Strudel REPL](https://strudel.cc) - Browser-based live coding
- [Strudel Docs](https://strudel.cc/workshop/getting-started/) - Full documentation
- [TidalCycles](https://tidalcycles.org) - The original Haskell version
- [Strands Agents](https://github.com/strands-agents/strands-agents) - AI agent framework

## License

MIT
