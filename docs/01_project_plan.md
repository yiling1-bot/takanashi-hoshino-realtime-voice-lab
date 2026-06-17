# 项目规划

## 目标

建立一个本地接口服务：

- 输入：文本，例如 `你好`。
- 输出：目标音色的 `.wav` 或 `.mp3` 音频。
- 形式：HTTP API，优先使用 FastAPI。
- 运行方式：本地服务，后续可以封装为命令行或桌面调用。

## 技术路线判断

训练包到位后先做数据体检，然后按条件选择路线。

### 路线 A：GPT-SoVITS 直接 TTS 微调

优先选择这条路线。

适用条件：

- 有 1 分钟以上清晰单人声数据。
- 最好有 10 到 30 分钟以上高质量片段。
- 能整理出音频片段与文本的对应关系。
- 目标是让接口直接从文本生成目标音色。

接口流程：

```text
text -> text normalization -> GPT-SoVITS inference -> wav/mp3 response
```

风险：

- 如果训练包里背景音乐、混响、重叠人声太多，音色相似度和清晰度会下降。
- 如果文本标注不准，中文输入的发音稳定性会受影响。

### 路线 B：基础 TTS + RVC 音色转换

当训练包缺少文本标注时使用。

适用条件：

- 有较干净的人声音频。
- 没有准确逐句文本。
- 需要先快速做出可调用 demo。

接口流程：

```text
text -> base TTS wav -> RVC voice conversion -> wav/mp3 response
```

风险：

- 语气和节奏主要来自基础 TTS。
- 对中文、日文混合文本需要额外做分词和发音控制。

## 阶段计划

### 阶段 0：训练包接收

把训练包放入：

```text
data/raw/training_pack/
```

原始文件只读保留，不直接覆盖。

### 阶段 1：数据体检

检查内容：

- 总时长。
- 音频格式、采样率、声道数。
- 是否含 BGM、音效、混响、多人声。
- 是否有文本标注。
- 每段长度分布。
- 静音、爆音、截断、音量过低等问题。

产物：

```text
data/processed/audit_report.md
data/processed/manifest.csv
```

### 阶段 2：数据清洗

处理内容：

- 转为统一采样率和单声道。
- 切分为短句片段。
- 去除长静音、杂音严重片段和重叠人声。
- 统一响度。
- 如有必要，先做人声分离。

推荐片段长度：

- 单句 2 到 10 秒。
- 尽量不要超过 15 秒。
- 不保留明显 BGM 或战斗音效片段。

### 阶段 3：标注整理

如果走直接 TTS 微调，需要：

```csv
audio_path,text,language,notes
```

示例：

```csv
data/processed/wavs/000001.wav,你好,zh,
data/processed/wavs/000002.wav,おじさん、眠いよ,jp,
```

如果只有音频、没有文本，则先走路线 B。

### 阶段 4：训练

路线 A：

- 使用 GPT-SoVITS 做少样本微调。
- 优先生成中文测试句：`你好`、`今天有点累呢`。
- 再测试日文和中日混合句。

路线 B：

- 使用 RVC 训练音色转换模型。
- 接入一个基础中文 TTS 模型生成中间音频。
- 再通过 RVC 输出目标音色。

### 阶段 5：接口封装

接口服务初版：

```text
POST /api/v1/tts
```

输入：

```json
{
  "text": "你好",
  "language": "zh",
  "format": "wav",
  "speed": 1.0
}
```

输出：

- 默认返回 `audio/wav`。
- 可选返回 JSON，包含生成文件路径和耗时。

### 阶段 6：质量验证

最小测试集：

- `你好`
- `今天有点累呢`
- `老师，要一起休息一下吗`
- `おじさん、眠いよ`
- `今日はいい天気ですね`

检查项：

- 发音是否正确。
- 是否有机械音、爆音、吞字。
- 音色相似度是否稳定。
- 生成速度是否能接受。

## 需要你提供的信息

训练包到位后，请告诉我：

- 训练包路径或是否已放入 `data/raw/training_pack/`。
- 总时长大概多少分钟。
- 音频主要是中文、日文，还是混合。
- 是否有逐句文本标注。
- 是否含 BGM、音效、多人声。
- 你的显卡型号和显存大小。

## 外部项目参考

- GPT-SoVITS: https://github.com/RVC-Boss/GPT-SoVITS
- RVC WebUI: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI
- RVC library/API direction: https://github.com/RVC-Project/Retrieval-based-Voice-Conversion
