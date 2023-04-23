import os
import pandas as pd
import cv2
import numpy as np
import xml.etree.ElementTree as ET

class CandlestickDataset:

    def __init__(self, csv_path, image_folder, annotation_folder, input_size=(224, 224)):
        self.data = pd.read_csv(csv_path)
        self.input_size = input_size
        self.annotation_path = annotation_folder
        self.image_folder = image_folder

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # img_path = os.path.join(self.image_folder, self.data.iloc[idx]["image_filename"])
        # img = cv2.imread(img_path)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # img = cv2.resize(img, self.input_size)
        # annotation_file = os.path.join(self.annotation_path, os.path.splitext(self.data.iloc[idx]["image_filename"])[0] + ".xml")
        # tree = ET.parse(annotation_file)
        # root = tree.getroot()

        # boxes = []
        # labels = []

        # for obj in root.findall('object'):
        #     label = obj.find('name').text
        #     bndbox = obj.find('bndbox')
        #     x_min = int(float(bndbox.find('xmin').text) * self.input_size[0])
        #     y_min = int(float(bndbox.find('ymin').text) * self.input_size[1])
        #     x_max = int(float(bndbox.find('xmax').text) * self.input_size[0])
        #     y_max = int(float(bndbox.find('ymax').text) * self.input_size[1])

        #     boxes.append([x_min, y_min, x_max, y_max])
        #     labels.append(label)

        # return img, np.array(boxes), np.array(labels)
        
        # Get the binary label (1 if there's a pattern, 0 otherwise)
        row = self.data.iloc[idx]
        img_path = os.path.join(self.image_folder, self.data.iloc[idx]["image_filename"])

        # Load and preprocess the image
        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, self.input_size)
        has_pattern = 1 if row["label"] != "no_pattern" else 0

        return img, has_pattern