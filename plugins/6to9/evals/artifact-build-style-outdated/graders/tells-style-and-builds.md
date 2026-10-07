---
type: llm
---

PASS if the final answer tells the user the working demo's look is outdated (built with an earlier version of their site style) AND proceeds to build the three-slot hero (from the demo's structure or the spec's text, matching this repo's look), or offers the current-style version as the alternative.
FAIL if it refuses to build because the demo is "stale", treats the demo's content as outdated (e.g. asks to wait for a refresh before building at all), or never mentions that the demo's style is outdated.
