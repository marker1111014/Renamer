# Renamer 重新命名工具

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?logo=qt)
![Tests](https://img.shields.io/badge/Tests-46%20Passed-brightgreen)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows)

一個現代、直覺且安全可靠的桌面批次檔案重新命名工具。具備深色主題介面、零延遲雙欄即時預覽、兩階段交易式更名防護、以及一鍵復原 (Undo) 功能。

---

## 🌟 主要功能特色

### 1. ⚡ 雙欄即時動態預覽 (Live Preview)
* **零延遲即時反饋**：調整「刪除前綴字數」、「全刪」、「前置詞」、「起始數字」或「自動補零」時，右側新檔名欄位即時聯動更新，無須點擊即可預覽效果。
* **智慧狀態著色**：
  * 🟢 **薄荷綠 (`#4EC9B0`)**：名稱即將變更的檔案。
  * ⚪ **暗灰色 (`#8A8A8A`)**：維持原名不變的檔案。
  * 🔴 **亮紅色 (`#FF6B6B`)**：同目錄新檔名重複衝突（即時標註 `⚠️ 重複` 警示）。
* **詳細提示資訊**：滑鼠懸停於任一項目即可查看檔案完整原始路徑與預計目標路徑。

### 2. 🛡️ 兩階段交易式安全防護機制 (Transaction-like Safe Rename)
* **無損暫存機制**：採用「原始 ➔ 暫存 ➔ 目標」雙階段改名演算法，杜絕批次內互換檔名 (Swap) 造成的自我覆蓋問題。
* **真正無害的跳過 (SKIP)**：當目標檔名存在且使用者選擇「跳過」時，系統會將檔案還原回原始名稱，絕不竄改或加上任何前綴後綴。
* **完整反向回滾 (Atomic Rollback)**：若執行過程中遭遇權限不足、檔案佔用或使用者中途取消，系統自動執行完整的反向回滾，確保檔案系統狀態 100% 一致。
* **暫存檔碰撞防禦**：自動偵測並避開既存的暫存檔案名稱。

### 3. ↶ 一鍵復原 (Undo / `Ctrl+Z`)
* 支援批次重命名歷史堆疊。重命名完成後若發現規則設定錯誤，只需點擊 **「↶ 復原」** 或按下快捷鍵 **`Ctrl+Z`**，即可將該批檔案全數安全還原為原本名稱。

### 4. 📁 多元匯入與資料夾遞迴掃描
* **按鈕選擇**：工具列提供「＋ 加入檔案」與「📁 加入資料夾」對話框。
* **拖曳支援**：可直接將單檔、多檔或**整個資料夾**拖入清單。拖入資料夾時自動遞迴掃描子檔案，並智慧過濾隱藏目錄（如 `.git`）與系統廢檔（如 `Thumbs.db`、`desktop.ini`、`.DS_Store`）。

### 5. ⇅ 7 種快速排序（支援自然排序演算法）
* 點擊工具列的「⇅ 排序 ▾」選單，即時依以下規則重整順序並自動重新編號：
  * 🔤 檔名正序 / 倒序（採用自然排序 `Natural Sort`：`file2` 優先於 `file10`）
  * 🕒 檔案修改時間（由舊到新 / 由新到舊）
  * 📄 檔案大小（由小到大 / 由大到小）
  * 🏷️ 依照副檔名類型排序

### 6. ⏱️ 非阻塞背景線程 (`QThread`) 與進度條
* 大量檔案更名作業移交背景線程執行，避免視窗卡死無回應。
* 狀態列上方配備即時進度條，清晰呈現執行百分比與當前處理進度。
* 背景執行緒與主線程安全同步衝突對話框。

### 7. ⌨️ 便捷鍵盤操作與批次右鍵選單
* 支援多選（`Shift` / `Ctrl` 連選與複選）。
* 右鍵選單可對選取的全部檔案**批次切換**「套用前置詞」與「套用刪除前綴」。
* 鍵盤快捷鍵：`Delete` / `Backspace` 移除選取檔案；`Ctrl+A` 全選；`Ctrl+Z` 復原。

---

## 📂 專案架構

```text
Renamer/
├── main.py                 # 程式啟動進入點
├── Renamer.spec            # PyInstaller 打包設定檔
├── requirements.txt        # 依賴套件清單
├── pyproject.toml          # 現代專案設定與 pytest 配置
├── README.md               # 專案說明文件
├── favicon.ico             # 應用程式圖示
├── core/                   # 核心商務邏輯模組（無 GUI 依賴）
│   ├── __init__.py
│   ├── naming.py           # 檔名運算與補零規則
│   └── operations.py       # 兩階段安全重命名、衝突處理、Rollback、Undo 條目建構
├── ui/                     # PyQt5 使用者介面模組
│   ├── __init__.py
│   ├── app.py              # 主視窗應用程式與互動邏輯
│   ├── widgets.py          # 自訂清單元件、雙欄即時繪製 Delegate、排序與拖放
│   ├── worker.py           # 背景非阻塞更名執行緒 (QThread)
│   ├── preview.py          # 執行前清單預覽對話框
│   └── theme.py            # 深色主題樣式表與調色盤
└── tests/                  # 單元測試集
    ├── __init__.py
    ├── test_naming.py      # 命名規則測試 (24 項)
    ├── test_operations.py  # 重命名、衝突、Rollback、Undo 測試 (15 項)
    └── test_ui.py          # 清單操作、排序、即時預覽更新測試 (7 項)
```

---

## 🚀 快速開始

### 1. 環境需求
* Python 3.10 或以上版本
* 作業系統：Windows 10 / 11

### 2. 安裝依賴
```bash
pip install -r requirements.txt
```

### 3. 執行程式
```bash
python main.py
```

---

## 🧪 執行自動化測試

本專案具備完整的單元測試覆蓋（包含命名演算法、檔案兩階段移動、衝突 Rollback、Undo 復原、檔案排序、UI 即時預覽響應等）：

```bash
pytest -v
```

所有測試皆會於臨時目錄中建立虛擬檔案進行驗證，不會更動本機任何實際檔案。

---

## 📦 打包發行獨立執行檔 (.exe)

本專案已設定好標準的 PyInstaller `.spec` 設定檔，可直接打包為單一雙擊可執行的 Windows 應用程式：

```bash
pyinstaller Renamer.spec
```

打包完成後，可執行檔會產出於 `dist/Renamer.exe`。
