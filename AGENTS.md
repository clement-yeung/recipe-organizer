# AGENTS.md

Personal Traditional-Chinese cookbook. `dishes/*.md` are the source of truth; `export/` is generated. There is no app, test suite, linter, or CI.

## Commands

```bash
python3 build_cookbook.py               # full build: exports md/html/pdf
python3 build_cookbook.py --merge-only  # fast: md/html only, no venv/Playwright
```

- Full build self-bootstraps `_support/.venv` (currently Python 3.9.6), pip-installs Playwright, runs `playwright install chromium`, then re-runs the script with `--render`. First run needs network.
- Use `--merge-only` to validate recipe parsing, sorting, and HTML quickly. It never touches the venv.
- `--render` is an internal second pass that assumes Playwright is already importable; do not call it directly.
- There is no test/lint command. Verification means running the build and checking `export/`. Do not claim the PDF works unless you ran the full build.

## Recipe content

- Read `_support/AI_INSTRUCTIONS.md` before adding or editing recipes; it is the authoritative spec (templates, timing, tool labels, dietary rules). `_support/TEMPLATE.md` is the starter.
- Write all recipe content in Traditional Chinese.
- One recipe per file, no subfolders.
- Filenames: `NNN-菜名.md`, three-digit prefix, next free number after the current maximum. Never renumber, reuse, or backfill numbers. The in-file `# 標題` must not include the number.
- Preferences: no garlic, no scallion/shallot; onion only as large removable pieces that are taken out and discarded after cooking.
- Required header fields: `器具`, `份量`, time field(s), `狀態`. Rice-cooker recipes list only `準備時間` (never steam or total time); oven/stove recipes list `準備時間` and `烹調時間`. Use `額外等待` only when relevant.
- No trial logs, dates, blank fill-in fields, or history sections. Update the current recipe in place.
- Do not add or maintain a recipe index in `README.md`; the TOC is generated from filenames.

## Markdown limits

The custom renderer in `build_cookbook.py` is not full Markdown. Recipes may contain only:

- headings, paragraphs, single-level ordered/unordered lists
- `**bold**`, `` `inline code` ``, `[text](https://…)` (http/https only)

Do not put tables, images, nested lists, fenced code blocks, raw HTML, or manual page breaks in recipes — they are unsupported and may be flattened or dropped.

## Do not edit

- `export/cookbook.md|html|pdf` — generated and gitignored; overwritten on every build. Edit `dishes/` and rebuild.
- `_support/.venv/` — local virtualenv created by the build and gitignored. Do not edit or delete it; recreating it is slow and may require network.
- Layout, CSS, page frame, TOC, and pagination live only in `build_cookbook.py`; keep recipes as plain Markdown.

## Gotchas

- Each recipe's PDF title comes from its first `# ` heading; if missing, the filename stem is used and an `# title` line is prepended. Keep exactly one H1.
- Build order is `casefold()`ed relative path, so numeric prefixes control PDF order.
- Regenerating exports rewrites files under `export/`, which is gitignored. Never force-add generated output.
- `docs/preview.png` is a committed screenshot of the PDF cover, used by `README.md`. Re-shoot it after changing layout or CSS in `build_cookbook.py`:
  `qlmanage -t -s 1600 -o docs export/cookbook.pdf` (then rename the output to `preview.png`).
- Never put `_support/AI_INSTRUCTIONS.md`, `_support/TEMPLATE.md`, or `README.md` into `dishes/` — everything in `dishes/` is exported as a recipe.
