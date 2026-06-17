# Resume Soft Training

Status at pause:

- Date: 2026-06-15
- Experiment: `hoshino_soft_rvc_40k_v1`
- Process status: stopped
- Reached in log: around epoch 7
- Saved deployable soft test weight: `assets/weights/hoshino_soft_rvc_40k_v1.pth`
- Saved explicit soft checkpoint: `assets/weights/hoshino_soft_rvc_40k_v1_e1_s92.pth`
- No `e25` checkpoint yet.

Recommended resume command:

```powershell
PowerShell -ExecutionPolicy Bypass -File E:\Codexworkspace\takanashi-hoshino-voice-api\scripts\start_formal_training.ps1 `
  -Experiment hoshino_soft_rvc_40k_v1 `
  -Epochs 200 `
  -BatchSize 4 `
  -SaveEveryEpoch 10
```

Check status:

```powershell
PowerShell -ExecutionPolicy Bypass -File E:\Codexworkspace\takanashi-hoshino-voice-api\scripts\check_training_status.ps1 `
  -Experiment hoshino_soft_rvc_40k_v1
```

After training completes, build the soft index:

```powershell
PowerShell -ExecutionPolicy Bypass -File E:\Codexworkspace\takanashi-hoshino-voice-api\scripts\build_rvc_index.ps1 `
  -Experiment hoshino_soft_rvc_40k_v1
```

Then switch API to:

```text
HOSHINO_RVC_MODEL=hoshino_soft_rvc_40k_v1.pth
HOSHINO_RVC_INDEX=E:\Codexworkspace\external\Retrieval-based-Voice-Conversion-WebUI\assets\indices\<soft-index-file>.index
```
