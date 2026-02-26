#! /usr/bin/env python3

import cv2
import mediapipe as mp
from utils import log
import glob
import os
import math
from deepdespeckling.despeckling import despeckle
from deepdespeckling.utils import utils
import numpy

import torch.serialization

torch.serialization.add_safe_globals([numpy.core.multiarray.scalar,
                                      numpy.dtype,
                                      numpy.dtypes.Float64DType])


def get_array(stream):
    return numpy.asarray(
        bytearray(stream.read()), dtype=numpy.uint8)


def detect(file):
    img = cv2.imdecode(get_array(file), 0)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img)
    BaseOptions = mp.tasks.BaseOptions
    ObjectDetector = mp.tasks.vision.ObjectDetector
    ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = ObjectDetectorOptions(
        base_options=BaseOptions(
            model_asset_path='data/ssd_mobilenet_v2.tflite'),
        max_results=1,
        running_mode=VisionRunningMode.IMAGE)

    with ObjectDetector.create_from_options(options) as detector:
        detection_result = detector.detect(mp_image)

    return detection_result.detections[0].categories[0].category_name


class SarMapper:
    def __init__(self):
        self.delimiter = '\n'

    def run_map(self, payload):
        data_id = payload["meta_data"]["data_id"]
        for fname in payload["data"]:
            log(f"sarmap checking {fname} idx {data_id}", context=payload)
            detected_object = detect(payload["files"][fname])
            log(
                f"sarmap detected {detected_object} in {fname} idx {data_id}",
                context=payload)
            yield {detected_object: 1}


def get_task():
    return SarMapper()
