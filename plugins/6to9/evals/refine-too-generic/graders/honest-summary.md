---
type: llm
---

PASS if the final answer does all three:
1. says the spec was changed in 6to9 (not only in a local copy);
2. names what 6to9 changed: the detail and the copy (or plainly equivalent wording, e.g. "the details and wording");
3. says the change can be undone (e.g. a revert, "go back", or `revert_spec`).

Summarising the new build prompt is expected and fine. Remarks about the repo, the product id or offers to build next are fine.

FAIL only if one of the three is missing, OR the answer says it edited a file in the repo as the revised spec, OR it says 6to9 changed fields other than the detail and the copy (e.g. "6to9 also changed the title").
