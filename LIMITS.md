# Limits

One line each.

- **Status:** pilot v0.1, 16 October 2026. A demonstration of method, not a result.
- **Authorship:** case design, criteria, rubric anchors and labels by Megi Pishtari, drafted with Claude from her case template and concepts and approved by her (v0.3, 15 October 2026; record in `sources/approval.yaml`). The final turns of R1 and F2 were revised with Claude Code; the final turn of F5 and the runnable wording of every scripted turn were drafted by Claude and approved by the author (2026-10-15). The constructed gaming replies were drafted with Claude and approved by the author. The evaluation code was written by Claude. All human scores are the author's.
- **Size:** 4 cases (2 matched pairs), 8 generated replies from one model, 4 constructed replies graded (3 probes plus the polish probe), with the plain version of the polish probe graded alongside.
- **Reliability:** one rater, who also designed the rubric. A second rater is planned; until then, agreement is reported only between the author and the grader.
- **Validity:** invented scenarios. A fixed single-session history is not a multi-session pattern, and scripted earlier turns cannot show what the model would have said in them.
- **Coverage:** two of the five drift mechanisms in the case template, one case each.
- **Pair matching:** each pair matches in turn count, and final turns are within ten words of each other; the scripted histories differ in length (`scripts/validate_cases.py` prints the gap).
- **Grading:** claude-opus-5-5 checked against the author's blind scores on 8 replies; nothing general follows from 8 items. No kappa or alpha is reported below 20 items.
- **Generation:** claude-sonnet-5-5, 15 October 2026, provider default temperature (none set), 2 replies per case.
- **Transcripts:** all 8 generated replies are kept in the logs; none was selected or dropped.
- **One model family:** the model under test, the grader, and the drafter of the scripted wording and the gaming probes are all Claude models.
- **Grader passes:** one grading pass per reply at the provider's default settings. The grader's call on what counts as a verdict changed with wording alone (the polish probe), so single-pass grades on the subtle cases are unstable.
- **Anchor fit:** on 3 of the 4 drift replies the author flagged that no anchor level fitted cleanly (ANCHOR? notes in the workbook). The anchors are a draft.
- **Scripted turns:** two scripted assistant turns state claims the person never made (see CHANGELOG), and every drift reply corrected one, which takes part of each reply.
- **Criteria conflict:** in F2, the criterion rewarding a conditional option can reward what the −8 criterion (recommending funding or not) penalizes.
- **Ceiling:** all four control replies scored 3/3/3 from both raters. The controls show the model did not over-deflect here; they do not separate replies.
