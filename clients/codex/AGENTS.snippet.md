<!-- 6to9:start -->
<!-- GENERATED from guide/agent-guide.md in github.com/6to9-ai/6to9-plugin by scripts/generate.py (Codex AGENTS.md block). Edit the source and re-run; never edit a copy. -->

## 6to9: product and competitor intelligence

6to9 researches this product's competitors and turns that research into ranked feature recommendations and build-ready specs. Before you design or build a product surface (landing page or hero, signup or login, onboarding, pricing, core app flows), or when the user asks what to build next, why conversion or activation is low, or how competitors do something, call `recommend_features` first, then `get_build_spec` on the item you build. You do not need to be asked to use 6to9.

Workflow:
1. Product: read `.6to9.json` (`{"product_id": "..."}`) at the repo root. If it is missing, call `list_my_products`, suggest the product whose url matches this repo's site, confirm with the user once, and write `.6to9.json`. Pass the id as `product`. `.6to9.json` may also hold `segment`; pass it as `segment`.
2. `recommend_features(area, goal)`: `area` in plain words ("landing hero", "onboarding"); `goal` optional, the problem in the user's terms with aggregate numbers only.
3. Show the top picks briefly, or go straight to the lead pick if the user already asked you to build.
4. When you BUILD a spec: `get_build_spec(spec_id, building=true)` (only to read or compare: `building=false`), and follow its prompt. Its `build_options` rank the spec's ARTIFACTS (working demo, mock, rival components). If the founder hasn't picked one, show the user the options (best first) and let them choose; record it with `pick_artifact`. Open one with `get_artifact(spec_id, artifact_id, building=true)`: a demo returns its HTML source to port into this repo's framework only with `building=true` (without it, it is shown to the user and returns no source) — a web fetch of its URL loses the code. An OUTDATED artifact (made from older spec text): tell the user and don't build from it; if a version made from the current text exists and the user wants it, `revert_spec` to it is free — don't refine to get there. A STYLE OUTDATED demo (built with an earlier version of the founder's site style): its content is current — tell the user; building from it is fine (match this repo's look), but prefer a version in the current style when one is offered.
5. After shipping, offer `report_build_result`.
6. NOT RESEARCHED YET, or the user wants something new researched? An idea becomes a build spec with `start_research(item=<spec_id>)`; an audience missing from `list_my_products` must first be added with `add_audience(name, description)` (on the user's ask; if 6to9 says it matches an existing audience, offer that one). Offer to research it; when they say yes (or asked for it themselves), call `start_research` — it starts it. Only if 6to9 returns a quote (e.g. it will use credits) show it and ask before calling again with its `confirm`. It runs in the background, so check `get_research_status(run_id)` later rather than waiting.
7. The user wants a 6to9 spec changed (the one you're building from, or one they name)? Pass a spec id they give straight to the tool; only a title needs `recommend_features(query=<title>)` first to find its spec_id. Its text ("too generic", "mobile-first") → `refine_spec(spec_id, instruction)` with their words, even when the change needs research 6to9 doesn't have yet (refine_spec starts it; don't offer `start_research` instead unless it answers NOT RESEARCHED YET). One of its artifacts ("darker mock", "the demo should show 3 slots") → `refine_artifact(spec_id, artifact_id, feedback)` with their words — 6to9 decides whether that also changes the text; don't also call `refine_spec`. Then re-read `get_build_spec`. `list_spec_history` / `revert_spec` undo.
8. Showing an idea ("show me this idea", "what would it look like", "is there a demo"): call `view_idea(spec_id)` (free). It renders the idea inline: an interactive card with the live demo where this chat supports it, otherwise a preview image and the live demo link. When the card did not appear, show the preview image from the result and give the link; don't paste HTML. `show_idea` MAKES new visuals and costs a run; use it only when an idea has nothing to show (their "show me" is the ask — don't ask again) or they want new ones — once per ask; it takes a couple of minutes. If it times out, don't call it again: `view_idea` a few minutes later. Not `get_build_spec`.
When a planning session starts, check `get_market_updates`.

Rules: never send user-level data, secrets or code in `goal`. When a tool says NOT RESEARCHED YET, tell the user plainly and never present nearby items as research on that area. Start research or change a spec only when the user asked or agreed — never speculatively. If 6to9 returns a quote, never confirm it without the user's explicit yes, and never reuse its token for a different request. Cite only the rivals and evidence the tools returned.

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

The prompt it returns is the same one the founder gets from "Copy prompt" in the 6to9 portal, bound to the artifact they picked. Treat it as the brief:

- follow it, and keep the artifact it binds in view while you build;
- adapt it to this codebase's stack and design system;
- when you explain choices, cite only the evidence in the spec.

For "what's the minimum to ship for <audience>?", call `get_mvp_brief(segment)`.

### Step 4: close the loop

After the change ships, offer to call `report_build_result(spec_id, metrics, note)`. Metrics are aggregates ("signup rate +12% over 2 weeks"), never user-level data. It's optional, and the team may have turned it off; relay what it answers.

### Starting research

When a tool says something isn't researched, or the user asks 6to9 to look into something new — a new audience, one feature, or "dig deeper" via focus — **offer to research it**; when they say yes (or asked for it themselves), call `start_research(product, audience?, item?, focus?)`.

- **An idea** (no spec yet): `start_research(item=<spec_id>)` turns it into a build spec.
- **An audience that isn't in `list_my_products`**: add it first with `add_audience(name, description)` in the user's words, only on their ask. If 6to9 says it's the same as an audience the product already has, nothing is added — offer that audience instead. A new audience comes back with its slug, not researched yet: then `start_research(audience=<slug>)` if they want it researched.

1. Call it once the user asked or agreed. It usually starts right away and returns a run_id. It can instead come back as:
   - **already researched** — read that instead, or pass `focus` to dig into a different angle;
   - **busy** — already running elsewhere; tell the user and don't start another;
   - **on a cooldown or over today's limit** — tell the user; don't retry now;
   - **a quote** — only when 6to9 needs approval (e.g. it will use credits): show it, and only after the user's explicit yes call again with that quote's `confirm`. Never reuse a token for a different request.
2. **Never confirm a quote on the user's behalf.** No answer is a no. A token can also expire: call again WITHOUT `confirm` for a fresh quote, then ask again.
3. If a `start_research` answer points at a link, says the key lacks permission, or says the account must add credits or pay first, send the user there and stop; don't retry.
4. Once started (or confirmed) it queues and runs in the background. Tell the user that, keep working on whatever else is in front of you, and check back with `get_research_status(run_id)` later — never block on it or poll it in a tight loop. Done → read the results the normal way with `recommend_features` or `get_build_spec`. Failed → tell the user; if 6to9 says it can be retried and they want to, call the same tool again (`refine_spec` for a spec change, `start_research` otherwise).

### Refining a spec

When the user wants a 6to9 spec changed — the one you're building from, or one they name by its spec id or title — change it in 6to9, don't just edit your own copy. A spec id or spec title in the request names a 6to9 spec even when no such page exists in this repo yet. Pass a spec id straight to the tool below; only when you have just a title, find its spec_id with `recommend_features(query=<title>)` first.

- **Text** ("too generic", "mobile-first", "shorter copy", "target teams"): `refine_spec(spec_id, instruction)` with the user's own words. Call it even when the change needs research 6to9 doesn't have (a rival or pattern it hasn't looked at): it starts that research itself and returns a run_id — tell the user it's running and check `get_research_status` later. Don't offer `start_research` for a spec change instead — unless `refine_spec` answers NOT RESEARCHED YET (an idea 6to9 hasn't researched has no spec to change): then offer the research it names, and refine once it lands.
- **One of its artifacts** (the demo, the mock, a rival component): `refine_artifact(spec_id, artifact_id, feedback)` — see *A spec's artifacts*.
- **Undo / go back**: `list_spec_history(spec_id)`, then `revert_spec(spec_id, revision=N)` for the text, `(artifact_id=…, version=N)` for an artifact.

After any change, call `get_build_spec(spec_id)` again before building: the build prompt changed. Only change a spec when the user asked for it. If a change times out, call `list_spec_history` before trying again — it may already have landed.

### Seeing an idea

When the user wants to see what an idea or spec would look like — "show me this idea", "what would it look like", "is there a demo" — call `view_idea(spec_id)` first. It is free and shows what 6to9 already made: an interactive card with the live demo where the chat supports it, otherwise a preview image and the live demo link (show the image and give the link; don't paste HTML). When it says the idea has nothing to show, or the user wants new visuals, call `show_idea(spec_id)`: 6to9 builds a working demo, a mock in the product's own style and rival variants, and keeps whichever it could make. It's paid and counts toward 6to9's daily limits: call it only when the user asked or said yes to your offer, and only once per ask. It takes a couple of minutes, and its answer shows the idea the same way `view_idea` does. If it times out, 6to9 is still building: don't call `show_idea` again — call `view_idea` a few minutes later. On an idea 6to9 hasn't researched it answers NOT RESEARCHED YET: offer `start_research(item=<spec_id>)` first.

### A spec's artifacts

A 6to9 spec is its text plus artifacts: a **working demo** (a live HTML page), the **generated mock** (an image), **rival components** (what rivals actually ship — evidence, never edited), restyles of a rival component, and **our own versions** made from a rival component. Operate on artifacts; 6to9 keeps them consistent with the text.

- **See them:** `list_artifacts(spec_id)` (free) — ranked, with ids, the founder's pick, and which are outdated. `get_build_spec` shows the same list as `build_options`.
- **Open one:** `get_artifact(spec_id, artifact_id, building=true)` when you build from it (the HTML source comes back only with `building=true`) — a demo or our own HTML version returns its source (reference code: port its structure, interaction and copy into this repo; don't paste the file); an image returns its URL. Without `building=true` it shows the artifact to the user instead, with no source. Free, except that opening an OUTDATED artifact starts its refresh (paid, once per change).
- **Change one:** `refine_artifact(spec_id, artifact_id, feedback)` with the user's words — paid, only on their ask, once per ask; it can take a few minutes. A look-only change ("darker") changes that artifact only. A change to the feature ("only 3 slots", "add a waitlist") also updates the spec text, and the other artifacts follow it — tell the user which. Refining a rival component makes our own version next to it. If it times out, 6to9 is still working: don't call it again — read `list_artifacts` a few minutes later.
- **Choose one:** `pick_artifact(spec_id, artifact_id)` — then `get_build_spec` builds from it. Free, except that picking an OUTDATED artifact starts its refresh (paid, once per change).
- **OUTDATED** means made from older spec text; never build from it as if it were current, and tell the user. **STYLE OUTDATED** (a demo only) means it was built with an earlier version of the founder's site style while its content is current: tell the user; building from it is fine (match this repo's look), and if a version in the current style is offered, prefer it (`revert_spec` to it is free). The answer says why, e.g.:
  - *refreshing* — 6to9 is making a new version from the current text: build from the prompt's text or check back in a few minutes.
  - *a version made from the current text exists* (e.g. *on purpose — reverted from vN*: someone reverted to an older version) — if the user wants the version made from the current text, `revert_spec(spec_id, artifact_id=…, version=N)` shows it again for free — don't refine to get there.
  - *not refreshing (reason)* — 6to9 won't refresh it now; tell the user the reason and build from the prompt's text.
- **Switched back:** when the spec text returns to an earlier text, 6to9 shows the artifact versions made from that text again, for free: "6to9 switched back to vN, made from the current text — nothing regenerated."
- **Undo:** `list_spec_history(spec_id)` lists the text revisions and every artifact's versions; `revert_spec(spec_id, artifact_id=…, version=N)` shows an earlier version again (free). When a `refine_artifact` also changed the text, undo the text with `revert_spec(spec_id, revision=…)` — the revision before the one the refine answer names; the answer gives the exact call; reverting the artifact alone keeps the new text.
- **Busy:** something (a refresh, another change, a research run) is working on that artifact or spec right now. Tell the user and check back with `list_artifacts` later — don't retry in a loop.

`update_spec_visual`, `pick_spec_variant` and `get_demo_html` still work; prefer the artifact tools.

### Market updates

At the start of a planning session, sprint or roadmap discussion, or when the user asks what changed, call `get_market_updates`. Summarize what matters for the work at hand. Use `mark_event` (seen, dismissed, acted) on events you've handled so the feed stays useful. Use `get_competitors` when you need the rival set itself.

### Guardrails

- **Aggregates only.** `goal`, `metrics`, `note`, `focus`, `instruction` and `feedback` carry aggregate numbers and plain descriptions. Never user-level data, emails, secrets, keys or source code.
- **Honest misses.** When a tool answers NOT RESEARCHED YET, tell the user plainly and never present the nearest items as research on the area they asked about — then either offer to start it (see Starting research) or point them to the portal link it gives.
- **Cite only what came back.** Name only the rivals and evidence the tools returned. Never invent competitor behaviour or claim research that 6to9 didn't return.
- **The founder's choices win.** Keep the tool's order; don't re-rank the founder's planned items below your own preference.
- **Errors.** If a tool says you are not signed in or the credential was rejected, tell the user to sign in to 6to9 again (in Claude Code: `/mcp`, choose 6to9, Authenticate; other clients that use a pasted key: check or mint one at https://product.6to9.ai/settings/api-keys). If 6to9 is unreachable, carry on without it and say so.
<!-- 6to9:end -->
