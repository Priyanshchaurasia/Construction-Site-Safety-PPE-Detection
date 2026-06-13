---
title: Construction PPE Monitor
emoji: ⛑️
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 5.9.1
app_file: app.py
pinned: false
python_version: 3.11
---
## Model Performance
- Base model: YOLOv8n (hardhat detection)
- mAP@0.5: 83.6% (on hard-hat-detection validation set, via keremberke/yolov8n-hard-hat-detection)
- Inference: ~2-8 FPS on CPU (Intel Core 7 150U)