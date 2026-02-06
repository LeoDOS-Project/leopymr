#! /usr/bin/env python3

import glob,os
import math
from deepdespeckling.despeckling import despeckle
from deepdespeckling.utils import utils
import numpy

import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])

import mediapipe as mp
import cv2


def detect(img_name,idx):
  fname = f"data/output{idx}/denoised/denoised_{img_name}.png"
  if not os.path.exists(fname):
    return None
  img = cv2.imread(fname)

  mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
  BaseOptions = mp.tasks.BaseOptions
  ObjectDetector = mp.tasks.vision.ObjectDetector
  ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
  VisionRunningMode = mp.tasks.vision.RunningMode

  options = ObjectDetectorOptions(
    base_options=BaseOptions(model_asset_path='data/ssd_mobilenet_v2.tflite'),
    max_results=1,
    running_mode=VisionRunningMode.IMAGE)

  with ObjectDetector.create_from_options(options) as detector:
    detection_result = detector.detect(mp_image)

  return detection_result.detections[0].categories[0].category_name

class SarCollector:
  def __init__(self):
    self.delimiter = '\n'
  def collect(self,payload):
    data = []
    data_id = payload["meta_data"]["data_id"]
    image_path=f"data/task{data_id}"
    destination_directory=f"data/output{data_id}"
    despeckle(image_path, destination_directory, model_name="sar2sar")

    for file in glob.glob(f"data/task{data_id}/*.tiff"):
      fname = file.split('/')[-1].split('.tiff')[0]
      detected_object =  detect(fname, data_id)
      print(f"DEBUG sarcollect detected {detected_object} in {fname} idx {data_id}")
      yield detected_object

def get_task():
  return SarCollector()



