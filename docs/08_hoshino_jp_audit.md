# Dataset Audit Report

- Source: `D:\.FPGA_7020\BlueArchiveVoice\jp\小鸟游星野`
- Files: 408
- Total duration: 17m 47.7s
- Train-suggested duration: 15m 47.6s
- Review duration: 1m 10.4s
- Excluded duration: 0m 49.6s
- Sample rates: 44100, 48000
- Channels: 1, 2

## Subsets

| Subset | Files | Total | Train Files | Train Duration |
| --- | ---: | ---: | ---: | ---: |
| 临战 | 113 | 6m 40.4s | 82 | 6m 11.1s |
| 泳装 | 80 | 6m 36.1s | 69 | 5m 51.6s |
| 默认 | 215 | 4m 31.1s | 56 | 3m 44.9s |

## Recommendation

- Enough clean-looking audio for direct TTS fine-tuning if transcripts are available.
- Without transcripts, use RVC/SVC-style voice conversion first.

## Notes

- `train` is an automatic suggestion based on file name and duration only.
- Manual listening is still required before final training.
- Files marked `review` may still be useful after deduplication or transcript matching.
