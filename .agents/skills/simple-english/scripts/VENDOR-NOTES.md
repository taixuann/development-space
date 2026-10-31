# Vendor notes

This file records where each added file came from and what this install changed.
Read it before you update the skill from upstream again.

Upstream is AminBlg/SimpleEnglish on GitHub, MIT license. The copy in this
folder came from commit 32ea2d3, tag version 2.1.1. The SKILL.md in this folder
matched upstream byte for byte before this update.

## Added files

| File in this skill | Path in upstream | Change |
|---|---|---|
| `scripts/ste-lint.py` | `evals/ste_lint.py` | none. Copied as is. |
| `scripts/slop.tsv` | `evals/slop.tsv` | none. A relative link to `../references/slop.tsv`. The linter reads the file next to itself. |
| `references/slop.tsv` | `evals/slop.tsv` | none. Copied as is. The linter link and this file hold one copy of the data. |
| `scripts/dictionary/parse_dict.py` | `tools/ste-dictionary/parse_dict.py` | none |
| `scripts/dictionary/emit.py` | `tools/ste-dictionary/emit.py` | none |
| `scripts/dictionary/ste_dict_lint.py` | `tools/ste-dictionary/ste_dict_lint.py` | none |
| `scripts/dictionary/README.md` | `tools/ste-dictionary/README.md` | none |

No upstream Python file was edited. Each one uses the standard library only.
None of them open a network connection, start a process, or evaluate code.

## Changed in SKILL.md

The install changed four parts of SKILL.md and bumped the version to 2.2.0.

1. Rule 5 now keeps a hedge in an error message, a status report, and any text
   that tells what a person or an agent does not know. The old rule banned
   "may", "might", and "could" everywhere, which forced a rewrite to turn a
   doubt into a fact.
2. A new Output section sets the output contract.
3. The Self-Check section gained a machine pass, a modality check, and a
   content check.
4. A new section, What This Skill Can Check, states which rules the linter
   verifies and which rules need the ASD dictionary.

## Known limit

The linter counts "may", "might", and "could" as banned in every text. It does
not read rule 5. When rule 5 tells you to keep a hedge, the linter finding on
that word is expected. Keep the hedge. The Self-Check section says this too.

## Files not vendored

Three upstream files stay out of this folder on purpose.

- `evals/check_numbers.py` reads `README.md`, `evals/scenarios.json`, and
  `evals/results/rebuild-2026-09-02/`. It checks the numbers published in the
  upstream README against its own benchmark files. It is a repository tool. It
  does not check a rewrite, and it fails to start without those files.
- `src/hooks/` holds the SessionStart hook. The hook loads the writing rules at
  the start of a session. It needs the upstream plugin. A folder copy cannot
  run it.
- `evals/run_bench.py`, `evals/run_pi_bench.py`, and `evals/run_reply_bench.py`
  need paid model API keys. They measure the skill. They are not part of it.

## Dictionary content

This folder holds no ASD word list. Issue 9 page 2 of ASD-STE100 forbids
reproduction of the standard, in whole or in part, without written authority
from ASD. The `scripts/dictionary/` tools make the word lists from a copy of
the standard that you own. Do not commit the generated files.