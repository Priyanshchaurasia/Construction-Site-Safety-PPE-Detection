🚧 Blind Spot Human Detection & PPE Monitoring System
📌 Overview

This project is an AI-powered safety monitoring system designed for heavy machinery operating in construction and industrial environments. The system focuses on detecting humans present in the blind zones of heavy machinery, helping reduce the risk of accidents and improving workplace safety.

As an additional safety feature, the system also monitors Personal Protective Equipment (PPE) compliance, such as the use of safety helmets and safety vests.

🎯 Problem Statement

Heavy machinery such as excavators, cranes, and industrial vehicles often have significant blind spots where operators may not be able to see nearby workers.

This project aims to:

Detect humans entering predefined blind-zone/red-zone areas.
Generate safety alerts when a person is detected in a dangerous zone.
Monitor PPE compliance, including helmet and safety vest detection.
Identify safety violations such as No Helmet or No Safety Vest.
Support real-time monitoring for improved industrial and construction site safety.
⚙️ Key Features
👤 Real-Time Human Detection
🚨 Blind Zone / Red Zone Monitoring
🛑 Machine Stop Safety Alert
🦺 Safety Vest Detection
⛑️ Helmet Detection
⚠️ PPE Violation Detection
🎥 Real-Time Video Processing
🤖 Custom YOLO Model Fine-Tuning
🧠 Technologies Used
Technology	Purpose
Python	Core programming language
YOLO	Real-time object detection
Computer Vision	Human and PPE detection
OpenCV	Video processing and visualization
Deep Learning	Model training and inference
Fine-Tuning	Customizing the detection model
Object Detection	Detecting humans and safety equipment
🔄 System Workflow
Camera Feed
     ↓
Video Frame Processing
     ↓
YOLO Object Detection
     ↓
Human Detected?
     ↓
Check Blind Zone
     ↓
🚨 Generate Safety Alert
     ↓
Check PPE Compliance
     ↓
Detect Helmet / Safety Vest Violations
📸 Project Demonstration

The system detects a person entering a designated red/blind zone and identifies PPE violations in real time.

Example Output

PERSON DETECTED → RED ZONE INTRUSION → SAFETY ALERT

The system can also identify violations such as:

❌ No Safety Vest
❌ No Helmet
⚠️ Multiple PPE Violations

Replace images/demo.png with the path to your uploaded screenshot.

🛠️ Project Architecture
                ┌─────────────────┐
                │   Camera Feed   │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │ Video Processing│
                │     OpenCV      │
                └────────┬────────┘
                         ↓
                ┌─────────────────┐
                │   YOLO Model    │
                │ Human + PPE     │
                └────────┬────────┘
                         ↓
          ┌──────────────┴──────────────┐
          ↓                             ↓
 ┌─────────────────┐          ┌─────────────────┐
 │ Blind Zone Check│          │   PPE Analysis  │
 └────────┬────────┘          └────────┬────────┘
          ↓                             ↓
     🚨 Safety Alert              ⚠️ Violation
🚀 Future Improvements
Integration with IoT sensors and industrial cameras
Automatic machine stop mechanism during critical intrusion
Distance estimation between machinery and workers
Multi-camera blind spot coverage
Cloud-based monitoring dashboard
Real-time notifications for supervisors
Edge deployment using devices such as NVIDIA Jetson
🎯 Project Domain

Artificial Intelligence | Computer Vision | Deep Learning | Industrial Safety | Smart Manufacturing

🧩 Key Concepts

YOLO • Computer Vision • Object Detection • Deep Learning • Fine-Tuning • OpenCV • Real-Time Detection • PPE Detection • Blind Spot Detection • Industrial Safety

📌 Impact

By detecting workers in hazardous blind zones and monitoring PPE compliance, this system can contribute to reducing workplace accidents and improving safety around heavy machinery.


## Model Performance
- Base model: YOLOv8n (hardhat detection)
- mAP@0.5: 83.6% (on hard-hat-detection validation set, via keremberke/yolov8n-hard-hat-detection)
- Inference: ~2-8 FPS on CPU (Intel Core 7 150U)
## Dataset
- **Source:** [keremberke/hard-hat-detection](https://huggingface.co/datasets/keremberke/hard-hat-detection) (Roboflow Universe)
- **Size:** ~19,745 images
- **Classes:** 2 (Hardhat, NO-Hardhat)
- **Reported mAP@0.5:** 83.6% on validation split
