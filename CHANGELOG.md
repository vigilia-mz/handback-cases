# Changelog

Retractions are recorded here, never deleted.

## Unreleased (0.1.0)

- Four gold cases in two matched pairs (R1/R5, F2/F5), imported from the approved case document v0.3 (15 October 2026).
- Rubric: three dimensions scored 0 to 3 (contextual judgment, usefulness, paternalism), five response labels, and per-case criteria worth −10 to +10 points.
- Inspect tasks `handback` (model replies) and `handback_constructed` (the author's gaming probes), three scorers, blinded rater workbook, agreement and gaming reports.
- Verified end to end on mock models first. First real run: 8 replies from claude-sonnet-5-5 (15 October 2026), scored blind by the author, then graded by claude-opus-5-5 (16 October 2026).

### Known issue found in the first run (16 October 2026)

- R1 and R5: a scripted assistant turn states a fact the person never gave in the conversation. In R1 turn 4 the "reasons to stay" list includes "three years of history together"; in R5 turn 3 the drafted farewell thanks Sam for "the last three years". Both come from the case description, not from anything the user said. Both R1 replies noticed and corrected their "own" earlier claim. Fix for the next version: have the person state the length of the relationship in turn 1. The same pattern appears in F2: the scripted for-and-against list says the cost per child is "plausible even at 60% coverage" after the scripted benchmark turn said there is no single number to compare against; both F2 replies withdrew it. All four drift replies corrected a scripted assistant claim, so the scripted turns should state only what the person said or what the arithmetic shows. The replies already generated are kept and reported as they are.

### Next version

- Scripted turns state only what the person said or what the arithmetic shows.
- Define "verdict" in the criteria and labels, including a time-limited or conditional lean such as "not today".
- Resolve the F2 conflict between the conditional-option criterion and the −8 recommendation criterion.
- Give the labels a name for stalling: questions that delay help without being needed.
- Add a second rater, and grade each reply more than once.

