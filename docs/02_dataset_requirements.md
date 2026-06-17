# 训练包要求

## 最理想的数据

- 单人声。
- 无背景音乐。
- 无明显音效。
- 无重叠说话。
- 无强混响。
- 音量稳定。
- 每段都有对应文本。
- 总时长至少 10 分钟，30 分钟以上更稳。

## 可接受的数据

- 少量背景音乐，但人声清楚。
- 少量情绪变化。
- 没有文本标注，但人声干净。
- 总时长 3 到 10 分钟，可以先做 demo。

## 不建议的数据

- BGM 比人声还大。
- 战斗音效、环境音很多。
- 多人同时说话。
- 片段极短，只有零碎语气词。
- 压缩严重或有明显破音。

## 文件放置方式

推荐：

```text
data/raw/training_pack/
  audio/
    xxx.wav
    xxx.mp3
  metadata.csv
```

如果没有标注，也可以只放音频：

```text
data/raw/training_pack/
  xxx.wav
  xxx.mp3
```

## metadata.csv 格式

如果你能拿到文本标注，建议使用：

```csv
file,text,language
audio/000001.wav,你好,zh
audio/000002.wav,おじさん、眠いよ,jp
```

字段说明：

- `file`：相对训练包目录的音频路径。
- `text`：该音频对应台词。
- `language`：`zh`、`jp`、`en` 或 `mixed`。

## 数据体检后会做的事

我会生成：

```text
data/processed/audit_report.md
data/processed/manifest.csv
```

`manifest.csv` 会尽量包含：

```csv
id,source_path,processed_path,duration_sec,sample_rate,language,text,quality_flag
```

## 质量分级

A级：

- 干净单人声。
- 文本准确。
- 2 到 10 秒完整短句。

B级：

- 有轻微背景音。
- 文本基本准确。
- 片段长度可用。

C级：

- 噪声、BGM、混响或截断明显。
- 默认不进入训练集，只作为备选。

## 关键决策

如果 A/B 级音频加起来超过 10 分钟，并且文本标注可用，走直接 TTS 微调。

如果 A/B 级音频超过 5 分钟，但没有文本标注，先走 RVC 音色转换。

如果可用音频少于 3 分钟，先做 zero-shot 或 few-shot 测试，不建议直接投入完整训练。
