# Running the pilot: your steps, in order

Everything runs from the `handback-cases` folder, in Terminal or through Claude Code. Your API key goes in a `.env` file on your machine; it never goes in a chat.

## Step 0. Approve the wording of the scripted turns (about 15 minutes)

The approved case document describes turns 1 to 4 ("a warm, direct draft of about 70 words"); a model needs the actual words. Claude drafted them to match each description, in `cases/drafts/runnable_text_v0.3.yaml`.

1. Read that file. Check each turn against its description in `sources/PILOT_Draft_Cases_and_Rubric_v0.3_2026-10-15.md`. Change anything that doesn't sound right.
2. Set `approved_by_author: "2026-10-16"` (your date) near the top.
3. Run:

```bash
python3 scripts/import_markdown.py
python3 scripts/validate_cases.py
```

The validator should end with `0 errors`. Until Step 0 is done, it fails on purpose and no real run will start.

## Step 1. Set up once (about 5 minutes)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then open .env and paste your key after ANTHROPIC_API_KEY=
python3 scripts/dry_run.py    # every step on mock models; no key used, no cost
```

The dry run ends with "Dry run complete". Its output goes to `logs/dryrun/` and means nothing; it only proves the plumbing.

## Step 2. Check the cost, then generate (a few minutes)

```bash
python3 scripts/estimate_cost.py --epochs 2
```

About 100 calls and roughly 130,000 input tokens in all, most of it grading. Check the prices for the models you pick before going on.

Pick two models from Anthropic's models page: the **model under test**, and a **grader** (a different model; ideally a stronger one). Then:

```bash
# smoke test: one reply
inspect eval evals/handback.py@handback --model anthropic/<model-under-test> --limit 1 --epochs 1 --no-score
# the run: 4 cases x 2 replies = 8 replies, no grading
inspect eval evals/handback.py@handback --model anthropic/<model-under-test> --epochs 2 --no-score
```

Inspect prints the path of the log it wrote, in `logs/`. Copy that path; it's your **generation log**.

## Step 3. Score blind (about 1.5 hours)

```bash
python3 scripts/export_for_raters.py logs/<generation log>.eval
```

This writes `ratings/rater1_scoring.xlsx`. Open it in Excel or Numbers. Three tabs:

- **Score:** one row per reply, shuffled. Fill in the three dimensions, the five labels (Y/N), each criterion (Y/N; "n/a" cells don't apply), and a one-line reason that quotes the reply. Write ANCHOR? in Notes when an anchor didn't fit.
- **Cases:** the full conversation for each case.
- **Anchors:** the rubric and the labels.

Score all 8 in one sitting. Save and close. **Until you've saved, don't open `logs/` and don't run `inspect view`.** Once the grader runs, your scores are frozen; if you change your mind later, save a copy as `rater1_after.xlsx` instead.

## Step 4. Grade (a few minutes)

```bash
inspect score logs/<generation log>.eval \
  --model-role grader=anthropic/<grader> \
  --output-file logs/scored_grader1.eval

inspect eval evals/handback.py@handback_constructed \
  --model-role grader=anthropic/<grader>
```

The second command scores your gaming probes. No model writes anything there; your constructed replies are used word for word.

Always score the **generation** log (the one from Step 2), never an already-scored log.

## Step 5. Reports

```bash
python3 scripts/agreement.py --rater ratings/rater1_scoring.xlsx --key ratings/rater1_key.json \
  --grader logs/scored_grader1.eval
python3 scripts/gaming_report.py logs/<handback-constructed log>.eval
```

They write `ratings/agreement_report.md` and `ratings/gaming_report.md`. Then fill in the brackets in `LIMITS.md`.

## Optional. Grader swap

Repeat Step 4 with a second grader and a new `--output-file` (for example `scored_grader2.eval`), then pass both logs:

```bash
python3 scripts/agreement.py --rater ratings/rater1_scoring.xlsx --key ratings/rater1_key.json \
  --grader logs/scored_grader1.eval --grader logs/scored_grader2.eval
```
