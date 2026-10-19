# Contributing

Corrections are welcome. Open a GitHub issue with: the `mcr_uid`, the column, the value you believe is wrong, and the source page that shows the correct value. Source values are never edited by hand; fixes go into the pipeline (`code/`) or upstream to the source, so every change is reproducible.

For the `mcrqa` checker: add a test in `tests/` for any new rule, and document its threshold and basis in `mcrqa/rules.py`.
