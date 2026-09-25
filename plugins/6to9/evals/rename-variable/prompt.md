---
description: A pure refactor. Must NOT reach for 6to9.
tags: [should-not-trigger]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Skill]
---

Rename the variable `usrCnt` to `userCount` everywhere in this function:

```ts
function summary(users: User[]) {
  const usrCnt = users.length;
  return `${usrCnt} users`;
}
```
