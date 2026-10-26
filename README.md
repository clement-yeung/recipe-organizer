# 我的食譜

一道菜一個 Markdown 檔案，存放在 `dishes/`。

本 README 不維護個別食譜清單。
新增、刪除或改名食譜時，不需要更新本文件。

## 日常使用

- 直接在 `dishes/` 新增或修改食譜。
- 新食譜可複製 `_support/TEMPLATE.md`。
- 多器具食譜只保留一份檔案，在內容中列出需要的器具。
- 在 VS Code 按 `Cmd + Shift + V` 查看 Markdown 預覽。
- 不需要手動合併食譜或維護目錄。

## 匯出整本 PDF

在 VS Code 開啟 `recipes` 資料夾，
開啟 Terminal，執行：

```bash
python3 build_cookbook.py
```

腳本會自動掃描 `dishes/` 裡的 Markdown 食譜，
重新建立整本食譜及其目錄。

電腦需要已有可用的 Python 3。
首次執行需要網路，腳本會自動準備
`_support/.venv/`、Playwright 與 Chromium。

不需要修改 VS Code 設定，也不使用 LaTeX。

這是執行時更新，不是儲存食譜後立即更新。
每次想產生新版 PDF 時，重新執行指令即可。

## 輸出檔案

- [整本食譜 PDF](export/cookbook.pdf)
- [合併後的 Markdown](export/cookbook.md)
- [HTML 排版預覽](export/cookbook.html)

第一次執行後才會出現這些檔案。

每次執行會覆寫產出，但不修改原始食譜。
不要直接編輯 `export/` 裡的檔案。

## 食譜順序

依 `dishes/` 中的相對檔名排序。

若想指定順序，可在檔名前加上：

```text
01-香菇玉米蒸肉餅.md
02-番茄炒蛋.md
03-烤雞腿.md
```

不使用編號也可以。
新增、刪除或改名後，下一次匯出會自動反映。

## PDF 樣式

- 一本 PDF 包含全部食譜。
- 封面提供藍色、可點選的食譜目錄。
- 每道食譜從新的一頁開始。
- 標題、小標題、正文與頁碼使用黑色。
- 目錄連結及網站連結保留藍色。
- 每頁保留細藍框，放在正文區域外側。
- 食譜標題沒有水平底線。
- 器具使用文字與原有圓點符號。
- 長食譜自然續頁，不強制縮小字體。

## 檔案結構

```text
recipes/
├── README.md
├── dishes/
├── build_cookbook.py
├── export/
│   ├── cookbook.md
│   ├── cookbook.html
│   └── cookbook.pdf
└── _support/
    ├── AI_INSTRUCTIONS.md
    ├── TEMPLATE.md
    ├── requirements.txt
    └── .venv/
```

`export/` 和 `_support/.venv/` 由腳本自動產生。

## 讓 AI 協助修改

將 `_support/AI_INSTRUCTIONS.md` 的全部內容提供給 AI。

指引已包含完整範本、偏好與工具限制，
不必另外貼上 `TEMPLATE.md`。

修改既有食譜時，仍須讓 AI 讀取該檔案，
或一起貼上食譜內容。

## Markdown 格式

支援標題、一般段落、單層清單、粗體、
行內程式碼及 HTTP(S) 連結。

食譜內不要加入表格、圖片、巢狀清單、
程式碼區塊或原始 HTML 排版。# recipe-organizer
