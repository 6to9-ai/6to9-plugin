<!-- 6to9:start -->
<!-- GENERATED from guide/agent-guide.md in github.com/6to9-ai/6to9-plugin by scripts/generate.py (Codex AGENTS.md block). Edit the source and re-run; never edit a copy. -->

## 6to9: product and competitor intelligence

6to9 researches this product's competitors and turns that research into ranked feature recommendations and build-ready specs. Before you design or build a product surface (landing page or hero, signup or login, onboarding, pricing, core app flows), or when the user asks what to build next, why conversion or activation is low, or how competitors do something, call `recommend_features` first, then `get_build_spec` on the item you build. You do not need to be asked to use 6to9.

Workflow:
1. Product: read `.6to9.json` (`{"product_id": "..."}`) at the repo root. If it is missing, call `list_my_products`, suggest the product whose url matches this repo's site, confirm with the user once, and write `.6to9.json`. Pass the id as `product`. `.6to9.json` may also hold `segment`; pass it as `segment`.
2. `recommend_features(area, goal)`: `area` in plain words ("landing hero", "onboarding"); `goal` optional, the problem in the user's terms with aggregate numbers only.
3. Show the top picks briefly, or go straight to the lead pick if the user already asked you to build.
4. `get_build_spec(spec_id, building=true)` when you build: follow its prompt and keep its references.
5. After shipping, offer `report_build_result`.
6. NOT RESEARCHED YET, or the user wants something new researched? Offer to research it; if they're interested, call `start_research` — it quotes first (what, ETA, the cost, a confirm token). The yes must come only after they've seen that quote; then call it again with `confirm`. It runs in the background for several minutes, so check `get_research_status(run_id)` later rather than waiting.
When a planning session starts, check `get_market_updates`.

Rules: never send user-level data, secrets or code in `goal`. When a tool says NOT RESEARCHED YET, tell the user plainly and never present nearby items as research on that area. Never confirm a `start_research` quote without the user's explicit yes, and never reuse a confirm token for a different request. Cite only the rivals and evidence the tools returned.

### When to use it

Reach for 6to9 whenever the task touches how the product wins or loses users, even if nobody says "6to9":

- Building or changing the **landing page or hero**, **signup or login**, **onboarding**, the **pricing page**, or **core app flows**.
- "What should we build next?", "what's missing for <audience>?", roadmap or sprint planning.
- "We get visits but few signups", "users sign up and never come back", any conversion or activation problem.
- "How do competitors do X?", "who are we up against?".
- Any mention of 6to9.

Not for: fixing a type error, renaming, refactoring, dependency bumps, or other work that doesn't change what users see or do.

### Step 1: know which product this repo is

1. Read `.6to9.json` at the repo root. If it holds `{"product_id": "<id>"}`, pass that id as `product` to every tool and skip the rest of this step.
2. Otherwise call `list_my_products`.
   - One product: use it, and write `.6to9.json` with its id.
   - Several: find this repo's own site url in `package.json` `homepage`, deploy config (`vercel.json`, `netlify.toml`, `fly.toml`), README links, or the git remote. Suggest the product whose `url` matches, and **ask the user to confirm once**. A match is only a suggestion; never pick silently.
3. Write `.6to9.json` as `{"product_id": "<id>"}`. The user may commit it or ignore it.

If a tool answers CHOOSE A PRODUCT FIRST, do exactly this step, then retry with `product`.

#### Which audience (ICP) this work is for
- `list_my_products` lists each product's audiences with who buys, their trigger and pitch.
- Infer the audience from the task and the repo (landing copy, pricing page, README). If one clearly fits, **suggest it and confirm once**, then save it as `"segment": "<slug>"` in `.6to9.json` next to `product_id` and pass it as `segment`.
- If the task is about an audience that is not on the list, say so and ask. Do not force-fit the nearest one. The founder can add it at product.6to9.ai.
- An audience with `research_state: none` has no research yet; say so honestly. Without a clear audience, omit `segment`: recommendations come back grouped by audience.

### Step 2: get the recommendation

Call `recommend_features` with:

- `area`: the part of the product in plain words ("landing hero", "signup", "onboarding", "pricing page", "core flows"). Omit it for "what should we build next?".
- `goal` (optional): one or two sentences on the problem in the user's own words, with aggregate context only, for example "landing gets ~2k visits a week and ~1% sign up". It only reorders and explains the picks; the tool works fully without it.
- `segment` (optional): an audience segment slug from `list_my_products`.

You get 3–5 items, each with why it fits this product (which rivals ship it, the evidence, the audience it serves, whether it's already built or planned), and a lead pick with a short build-spec summary. Items the founder already chose or put in Build come first: respect that order.

Show the user the top picks in a few lines each, and say which rivals back each one. If the user already asked you to build, go with the lead pick and say so.

### Step 3: build from the spec

Call `get_build_spec` with the item's `spec_id` and `building=true` when you are actually going to build it (this registers it in the team's Build tracker; use `building=false` to read or compare).

The prompt it returns is the same one the founder gets from "Copy prompt" in the 6to9 portal, bound to the reference they picked. Treat it as the brief:

- follow it, and keep its references (demo, visual, variant or competitor component) in view while you build;
- adapt it to this codebase's stack and design system;
- when you explain choices, cite only the evidence in the spec.

For "what's the minimum to ship for <audience>?", call `get_mvp_brief(segment)`.

### Step 4: close the loop

After the change ships, offer to call `report_build_result(spec_id, metrics, note)`. Metrics are aggregates ("signup rate +12% over 2 weeks"), never user-level data. It's optional, and the team may have turned it off; relay what it answers.

### Starting research

When a tool says something isn't researched, or the user asks 6to9 to look into something new — a new audience, one feature, or "dig deeper" via focus — **offer to research it**; if they're interested, call `start_research(product, audience?, item?, focus?)` for a quote.

1. Call it without `confirm` first. Depending on 6to9's state it can come back as: a quote — what will be researched, an ETA, and the cost (read it from the quote) — plus a confirm token good for that quote only; already researched (nothing to confirm; read that instead, or pass `focus` — e.g. "dig deeper into pricing for teams" — to dig into a different angle instead of re-running the same research); busy (already running elsewhere, no run_id yet — tell the user and don't start another run); or on a cooldown or over today's limit (tell the user; don't retry now).
2. **Show the quote to the user and ask.** Asking for research is not a yes; the yes must come after they've seen this quote — no answer is a no. Only then, call `start_research` again with `confirm` set to the token it gave you. Never confirm on the user's behalf, and never reuse a token for a different audience, item or focus — get a fresh quote instead. A token can also expire: call again WITHOUT `confirm` for a fresh quote, then ask again.
3. If any answer points at a link, says the key lacks permission, or says credits or payment are needed, send the user there (or to mint a key at the portal) and stop; don't retry.
4. Once confirmed it queues and runs in the background for several minutes. Tell the user that, keep working on whatever else is in front of you, and check back with `get_research_status(run_id)` later — never block on it or poll it in a tight loop. Done → read the results the normal way with `recommend_features` or `get_build_spec`. Failed → tell the user; if they want to retry, start over from a fresh quote.

### Market updates

At the start of a planning session, sprint or roadmap discussion, or when the user asks what changed, call `get_market_updates`. Summarize what matters for the work at hand. Use `mark_event` (seen, dismissed, acted) on events you've handled so the feed stays useful. Use `get_competitors` when you need the rival set itself.

### Guardrails

- **Aggregates only.** `goal`, `metrics`, `note` and `focus` carry aggregate numbers and plain descriptions. Never user-level data, emails, secrets, keys or source code.
- **Honest misses.** When a tool answers NOT RESEARCHED YET, tell the user plainly and never present the nearest items as research on the area they asked about — then either offer to start it (see Starting research) or point them to the portal link it gives.
- **Cite only what came back.** Name only the rivals and evidence the tools returned. Never invent competitor behaviour or claim research that 6to9 didn't return.
- **The founder's choices win.** Keep the tool's order; don't re-rank the founder's planned items below your own preference.
- **Errors.** If a tool says the key was rejected, tell the user to check or mint a key at https://product.6to9.ai/settings/api-keys. If 6to9 is unreachable, carry on without it and say so.
<!-- 6to9:end -->
