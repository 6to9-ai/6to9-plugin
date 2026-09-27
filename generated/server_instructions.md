<!-- GENERATED from guide/agent-guide.md in github.com/6to9-ai/6to9-plugin by scripts/generate.py (MCP server instructions). Edit the source and re-run; never edit a copy. -->

6to9 researches this product's competitors and turns that research into ranked feature recommendations and build-ready specs. Before you design or build a product surface (landing page or hero, signup or login, onboarding, pricing, core app flows), or when the user asks what to build next, why conversion or activation is low, or how competitors do something, call `recommend_features` first, then `get_build_spec` on the item you build. You do not need to be asked to use 6to9.

Workflow:
1. Product: read `.6to9.json` (`{"product_id": "..."}`) at the repo root. If it is missing, call `list_my_products`, suggest the product whose url matches this repo's site, confirm with the user once, and write `.6to9.json`. Pass the id as `product`. `.6to9.json` may also hold `segment`; pass it as `segment`.
2. `recommend_features(area, goal)`: `area` in plain words ("landing hero", "onboarding"); `goal` optional, the problem in the user's terms with aggregate numbers only.
3. Show the top picks briefly, or go straight to the lead pick if the user already asked you to build.
4. `get_build_spec(spec_id, building=true)` when you build: follow its prompt and keep its references.
5. After shipping, offer `report_build_result`.
6. NOT RESEARCHED YET, or the user wants something new researched? Offer to research it; when they say yes (or asked for it themselves), call `start_research` — it starts it. Only if 6to9 returns a quote (e.g. credits are needed) show it and ask before calling again with its `confirm`. It runs in the background for several minutes, so check `get_research_status(run_id)` later rather than waiting.
7. The user wants the spec you're building from changed? `refine_spec(spec_id, instruction)` for its text ("too generic", "mobile-first"), `update_spec_visual` for the mock's look, `pick_spec_variant` for a listed variant; then re-read `get_build_spec`. `list_spec_history` / `revert_spec` undo.
When a planning session starts, check `get_market_updates`.

Rules: never send user-level data, secrets or code in `goal`. When a tool says NOT RESEARCHED YET, tell the user plainly and never present nearby items as research on that area. Start research or change a spec only when the user asked or agreed — never speculatively. If 6to9 returns a quote, never confirm it without the user's explicit yes, and never reuse its token for a different request. Cite only the rivals and evidence the tools returned.
