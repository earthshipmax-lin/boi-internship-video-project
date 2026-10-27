# CODEX_PROMPT_14：美國版 60 秒宣傳片 — 初版樣片（含配樂）

> 由 Claude 撰寫，交 Codex 執行。
> **前置閱讀**：`CODEX_PROMPT_13_美版團隊鏡與人物素材.md`（素材與人物鏡規格）、`video/README.md`、`CLAUDE_HANDOFF.md`。
> **本輪目標**：做出一支 **60 秒左右、英文旁白、帶配樂**的初版樣片，供使用者審看。
> 香港版 v12 全部 Composition、音軌、成片**一律不得覆寫**。美國版另建 Composition。
> 使用者已確認：8 秒團隊試片效果不錯，音色 B（`Magnetic-voiced Male`）定案，可沿用。

---

## 0. 使用者需求原文

1. 「接下来也是要做个 60 秒左右的宣传片，给一个能让 codex 使用的提示词吧」
2. 「bgm 这次也要配套了」
3. 「然后看看初版样片如何」

**關鍵詞：初版樣片。** 本輪要的是「能看出全片長什麼樣」的版本，不是定版。畫面可以簡，但**節奏、旁白、配樂三件事必須是真的**，否則看不出效果。

---

## 1. 已有資產（不要重做）

| 項目 | 位置 | 狀態 |
|---|---|---|
| 六張人像（已裁切調色） | `public/portraits/us-v1/*.png` | 已完成，224×280，倍率 ≤1.0 |
| 人像清單與來源雜湊 | `src/config/us-team-v1.json` | 已完成，含前雇主文案 |
| 8 秒團隊鏡 | `src/scenes/USTeamV1.tsx` | 已完成，3 欄×2 列交錯 16px |
| 旁白音色 | MiniMax `speech-2.8-hd` / `Magnetic-voiced Male` | **使用者選定 B，不再試聽** |
| 配音流程 | `scripts/prepare-minimax-us.py` | 已完成，可直接擴充 |
| 已合成旁白 | `public/vo/us-v1/team-b/VO-01.wav`（6.82s） | 已完成 |
| 來源記錄 | `public/vo/us-v1/team-b/VOICE_PROVENANCE.json` | 已完成 |

**本輪要新增的，只有：全片旁白（約 5–6 段）、配樂、其餘鏡頭、60 秒組合。**

---

## 2. 全片結構（60 秒 / 30fps / 1800 幀）

> 以下時長為**設計目標**。實際以旁白合成後的實測長度回推，誤差控制在 ±2 秒內即可。
> **不得為了湊時間而變速旁白**（`playbackRate` 永遠 = 1）。寧可調整鏡長。

| # | 段落 | 時長 | 幀 | 畫面 | 旁白 |
|---|---|---|---|---|---|
| S0 | 開場鉤子 | 4s | 0–120 | 純文字，無 Logo | 「Most people never get a real shot at this business.」 |
| S1 | 這是什麼 | 7s | 120–330 | 城市/桌面靜物（無人臉），文字排版 | 「We're Blue Oak International. A US practice built by people who came from the industry you're already in.」 |
| S2 | 人 | 8s | 330–570 | **沿用 8 秒團隊鏡** | 「Insurance. Banking. Engineering. Twenty years each, on average.」 |
| S3 | 你進來做什麼 | 12s | 570–930 | 三段節點時間軸（非環形） | 「Year one is structured. Licensing, products, and the fundamentals you actually need.」 |
| S4 | 誰帶你 | 10s | 930–1230 | 導師概念（線條／並行軌道） | 「You're not handed a list and left alone. You work alongside partners who've done this before.」 |
| S5 | 你要付出什麼 | 8s | 1230–1470 | 極簡文字，留白 | 「It's not passive. The first year is the hardest one. We're direct about that.」 |
| S6 | 收尾 | 11s | 1470–1800 | 年輪隱喻回歸 + Logo | 「If you've been thinking about this for a while — this is the conversation to have. Blue Oak International.」 |

**S0 是美國版最重要的一鏡。** 香港版前 12 秒是 Logo 生長，美國版前 4 秒必須是「一句話 + 空白」。不要 Logo、不要配樂漸強、不要動效——就是一句白底黑字，停住。

**S5「你要付出什麼」是這一版的原創段落，香港版沒有。** 美國候選人對「只講好處」的招募片高度警惕；主動說難，反而是最強的可信度信號。**不要刪掉這一段。**

---

## 3. 旁白（英文，MiniMax 生成）

### 3.1 語氣基準

沿用已選定的 B 音色，但**整片語氣要比 8 秒團隊鏡更平**：

- 8 秒那段是「介紹」，可以略帶暖意。
- 60 秒這支是「對話」，要像一個人在你對面講話，不是念稿。
- **句尾一律下沉**，不要上揚。上揚會被聽成推銷。
- 不要為了「有力」而加重音。美國觀眾對「刻意強調」極敏感。

### 3.2 合成文字與字幕切分

寫進 `src/config/performance-us-v1.json` 的 `scenes`，沿用現有結構（`text` / `synthesisText` / `subtitleChunks` / `emotions`）。

**停頓用 `<#秒數#>`，英文建議 0.3–0.6s，單處不超過 0.8s。**

參考寫法：

```json
"S0": {
  "text": "Most people never get a real shot at this business.",
  "synthesisText": "Most people never get a real shot at this business.<#0.6#>",
  "subtitleChunks": ["Most people never get a real shot at this business."],
  "emotions": [{"text": "Most people never get a real shot at this business.", "emotion": "Fluent"}]
}
```

**字幕切分按語意單位，不按字數。** 即使本版不上字幕，這欄仍是對齊腳本的計時依據。

### 3.3 合成流程

直接擴充 `scripts/prepare-minimax-us.py`：

- 新增 `S0`–`S6` 各段（`TEAM` 改名或映射到 `S2`，沿用已合成的 `VO-01.wav` 避免重複扣點）。
- Whisper 對齊保持 `language='en'`。
- 輸出到 `public/vo/us-v1/full/`，**不要覆寫** `team-b/`。
- 產出一份新的 `VOICE_PROVENANCE.json`，記錄每段的 credits delta。

> ⚠️ **MiniMax 點數有限**（上次顯示剩 2913）。合成前先列出全部文字與字數，一次算好再跑。若點數不足，先回報，不要中途停在一半。

---

## 4. 配樂（本輪必做）

### 4.1 選曲方向

香港版 `bgm-A.mp3` **不得沿用**（史詩弦樂，在美國招募語境是 infomercial 符號）。`archive/` 裡的 B、C 也未經美國市場驗證，可作為**候選**但不能預設可用。

方向按優先級：

1. **極簡鋼琴 / 單樂器**——一個音一個音走，允許留白。
2. **低頻脈衝電子（minimal pulse）**——有節奏但不煽情。
3. **近乎無配樂**——只留人聲。若配音夠好，這是最有說服力的。

**硬性要求：**

- 無明顯旋律記憶點（觀眾會分心去認曲）。
- **無鼓組重音、無弦樂漸強、無 riser/impact 音效。**
- 授權可商用，並在 `ASSET_ROLES.json` 登記來源。

### 4.2 混音規格

| 項目 | 規格 |
|---|---|
| BGM 相對旁白 | 峰值低 **≥ 12 dB** |
| 旁白段 duck | 降至 **−18 dB**，人聲結束後 **0.5s** 內回復 |
| 剪輯結構 | 沿用 `beats-v11.json` 的 span / crossfade（`crossfade_s: 0.4`），只換素材不改結構 |
| 峰值上限 | 全片 ≤ **−1 dBFS**，預留 headroom |
| 輸出 | WAV 48kHz / 立體聲 |

**S0 開場 4 秒建議完全無配樂**，第一個字出來時才進。這是全片最有效的留白。

**S5「你要付出什麼」的 BGM 要再降一檔**（或短暫全靜），讓那句話裸奔。

### 4.3 若找不到合適授權曲目

**不要用香港版 A 湊數，也不要網上隨手抓。** 改為「無人聲 + 極簡環境音」的版本先出樣片，在 `ASSET_ROLES.json` 標明 `music.status: "pending_licensed_source"`，並在交付說明裡寫清楚。使用者要的是看效果，無配樂版本同樣能判斷節奏。

---

## 5. 其餘鏡頭的製作規格

### 5.1 通用視覺語言（沿用 `video/src/theme.ts`，不新增色票）

- 底色 `paper`：`oklch(97% 0.01 80)`
- 文字 `ink`：`oklch(25% 0.01 60)`
- 點綴 `terracotta`：`oklch(62% 0.13 45)`——**全片只用在年輪線條與一處重點字**
- easing：`theme.ease`（cubic-bezier 0.16, 1, 0.3, 1）
- 字體：標題用 `Source Serif 4`，小字用 `Geist`。**全片不超過 2 種字族。**

### 5.2 S0 開場

- 純白底，一句話居中，Source Serif 4，約 56–64px。
- 入場：`opacity 0→1`，0.5s。**不做打字機效果、不做位移、不做縮放。**
- 停留 2.5s 後淡出。
- **不顯示 Logo。**

### 5.3 S1「這是什麼」

- 可用 `public/stills/` 中既有的城市／桌面素材，**不要人臉**。
- 文字疊加，左下角對齊，兩行以內。
- 若無合適素材，改為純排版 + 一條細線分隔，不要勉強找圖。

### 5.4 S2 團隊鏡

**直接沿用 `USTeamV1.tsx`**，只改兩處：

- 時長由 240 幀改為約 240 幀（8s），起始幀對齊旁白。
- 移除左下角 `INTERNAL VISUAL STUDY / NOT FOR DISTRIBUTION`——改為全片統一的 `INTERNAL REVIEW — NOT FOR DISTRIBUTION`，只在片尾出現一次。

### 5.5 S3「你進來做什麼」

- **橫向三段節點時間軸**，不是香港版的環形年輪。
- 三個節點：`Licensing` → `Products & Process` → `Client Work`。
- 節點依旁白節奏逐個亮起，連線以 `terracotta` 描繪。
- 不做粒子、不做光暈。

### 5.6 S4「誰帶你」

- 抽象表達，**不要 AI 生成人物**。
- 建議：兩條平行線，其中一條由虛線漸變為實線（象徵從跟隨到獨立）。
- 極簡，留白要大。

### 5.7 S5「你要付出什麼」

- **全片最簡的一鏡**：純白底 + 一行字，字比 S0 小。
- 建議文案：`The first year is the hardest one.`
- BGM 在此降至最低或全靜。
- 停留 4s，讓觀眾有時間反應。

### 5.8 S6 收尾

- 年輪母題回歸（與香港版視覺語言呼應，但**只出現 2–3 圈**，不是全片鋪滿）。
- Logo 最後出現，停留 1.5s。
- 片尾小字：`Internal review — not for distribution`，12px，`muted`，opacity ≤0.55。

---

## 6. 反模式（本輪禁止）

- ❌ 全片出現**任何中文**（含標點、標題、片尾）
- ❌ 前 4 秒出現 Logo 或配樂漸強
- ❌ 史詩弦樂、鼓組重音、riser、impact 音效
- ❌ AI 生成人物或修補人臉
- ❌ 為對齊畫面而對旁白變速（`playbackRate ≠ 1`）
- ❌ 任何人像單獨佔滿整屏
- ❌ 收入數字、產品名稱、其他保險公司品牌作為宣傳背書
- ❌ bounce / elastic easing
- ❌ 覆寫香港版任何既有文件或成片

---

## 7. 交付物

1. **主片**：`out/US-Team-v1_60s_初版.mp4`，1920×1080 / 30fps / 約 1800 幀（60s ±2s）
2. **靜幀**：每個段落各一張，`out/` 或 `qa/us-v1-60s/frames/`
3. **QA 目錄**：`qa/us-v1-60s/`，需含
   - `FINAL_QA.md`（逐項自查結果）
   - `timeline.json`（每段起止幀、旁白實測長度）
   - `mix-report.md`（BGM 相對音量、duck 曲線、峰值）
   - `VOICE_PROVENANCE.json`（每段 credits delta）
4. **不得覆寫**：`out/US-Team-v1-visual-study.mp4`、`out/US-Team-v1-B-narrated.mp4`、`public/vo/us-v1/team-b/`

---

## 8. 驗收清單

- [ ] 全片無中文（逐幀抽查標題與片尾）
- [ ] 8 秒團隊鏡為既有版本，未被重做
- [ ] 六張人像渲染倍率仍 ≤1.0
- [ ] 所有旁白 `playbackRate = 1`，Whisper 對齊 `language='en'`
- [ ] BGM 峰值比旁白低 ≥ 12 dB，duck 至 −18 dB
- [ ] S0 前 4 秒無配樂
- [ ] S5 段落 BGM 為最低或全靜
- [ ] 全片峰值 ≤ −1 dBFS
- [ ] 沒有史詩弦樂、鼓組重音、riser
- [ ] 香港版 v12 全部文件與成片未被改動
- [ ] 片尾有 `Internal review — not for distribution`，且全片只出現一次

---

## 9. 待公司確認（Codex 不要自行假設）

1. **肖像授權**：未確認前，本片僅限內部審看，不得對外發布。
2. **旁白文案**：全部為初稿，需公司／合規審閱。
3. **前雇主名稱措辭**：卡片上的 `Formerly at ...` 需合規確認。
4. **配樂授權**：若使用任何外部曲目，必須確認可商用。
5. **美國實體表述**：六位應作為獨立的美國團隊呈現，不可寫成香港團隊的延伸。

---

## 10. 交付後回報

請在 `CLAUDE_HANDOFF.md` 頂部新增一段入口，寫明：

- 主片輸出路徑與實際時長
- 各段旁白實測長度
- 配樂採用情形（已選／待授權／無配樂版）
- 哪些項目仍是內部假設、未經公司確認

**不要把「初版樣片已產出」寫成「已定版」或「已批准」。**
