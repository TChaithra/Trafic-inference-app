import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter, load_delegate
import os

class YOLOInference:
    def __init__(self, model_path, delegate_path):
        self.model_path = model_path
        self.delegate_path = delegate_path
        self.interpreter = self._load_model()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        # YOLO params (adjust for your model: classes, anchors, etc.)
        self.input_shape = self.input_details[0]['shape']
        self.num_classes = 80  # COCO example; adjust
        self.score_threshold = 0.5
        self.iou_threshold = 0.45

    def _load_model(self):
        interpreter = Interpreter(
            model_path=self.model_path,
            experimental_delegates=[load_delegate(self.delegate_path)]
        )
        interpreter.allocate_tensors()
        return interpreter

    def preprocess(self, image):
        # Resize to model input (e.g., 640x640)
        h, w = image.shape[:2]
        scale = min(self.input_shape[1] / w, self.input_shape[2] / h)
        new_w, new_h = int(w * scale), int(h * scale)
        resized = cv2.resize(image, (new_w, new_h))
        padded = np.zeros((self.input_shape[1], self.input_shape[2], 3), dtype=np.uint8)
        padded[:new_h, :new_w] = resized
        input_data = np.expand_dims(padded.astype(np.float32) / 255.0, axis=0)
        return input_data, (scale, new_w / w, new_h / h)  # Scale factors for postprocess

    def postprocess(self, outputs, orig_shape, scale_info):
        # Simplified YOLO postprocess (adjust for your model's output format)
        # Assume outputs[0]: [1, num_dets, 6] (xyxy, conf, class)
        boxes = outputs[0][0]  # Example
        detections = []
        for box in boxes:
            if box[4] > self.score_threshold:  # conf
                x1, y1, x2, y2 = box[:4]
                # Scale back
                x1, y1 = int(x1 / scale_info[1]), int(y1 / scale_info[2])
                x2, y2 = int(x2 / scale_info[1]), int(y2 / scale_info[2])
                detections.append((x1, y1, x2, y2, box[4], int(box[5])))
        return detections

    def infer(self, image):
        input_data, scale_info = self.preprocess(image)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        outputs = [self.interpreter.get_tensor(detail['index']) for detail in self.output_details]
        detections = self.postprocess(outputs, image.shape[:2], scale_info)
        return detections

    def draw_boxes(self, image, detections, colors=None):
        if colors is None:
            colors = [(0, 255, 0)] * len(detections)  # Green boxes
        for i, (x1, y1, x2, y2, conf, cls) in enumerate(detections):
            cv2.rectangle(image, (x1, y1), (x2, y2), colors[i % len(colors)], 2)
            cv2.putText(image, f'Class {cls}: {conf:.2f}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i % len(colors)], 2)
        return image
