# 給 Codex 的提示詞 02：建立 60 秒香港版影片工程（Remotion）

你是一名資深 Creative Developer 與 Motion Designer。請把已經通過用戶確認的 Logo 片頭原型，延伸成一條完整的 60 秒影片工程。

## 必讀檔案（工作目錄為本資料夾）
1. `BOI_60s_文案_繁中_v1.md`：旁白、分段腳本 S0–S7、字體、色彩、無實拍素材原則。**這是內容的唯一依據，不得自行增改文案。**
2. `prototype/logo-reveal/index.html`、`boi_tree_rebuild_v2.svg`、`wordmark-clean.svg`、`校正說明.md`：已確認的 Logo 片頭（S0）。字標以 `wordmark-clean.svg`（乾淨重建版，已內嵌於 index.html）為準，不要使用舊的描摹版。
3. `CLAUDE_HANDOFF.md`：已有約束。

## 任務

### 1. 建立工程
- 在 `video/` 建立 Remotion + React + TypeScript 工程，鎖定依賴版本。
- Composition：`BOI-HK-60s`，1920×1080，30fps，1800 幀；另建 `BOI-HK-Logo`（只有 S0，360 幀）方便單獨審片。
- 字體：從 Google Fonts 下載 Noto Serif TC、Noto Sans TC、Source Serif 4、Geist 放進 `video/public/fonts/`，用 `@remotion/fonts` 或 `FontFace` 載入，渲染前等待字體就緒。不要依賴系統字體。

### 2. 移植 S0 Logo 片頭（00:00–00:12）
- 把原型的樹形（69 片葉、6 層、`#base` / `#trunk` / `#canopy > #ring-N` 結構）和時間線 `T` 搬成 React 元件，動畫改用 `useCurrentFrame()` 計算，**不用 requestAnimationFrame**。
- 視覺必須和原型 `?t=任意秒數` 的畫面一致：同時間點抽幀對比原型截圖，確認無差異。
- 字標的「從中間向外揭示」保留。
- 原型結尾停在完整 Logo；影片需要轉場到 S1：在 10.2–12 秒，以樹冠的同心弧為起點，陶土色細線一圈圈向外擴散，Logo 淡出，畫面過渡到 S1。只用細線，不加光暈、粒子。

### 3. 製作 S1–S7（00:12–01:00）
- 每段一個元件，時間、字幕、畫面說明完全按文案檔第二節表格。
- 畫面以動態圖形為主：大字排版、同心年輪線、極簡圖示、香港天際線線稿（自行用 SVG 繪製簡潔線稿，不使用他人圖片）、Q1–Q4 環形時間線（每說一季多長出一圈）。
- 需要 AI 影片的鏡頭（S1 維港、S2 可選靜物）先放**佔位畫面**：暖灰底 + 文字標註「AI 影片佔位：鏡頭說明」，並預留 `video/public/footage/S1.mp4` 等檔名，有檔案時自動替換。
- S7 收尾回到完整 Logo，最後靜止 1 秒。

### 4. 參數化
- 所有文案、字幕、時間點、配音檔名放在 `video/src/config/hk.ts`，元件不寫死文字，為之後內地版、美國版預留同結構設定檔（只建 hk）。
- 色彩、字級（1.333 比例）、間距（8px 系統）、緩動 `cubic-bezier(0.16, 1, 0.3, 1)` 放在 `video/src/theme.ts`。

### 5. 配音對齊
- 預留 `video/public/vo/hk/VO-01.wav` … `VO-07.wav`。有檔案時，按檔案實際長度排布字幕；沒有檔案時用文案檔的預估時間，並在畫面角落顯示「無配音」。
- 預留 `video/public/music/bgm.wav`，音量可調，配音出現時自動壓低。

## 禁止
- 不用 AI 生成或修改 Logo；不改樹形與字標形狀。
- 不生成任何人物、人臉；不出現收入數字、保險產品或保險公司名稱。
- 不加光暈、陰影、粒子、金色、科技藍線、bounce/elastic 緩動、超過 600ms 的微動效。
- 不自行修改文案。

## 驗收與交付
- `npx remotion studio` 可預覽；`npx remotion render BOI-HK-60s out/BOI-HK-60s_v1.mp4` 可輸出（H.264，1080p）。
- 每段抽 1 張關鍵幀放在 `video/qa/`（S0–S7 共 8 張），另附 S0 與原型同時間點的對比圖。
- 寫 `video/README.md`：如何預覽、如何替換配音／AI 影片／音樂、如何輸出 4K。
- 列出所有佔位內容與未完成項。
