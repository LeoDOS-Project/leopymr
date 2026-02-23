#! /usr/bin/env python3
import cv2
import torch
from collections import deque
import math
from utils import log

 
# Constants
NUM_FRAMES = 7 # Critical Hyperparameter for Temporal Context
FRAME_WIDTH, FRAME_HEIGHT = 256, 256

#cv2.namedWindow("Display", cv2.WINDOW_AUTOSIZE)

# Delay transformer imports until after imshow is initialized
from transformers import AutoVideoProcessor, VJEPA2ForVideoClassification

# Load model and processor
processor = AutoVideoProcessor.from_pretrained("facebook/vjepa2-vitl-fpc16-256-ssv2")
model = VJEPA2ForVideoClassification.from_pretrained("facebook/vjepa2-vitl-fpc16-256-ssv2").eval()

def preprocess_clip(frames):
  resized = [cv2.resize(f, (FRAME_WIDTH, FRAME_HEIGHT)) for f in frames]
  return processor(resized, return_tensors="pt")

class VJEPACollector:
  def __init__(self):
    self.COMP_SKIP_MAP = True

  def collect(self,payload):
    data_id = payload["meta_data"]["data_id"]
    data_size = payload["meta_data"]["data_size"]
    fname = payload["meta_data"]["job_data"]["filename"]
    cap = cv2.VideoCapture(fname)
    file_size = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    chunk_size = math.ceil(file_size/data_size)
    start_frame = chunk_size * (data_id-1)
    end_frame = start_frame + chunk_size 
    log(f"VJEPACollector fname {fname} id {data_id} size {file_size} start {start_frame} end {end_frame}",context=payload)

    if not cap.isOpened():
      log(f"VJEPACollector fname {fname} cannot open video",context=payload,verbosity=0)
      return

    frame_buffer = deque(maxlen=NUM_FRAMES)
    frame_count = 0
    try:
      current_frame = 0
      while True:
        ret, frame = cap.read()

        if not ret:
            log(f"VJEPACollector fname {fname} failed to read frame",context=payload,verbosity=0)
            break

        current_frame += 1
        if current_frame < start_frame:
          continue
        if current_frame > end_frame:
          break

        frame_count += 1
        frame_buffer.append(frame.copy())

        if len(frame_buffer) == NUM_FRAMES:
            inputs = preprocess_clip(list(frame_buffer))
            with torch.no_grad():
                outputs = model(**inputs)
            logits = outputs.logits
            predicted_label_id = logits.argmax(-1).item()
            label = model.config.id2label[predicted_label_id]
            log(f"VJEPACollector Predicted label {label}",context=payload)
            yield {label:1}
            frame_buffer.clear()
    finally:
      cap.release()

def get_task():
  return VJEPACollector()
