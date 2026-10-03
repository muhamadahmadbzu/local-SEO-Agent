---
name: war-room
description: "Structured multi-agent debate that decides a gate or any big question. Analysts take positions, the devils-advocate and compliance-officer cross-examine, analysts rebut with evidence or concede, and the ic-chair rules GO, CONDITIONAL GO or NO-GO with kill criteria. Use it at every rank-and-rent gate (niche, market, go/no-go, launch, deal) or when the user asks the team to \"argue\", \"debate\", \"stress-test\", \"challenge\" or \"decide\" something."
argument-hint: "<project slug> <gate 1-5 | custom question>"
---

# War Room Protocol

The war room exists because single-agent analysis is overconfident. Four rounds turn opinions into a decision
that holds up: **positions**, then **cross-examination**, then **rebuttal**, then **verdict**. You (the orchestrator)
chair the process. You do not argue. The `ic-chair` agent rules.

Request: $ARGUMENTS

## Ground rules (read them out in every dispatch)
1. **Evidence beats eloquence.** Every claim carries a label: MEASURED, OBSERVED, PRIOR, ASSUMPTION or UNKNOWN.
   A PRIOR can't overrule a MEASURED number.
2. **Steelman before you attack.** Critics restate the strongest version of a position first.
3. **Numbered objections** (O-1...) with a severity: FATAL, MAJOR or MINOR. Compliance BLOCK = FATAL.
4. **Concede when the data says so.** Changing your mind on evidence is the job, not a loss.
5. **Two rebuttal cycles max.** Whatever is still unresolved goes to the chair as is.
6. **The chair judges the record only.** No new research in round 4. Missing evidence counts against the claim.
7. **Write everything down.** The project folder is the transcript.

## Participants by gate
| Gate | Question | Round 1 (positions, in parallel) | Round 2 (cross-exam, in parallel) | Verdict |
|---|---|---|---|---|
| 1 Niche | Which 2-4 niches advance? | niche-scout, lead-value-economist | devils-advocate, compliance-officer | ic-chair |
| 2 Market | Which 1-3 niche-by-city combos advance? | geo-market-analyst, keyword-demand-analyst (quick), serp-competition-analyst (quick) | devils-advocate, compliance-officer | ic-chair |
| 3 GO/NO-GO | Build this site? | keyword-demand-analyst, serp-competition-analyst, lead-value-economist, geo-market-analyst | devils-advocate, compliance-officer | ic-chair |
| 4 Launch | Is it ready for Google and customers? | content-qa-editor, site-architect | compliance-officer, devils-advocate | ic-chair |
| 5 Deal | Price and terms for this tenant or network? | monetization-closer, lead-value-economist | devils-advocate, compliance-officer | ic-chair |
| Custom | Any question | 2-4 relevant specialists | devils-advocate (+ compliance if legal or policy) | ic-chair |

## Round 1: Positions (parallel)
Dispatch all Round-1 agents **in one message**. Each brief includes: the gate question, the files to read, the
output path (`research/0X-*.md` per their agent file), the template (`templates/memos/analyst-memo.md`) and this line:
"State a clear position (recommend, recommend with conditions, or do not recommend) and the evidence for it."
Skip agents whose memo already exists and is current for this gate. Re-use it.

## Round 2: Cross-examination (parallel)
Dispatch in one message:
- `devils-advocate`: "Read all Round-1 memos for Gate N in projects/<slug>/research/. Steelman, then write numbered
  objections with severity and the evidence needed to resolve each, plus a pre-mortem. Output
  research/06-red-team-gate-N.md (template templates/memos/red-team.md)."
- `compliance-officer`: "Rule CLEAR, CONDITIONAL or BLOCK on every item in scope for Gate N. Output
  research/07-compliance-gate-N.md (template templates/memos/compliance.md)."

## Round 3: Rebuttal (parallel, only where needed)
1. Read the objection tables. For every **FATAL** and **MAJOR** objection, identify the owning agent(s).
2. Dispatch each owner once (in parallel), with its objections listed by ID:
   "Respond to O-x, O-y in research/rebuttals-gate-N.md (template templates/memos/rebuttal.md) under a heading
   with your agent name. For each: CONCEDE
   (with your revised estimate), REBUT (with NEW evidence, labeled and sourced) or MITIGATE (with a concrete plan, its
   cost and its deadline). You may run tools and research."
3. If a rebuttal brings new evidence on a FATAL objection, send the devils-advocate (and compliance-officer, if it was
   their item) one ruling pass: "Rule RESOLVED, PARTIALLY or STANDS on each rebutted objection in
   research/rebuttals-gate-N.md. Append your rulings there."
4. Two cycles maximum. Then stop.
5. MINOR objections skip rebuttal. They go into the decision's to-do list.

## Round 4: Verdict
Dispatch `ic-chair`: "Gate N for projects/<slug>. Read the full record (memos, red team, compliance, rebuttals).
Score with the Gate N scorecard, apply the decision rules, and write decisions/gate-N-<name>.md (template
templates/memos/decision.md). Append the decision-log row to STATUS.md."

## After the verdict (orchestrator)
1. Update `projects/<slug>/project.json`: append to `verdicts` ({gate, verdict, score, date}), and set `phase` and `status`.
2. Tick the gate in `STATUS.md`.
3. Report to the operator in 25 lines or fewer: the verdict and score, the 3 decisive reasons, the strongest dissent,
   conditions with deadlines, kill criteria, next actions, and **decisions needed from the operator**.
4. CONDITIONAL GO: schedule the condition work first, and don't start the next phase's spending until the condition
   is met and recorded in the decision file.
5. NO-GO: record what would have to change to revisit, and propose the next-best option from the team's data (the
   next niche or city on the shortlist).

## Fast mode (low stakes or early triage)
For Gate 1 with priors only, or a quick custom question: Round 1 with a single analyst, Round 2 with the
devils-advocate only, no Round 3, then the verdict. Say "fast mode" in the decision file. Never use fast mode for
Gate 3 or Gate 5.

## Disagreement log
When two analysts disagree on a number (e.g. demand or difficulty), the chair's decision must name both numbers,
their evidence labels, and which one it relied on and why. Persistent disagreements become "assumptions to monitor"
with a review date.
