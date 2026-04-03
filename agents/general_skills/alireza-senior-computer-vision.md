---
name: senior-computer-vision
description: "Computer vision engineering -- object detection, segmentation, and production deployment."
---

# Senior Computer Vision Engineer

Production computer vision engineering for object detection, image segmentation, and visual AI deployment. Covers architecture selection, training, optimization (ONNX/TensorRT), and inference serving.

## Key Patterns

- **Architecture by speed need**: real-time (>30 FPS) -> YOLOv8/RT-DETR; high accuracy -> Faster R-CNN/DINO; edge -> YOLOv8n/MobileNet-SSD
- **COCO format as standard**: Use COCO JSON for annotations; convert from VOC/YOLO/LabelMe as needed
- **Optimization path**: PyTorch -> ONNX -> target runtime (TensorRT for NVIDIA, OpenVINO for Intel, CoreML for Apple)
- **Quantization tradeoffs**: FP16 = 50% size, 1.5-2x speed, <0.5% accuracy loss; INT8 = 25% size, 2-4x speed, 1-3% accuracy loss
- **Augmentation essentials**: horizontal flip, scale, brightness/contrast, mosaic (YOLO-style), cutout
- **CNN vs ViT**: CNNs need less data (1K-10K images), train faster; Transformers (DETR/DINO) need 10K+ images but capture global context
- **Key metrics**: mAP@50, mAP@50:95, precision, recall, inference latency (P99)
- **Frameworks**: Ultralytics (YOLO), Detectron2 (Faster/Mask R-CNN), MMDetection, timm (classification)
- **Dataset splits**: <1K images: 70/15/15; 1K-10K: 80/10/10; >10K: 90/5/5

## Quick Reference

### Detection Architectures

| Architecture | Latency | mAP | Best For |
|:------------|:--------|:----|:---------|
| YOLOv8n | 1.2ms | 37.3 | Edge/mobile |
| YOLOv8s | 2.1ms | 44.9 | Balanced |
| YOLOv8m | 4.2ms | 50.2 | General purpose |
| YOLOv8l | 6.8ms | 52.9 | High accuracy |
| YOLOv8x | 10.1ms | 53.9 | Max accuracy |
| RT-DETR-L | 5.3ms | 53.0 | Transformer, no NMS |
| Faster R-CNN R50 | 46ms | 40.2 | Two-stage, high quality |
| DINO-4scale | 85ms | 49.0 | SOTA transformer |

### Segmentation Architectures

| Architecture | Type | Latency | Best For |
|:------------|:-----|:--------|:---------|
| YOLOv8-seg | Instance | 4.5ms | Real-time |
| Mask R-CNN | Instance | 67ms | High-quality masks |
| SAM | Promptable | 50ms | Zero-shot |
| DeepLabV3+ | Semantic | 25ms | Scene parsing |
| SegFormer | Semantic | 15ms | Efficient semantic |

### Optimization Targets

| Metric | Real-time | High Accuracy | Edge |
|:-------|:----------|:-------------|:-----|
| FPS | >30 | >10 | >15 |
| mAP@50 | >0.6 | >0.8 | >0.5 |
| Latency P99 | <50ms | <150ms | <100ms |
| GPU memory | <4GB | <8GB | <2GB |
| Model size | <50MB | <200MB | <20MB |

### Optimization Path by Target

| Deploy Target | Path |
|:-------------|:-----|
| NVIDIA GPU (cloud) | PyTorch -> ONNX -> TensorRT FP16 |
| NVIDIA GPU (edge) | PyTorch -> TensorRT INT8 |
| Intel CPU | PyTorch -> ONNX -> OpenVINO |
| Apple Silicon | PyTorch -> CoreML |
| Generic CPU | PyTorch -> ONNX Runtime |
| Mobile | PyTorch -> TFLite or ONNX Mobile |

### CNN vs Vision Transformer

| Aspect | CNN (YOLO, R-CNN) | ViT (DETR, DINO) |
|:-------|:-----------------|:-----------------|
| Training data | 1K-10K images | 10K-100K+ images |
| Training speed | Fast | Slow |
| Inference speed | Faster | Slower |
| Small objects | Good with FPN | Needs multi-scale |
| Global context | Limited | Excellent |

## When to Use

- Building an object detection or segmentation pipeline from scratch
- Choosing between detection architectures (YOLO vs R-CNN vs DETR)
- Optimizing a trained model for production (ONNX export, quantization, TensorRT)
- Preparing and augmenting a custom dataset for training
- Deploying vision models to edge devices, cloud GPUs, or mobile

## Resources

- [Ultralytics Docs](https://docs.ultralytics.com/)
- [Detectron2](https://github.com/facebookresearch/detectron2)
- [ONNX Runtime](https://onnxruntime.ai/)
