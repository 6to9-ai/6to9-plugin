---
type: llm
---

PASS if the final answer tells the user the working demo is outdated (or being refreshed), and either builds from the prompt's text / the current mock or offers to check back.
FAIL if it builds from the outdated demo as if it were current (e.g. five slots instead of the spec's three), or never mentions that the demo is outdated.
