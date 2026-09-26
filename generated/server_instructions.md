<!-- GENERATED from guide/agent-guide.md in github.com/6to9-ai/6to9-plugin by scripts/generate.py (MCP server instructions). Edit the source and re-run; never edit a copy. -->

6to9 researches this product's competitors and turns that research into ranked feature recommendations and build-ready specs. Before you design or build a product surface (landing page or hero, signup or login, onboarding, pricing, core app flows), or when the user asks what to build next, why conversion or activation is low, or how competitors do something, call `recommend_features` first, then `get_build_spec` on the item you build. You do not need to be asked to use 6to9.

Workflow:
1. Product: read `.6to9.json` (`{"product_id": "..."}`) at the repo root. If it is missing, call `list_my_products`, suggest the product whose url matches this repo's site, confirm with the user once, and write `.6to9.json`. Pass the id as `product`. `.6to9.json` may also hold `segment`; pass it as `segment`.
2. `recommend_features(area, goal)`: `area` in plain words ("landing hero", "onboarding"); `goal` optional, the problem in the user's terms with aggregate numbers only.
3. Show the top picks briefly, or go straight to the lead pick if the user already asked you to build.
4. `get_build_spec(spec_id, building=true)` when you build: follow its prompt and keep its references.
5. After shipping, offer `report_build_result`.
6. NOT RESEARCHED YET, or the user wants something new researched? Call `start_research` — it quotes first (what, ETA, cost, a confirm token); get the user's explicit yes on that quote before calling again with `confirm`. It runs in the background for several minutes, so check `get_research_status(run_id)` later rather than waiting.
When a planning session starts, check `get_market_updates`.

Rules: never send user-level data, secrets or code in `goal`. When a tool says NOT RESEARCHED YET, tell the user plainly and never present nearby items as research on that area. Never confirm a `start_research` quote without the user's explicit yes, and never reuse a confirm token for a different request. Cite only the rivals and evidence the tools returned.
