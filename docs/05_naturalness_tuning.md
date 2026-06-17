# Naturalness Tuning

## What The Persona Prompt Is Useful For

The persona prompt is useful as the text-writing layer.

It should be used before TTS generation:

```text
user intent -> persona rewrite -> base TTS -> RVC conversion
```

It does not directly change the RVC model. RVC only converts voice color from an input audio clip. If the base TTS sounds stiff, RVC will usually preserve that stiffness.

## Current API Defaults

The API now uses softer defaults:

- `voice`: `zh-CN-XiaoyiNeural`
- `index_rate`: `0.55`
- `auto_split`: `true`
- `pause_ms`: `180`

For more natural output, try:

```json
{
  "text": "唔嘿，今天也辛苦啦。要是脑袋有点转不动，就先休息五分钟吧。",
  "voice": "zh-CN-XiaoyiNeural",
  "index_rate": 0.5,
  "pause_ms": 260,
  "auto_split": true
}
```

## Why Long Recordings Help Only Partly

Longer recordings can help RVC cover more stable tone, breath, and timbre variation.

They do not teach the model how to read arbitrary text naturally, because RVC has no text input during training.

For true speech rhythm learning, use a direct TTS route such as GPT-SoVITS with transcripts:

```csv
file,text,language
默认/hoshino_lobby_1_new.ogg,老师，今天也辛苦啦,zh
泳装/hoshinoswimsuit_lobby_1.ogg,对应台词,zh
```

## Next Training Improvement

The dataset contains several long clips marked as `review,long_clip`.

Possible next RVC run:

```powershell
python .\scripts\prepare_voice_dataset.py `
  --manifest .\data\processed\manifest.csv `
  --output .\data\processed\rvc_train_with_review `
  --sample-rate 40000 `
  --include-review
```

This will include long clips and reviewed variants. It may improve voice coverage, but it can also add duplicate lines or lower-quality clips. Manual listening is recommended before using it for a second 200-epoch run.

## Practical Recommendation

Short term:

- Keep RVC.
- Use persona rewrite.
- Use auto-split.
- Use lower `index_rate`, usually `0.45` to `0.6`.
- Keep each sentence short and conversational.

Medium term:

- Collect transcripts for the clips.
- Train GPT-SoVITS.
- Use RVC only as an optional final polish, if needed.
