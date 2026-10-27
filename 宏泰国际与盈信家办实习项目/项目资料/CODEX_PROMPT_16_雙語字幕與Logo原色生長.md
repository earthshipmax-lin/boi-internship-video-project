# CODEX_PROMPT_16：雙語字幕 + 官方 Logo 原色 + 生長動效

> 由 Claude 撰寫，交 Codex 執行。
> **前置**：`CODEX_PROMPT_15_美版60秒內容密度版.md`（內容結構仍有效）、`video/README.md`。
> **本輪只做三件事**：中英雙語字幕、Logo 恢復原色、Logo 生長動效。
> **不動**：旁白音檔、段落結構、時間軸總長 1800 幀、已通過的人物鏡。
> 香港版 v12 全部文件不得改動。`out/US-Team-v1_60s_初版.mp4` 與 V2 成片均保留。

---

## 0. 使用者需求

> 「还需要做个中英双语字幕，而且宏泰国际的logo不要改变颜色，同时也要做跟之前一样的生长动效logo」

三件事，逐一處理。**第 2、3 項是現有實作的缺陷，不是新功能**，下面寫明根因。

---

## 1. 先更正一個我上一版的錯誤

`CODEX_PROMPT_15` 第 5.1 節我把「100 億港元」寫成 `one hundred billion`，**錯了十倍**。

實際換算：

| PDF 原文 | 正確英文 | 我上版誤寫 |
|---|---|---|
| 100 億+ 港元 | **ten billion** Hong Kong dollars | ~~one hundred billion~~ |
| 15 億+ 港元 | **one point five billion** Hong Kong dollars | （未寫） |

**V2 已實作的旁白是正確的**（`us-full-v2-timeline.json` 為 `Over ten billion...` / `One point five billion...`），不要因為看到本文檔而回頭改壞。**本輪不動旁白。**

---

## 2. Logo 原色（根因與修法）

### 2.1 為什麼現在是錯的

官方 Logo 共有 5 種填色，全部來自 `src/assets/official-logo-v10.json`：

| 部位 | 原始 fill |
|---|---|
| trunk（樹幹） | `url(#linear-gradient1)` — 漸層 |
| base（底線） | `#004098` |
| chinese（宏泰國際 4 字） | 繼承父層，實際 `#004098` |
| english（BLUE OAK INTERNATIONAL 20 字） | `#004098` |
| leaves（82 片葉） | `#0051a4` / `#007bc7` / `#0093d0` 混用 |

**問題出在這兩行：**

```tsx
// src/scenes/USFilm60V1.tsx:9
// src/scenes/USFilm60V2.tsx:29
fill: node.attrs.fill === 'none' ? 'none' : 'currentColor'
```

這把**所有非 none 的填色一律替換成 `currentColor`**，而外層 `style={{color: ink}}` 是墨色 → 整棵藍色橡樹變成單一深灰。香港版正確，是因為它用了 `OfficialBrandV10.tsx` 裡的 `draw()`，那個函式**保留原 fill**。

### 2.2 修法

**不要自己重寫 `node()`。直接從 `src/components/OfficialBrandV10.tsx` 匯出 `draw()`，或在美國版內複製同一份實作。**

`draw()` 的關鍵行為（必須完整保留）：

1. `attrs.fill === 'url(#linear-gradient1)'` → 改寫成 `url(#${prefix}-trunk-gradient)`，避免與香港版同時掛載時 id 衝突。
2. 其餘 fill **原樣保留**，不碰。
3. 對應的 `<defs>`（`gradient-template` / `trunk-gradient`）必須一起輸出。

**驗收硬指標（用截圖比色，不要憑眼睛）：**

- 取樹幹、一片葉、底線各一點，像素值必須落在原色 ±0（PNG 無損導出後應完全一致）。
- `#004098`、`#0051a4`、`#007bc7`、`#0093d0` 四色必須同時出現。
- 不得出現單色化的樹。

### 2.3 順帶要修的

`USFilm60V2.tsx` 第 177 行 `<svg width="210" height="210" style={{color: ink}}>` 中的 `color` 屬性在改回原色後**不再有作用**，但不要保留誤導性寫法，一併清掉。

---

## 3. Logo 生長動效

### 3.1 現況

- 香港版的生長動效在 `src/components/OfficialBrandV10.tsx`，**完整可用**：底座橫向展開 → 樹幹向上生長 → 6 圈葉片由內向外逐片綻放（共 82 片） → 中文 4 字 + 英文 20 字由中心向兩側展開。
- **美國版完全沒有用它**：S7 只是一組靜態 SVG + 一條 opacity 淡入，所以看起來是「淡出來」而不是「長出來」。

### 3.2 時長衝突（本輪關鍵）

香港版的生長時間軸（`hk.logoTimeline`）：

| 階段 | 起 | 時長 | 完成於 |
|---|---|---|---|
| 底座 | 1.2 | 0.9 | 2.1s |
| 樹幹 | 2.0 | 1.2 | 3.2s |
| 葉片 6 圈 | 3.0 | ringGap .55 × 5 + .5 | 6.25s |
| 字標 | 7.4 | 1.0 | **8.4s** |

但美國版 S7 只有 **7.23 秒**（1583–1800 幀）。**照搬會長不完。**

### 3.3 建議時間軸（美國版專用，不覆蓋香港版）

新增一組 `logoGrowth.us`，**不要改 `hk.logoTimeline`**：

| 階段 | 起 | 時長 | 完成於 |
|---|---|---|---|
| 底座 | 0.60 | 0.65 | 1.25s |
| 樹幹 | 1.10 | 0.90 | 2.00s |
| 葉片 6 圈 | 1.70 | ringGap .38 × 5 + leafDur .34 | 3.94s |
| 字標 | 3.30 | 0.90 | 4.20s |
| 靜止 | 4.20 | — | 至 7.23s |

- 全程 **4.2 秒完成**，餘 **3.03 秒靜止**——美國版需要這個停頓，不要為了「長一點」而拉慢。
- `leafDur` 不得低於 **0.30s**，`ringGap` 不得低於 **0.34s**；低於此值葉片會像同時爆開，失去「一圈一圈長出來」的語義。
- 若仍覺太快，**優先砍 S6（`The first year is the hardest one.` 目前 3.0s）** 挪 1 秒給 S7，**不要拉慢動效**。

### 3.4 實作要求

- 直接複用 `OfficialBrandV10` 的結構（`trunk` / `base` / `canopy > ring-N` / `chinese` / `english` 分組，逐片 `scale` + `opacity`）。
- `prefix` 傳 `'us'`，避免與香港版 gradient id 衝突。
- **不要用 CSS transform-origin 定位**，沿用現有的 `translate/scale/translate` 相對寫法。
- 字標必須**由中心向兩側**展開（現有 clipPath 已實作），不是由左往右。

### 3.5 與收尾其他元素的關係

S7 現有元素：3 圈 terracotta 細環（184/248/312）+ 上方標語 + Logo。處置：

- **3 圈細環保留**，但 opacity 由 .2 降到 **.12**，避免與藍色橡樹搶視覺。
- 標語 `This is the conversation to have.` 提前退場：在 Logo 開始生長（f = S7 起 + 18 幀）時開始淡出，**不要等整套 Logo 長完才退**，否則兩者會重疊。
- 官方 wordmark（宏泰國際 + BLUE OAK INTERNATIONAL）出生長動效後，**原本那行 Source Serif 的 `Blue Oak International.` 文字要刪掉**，否則字標重複。

> ⚠️ 注意：官方字標含「宏泰國際」四個中文字。**這是品牌資產，不是字幕**，保留不算違反「全片無中文」的規則。第 4 節的字幕規則僅適用於字幕軌。

---

## 4. 中英雙語字幕

### 4.1 先說一個前提

我先前建議美國版全片不出中文，理由是中文會讓片子被判定成「給華人看的」。**這個判斷在你要求雙語字幕後需要修正為更精確的版本：**

- 如果受眾是**在美國的華語顧問**（很可能就是你的招募對象），雙語不是問題，而且是必要的——英文建立專業感，中文確保理解。
- 真正要避免的是**中文成為主導視覺**。

**所以本方案：英文為主、中文為輔。** 英文在上、字大；中文在下、字小。若日後要給中文為主的受眾，改一個 config 常數即可對調，不需要重排版。

### 4.2 排版規格（1080p）

| 項目 | 規格 |
|---|---|
| 位置 | 底部居中，`bottom: 64` |
| 英文 | Geist / **28px** / lineHeight 1.4 / `ink` |
| 中文 | Noto Sans TC / **22px** / lineHeight 1.5 / `ink`，opacity .82 |
| 行距 | 英文與中文之間 **6px** |
| 背景 | 無底框（現有香港版用 paper 墊底色，雙語兩行會變成一塊大白板，**不要沿用**） |
| 對齊 | 居中，兩行各自居中 |
| 最大寬度 | 1200px，超出換行 |
| 安全區 | 距底 ≥ 64px；**S3/S4/S5 的內容最低點在 768px，字幕最高點不得高於 880px** |

字體皆已在本機，`NotoSansTC.ttf` 已驗證涵蓋所用字形，不需下載新字體。

### 4.3 中文字幕稿（照此使用，不要自行改寫）

> 英文為旁白原文。中文為翻譯，**用繁體**，與影片品牌一致。

| 段 | 英文（旁白原文） | 中文 |
|---|---|---|
| S0 | Most people never get a real shot at this business. | 大多數人，從未真正得到過踏入這行的機會。 |
| S1 | We're Blue Oak International. Group heritage since nineteen ninety-seven. Hong Kong, and the US. | 我們是 Blue Oak International。集團傳承自 1997 年。立足香港，扎根美國。 |
| S2 | Meet the people behind our US team. Their experience spans insurance, banking, and engineering. | 認識我們美國團隊的核心成員。他們的經驗橫跨保險、銀行與工程領域。 |
| S3 | Over ten billion Hong Kong dollars in premium income for insurers. One point five billion in group commission. Three offices. | 為保險公司帶來逾 100 億港元保費收入。集團佣金收入逾 15 億。三地辦公室。 |
| S4 | Our US carrier standard: A or better. Nine states. Century old carriers. | 美國合作保司標準：A.M. Best A 級或以上。覆蓋九大州份。百年歷史保司。 |
| S5 | Flushing, New York. A Hong Kong broker license. Insurance-service agreements with two banks. Singapore in preparation. | 紐約法拉盛辦公室。香港保險經紀牌照。與兩家銀行簽訂保險服務協議。新加坡籌備中。 |
| S6 | The first year is the hardest one. | 第一年，是最難的一年。 |
| S7 | If you've been thinking about this for a while, this is the conversation to have. Blue Oak International. | 如果你已考慮這件事一段時間，這就是那場該談的對話。Blue Oak International。 |

**數字寫法：** 中文用阿拉伯數字（`100 億`、`15 億`），英文用文字（`ten billion`）。這是行業慣例，不要統一。

### 4.4 切分與時間同步

- **沿用現有 `words` 對齊**（`us-full-v2-timeline.json` 每段已有逐詞時間戳）。
- 每段按句切成 1–3 條 cue，**英文與中文同步進出**，不要各自計時。
- 在 timeline 的每段新增 `subtitleCues: [{en, zh, startWord, endWord}]`，`startWord`/`endWord` 為該 cue 的首尾詞，由現有 `words` 陣列推算幀號（沿用 V2 已有的 `cueFrame` 邏輯，`Math.ceil` 保證不早於發音）。
- **不得**為對齊而改動音檔或 `playbackRate`。

建議切分（以 S3 為例，三個數字各一條 cue）：

```
cue1: "Over ten billion Hong Kong dollars in premium income for insurers."
cue2: "One point five billion in group commission."
cue3: "Three offices."
```

### 4.5 實作

- 新建 `src/components/BilingualCaptions.tsx`，接收 `{scene, cues, primary: 'en'|'zh'}`。
- 在 `USFilm60V2` 的 `AbsoluteFill` 最外層掛一次即可（不要逐鏡頭掛），z-index 高於所有鏡頭內容。
- 字體已由 `src/fonts.ts` 全片載入，不需重複 `loadFont`。
- **S2 人物鏡**現有 CSS hack（`.team-scene > div > div:last-child{display:none!important}`）會隱藏人物鏡自帶的左下角說明文字，**字幕層必須掛在這個 hack 範圍外**，否則會被一起隱藏。

---

## 5. 反模式

- ❌ 用 `currentColor` 或任何單一色覆蓋 Logo
- ❌ 把官方字標換成自己排的 Source Serif 文字
- ❌ 為塞進 7.23 秒而把 `leafDur` 壓到 0.30s 以下
- ❌ 中文字幕比英文字幕大
- ❌ 雙語字幕加白色底框
- ❌ 字幕與 S3/S4/S5 的內容重疊
- ❌ 為對齊字幕而改動音檔或變速
- ❌ 同時掛載兩個 `OfficialBrandV10` 而不改 `prefix`（gradient id 會衝突）

---

## 6. 驗收清單

**Logo**

- [ ] 樹幹、葉片、底線、字標均為官方原色，四種藍同時出現
- [ ] 截圖比色：`#004098` / `#0051a4` / `#007bc7` / `#0093d0` 逐點核對
- [ ] 無任何 `currentColor` 殘留於 Logo 渲染路徑
- [ ] 底座 → 樹幹 → 6 圈葉片 → 字標，依序完成，肉眼可辨「一圈一圈」
- [ ] 字標由中心向兩側展開
- [ ] 動效 4.2s 內完成，片尾靜止 ≥ 2.5s
- [ ] 沒有重複的 `Blue Oak International.` 文字
- [ ] 與香港版同時掛載時 gradient id 不衝突

**字幕**

- [ ] 8 段全部有中英兩行
- [ ] 英文 28px 在上、中文 22px 在下
- [ ] 字幕與 S3/S4/S5 內容無重疊（逐幀檢查最高點）
- [ ] S2 人物鏡字幕可見（未被 CSS hack 隱藏）
- [ ] 中文為繁體，數字用阿拉伯數字
- [ ] 字幕時間與旁白同步，無提前或延遲

**通用**

- [ ] 總長仍為 1800 幀
- [ ] 旁白音檔與 `playbackRate` 未變
- [ ] 香港版 v12 全部文件未改動

---

## 7. 交付

- 新 Composition：`US-Team-v1-60s-V3`（**不覆寫** V1 / V2）
- 主片：`out/US-Team-v1_60s_雙語字幕版.mp4`
- 另出：`out/US-Team-v1_60s_雙語字幕版_無字幕.mp4`（給日後上 YouTube 字幕軌用）
- QA：`qa/us-v1-60s-v3/`
  - `logo-color-check.png`（四個取色點的色值截圖）
  - `logo-growth-frames/`（f=0.6/1.25/2.0/2.6/3.2/3.94/4.2s 各一幀）
  - `caption-safety.md`（每段字幕最高點 vs 內容最低點的像素距離）
  - `FINAL_QA.md`
- `CLAUDE_HANDOFF.md` 頂部加新入口。

---

## 8. 待確認

1. **雙語字幕的受眾假設**：本方案按「英文為主、中文為輔」排版。若實際受眾以中文為主，請告知，改 `primary: 'zh'` 即可對調，不需重做。
2. **中文字幕用繁體還是簡體**：本方案用繁體（與品牌一致）。若美國受眾多為大陸背景，可能需要簡體。
3. **官方字標含「宏泰國際」四字**：這會讓全片出現中文品牌字。若公司要求美國版字標只用英文，需另備一份英文版 Logo，**不可自行刪改官方 SVG**。
4. **肖像授權**：仍未確認，本片僅限內部審看。
