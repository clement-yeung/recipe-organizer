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

## 選菜多樣性與鮮明風味

- 使用者要求新菜、不同食譜或提供選項時，預設推薦真正不同的菜色，不只是上一道菜更換一兩種醬料。只有明確要求調整既有配方或比較單一變因時，才以小幅變化為主。
- 不要反覆套用「整片雞胸＋甜鹹醬汁＋電鍋蒸」的同一框架，再把換醬版本當作全新菜。即使主食材或器具固定，也應探索不同的菜色結構、配料、口感、料理風格或呈現方式；遵守當次整片、不切、不煎等限制。
- 一次提供多個選項時，讓選項在菜色概念上有實質區別，簡短指出差異，而不是列出多組相似醃料。不要把某次方便操作的限制永久套用到未來所有推薦。
- 預設追求風味鮮明、層次清楚、有主題的料理，不自動把配方設計成清淡、微甜或少量調味。大膽不等於一律加鹽、加糖、加辣或堆疊瓶裝醬料；也不代表使用者一定喜歡辣。
- 優先參考有可靠來源、搭配邏輯清楚的完整菜色，再依偏好調整。不要只因現有兩種醬料就任意混搭並假設相配；須考慮食材重量、醬料濃度、烹調出水與最終醬汁濃淡。
- 不為了遷就現有調味料或電鍋而勉強改造不適合的菜；必要時清楚說明需要補買的關鍵材料，或提出符合當次器具限制的其他菜色。未經試做的個人調整仍標示待試，不保證風味或口感。
- 保留既有食材偏好與安全要求，不用大蒜、青蔥、紅蔥頭等使用者不喜歡的食材來補強味道。
- 不再推薦「海鮮醬＋味醂蒸雞胸」：使用者實際回饋整體太淡，且這兩種調味搭配不好吃。不要主動以加重調味、改名或小幅變體重新推薦；除非使用者明確要求重新討論。不將此回饋擴大解讀成討厭海鮮醬或味醂本身。
