---
description: A pure code fix. Must NOT reach for 6to9.
tags: [should-not-trigger]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Fix this TypeScript error: `Type 'string | undefined' is not assignable to type 'string'.` It's on the line `const name: string = user.name;` in our user profile component.
