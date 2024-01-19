"""
A class to initialize the Game state detection model and run prediction on it.

"""

import os
import torch
import numpy as np
from typing import List
from torchvision.transforms import Compose, Lambda, Resize
from pytorchvideo.transforms import Normalize, UniformTemporalSubsample
from transformers import VideoMAEImageProcessor, VideoMAEForVideoClassification

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'


class GameStateDetector:
    def __init__(self, cfg: dict):
        ckpt = cfg['weight']
        print("Initializing model and transforms...")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.feature_extractor = VideoMAEImageProcessor.from_pretrained(ckpt)
        self.model = VideoMAEForVideoClassification.from_pretrained(ckpt).to(self.device)
        self.labels = list(self.model.config.label2id.keys())
        sample_size = self.model.config.num_frames
        mean = self.feature_extractor.image_mean
        resize_to = 224
        std = self.feature_extractor.image_std
        self.label2state = {'service': 1, 'play': 2, 'no-play': 3}
        self.state2label = {1: 'service', 2: 'play', 3: 'no-play'}

        self.transforms = Compose(
            [
                UniformTemporalSubsample(sample_size),
                Lambda(lambda x: x / 255.0),
                Normalize(mean, std),
                Resize((resize_to, resize_to)),
            ]
        )

    def predict(self, frames: List[np.ndarray]) -> int:
        """
        Given the list of frames, it outputs the state of the game.
        Parameters
        ----------
        frames

        Returns
        -------

        """
        video_tensor = torch.tensor(np.array(frames).astype(frames[0].dtype))
        video_tensor = video_tensor.permute(3, 0, 1, 2)  # (num_channels, num_frames, height, width)
        video_tensor_pp = self.transforms(video_tensor)
        video_tensor_pp = video_tensor_pp.permute(1, 0, 2, 3)  # (num_frames, num_channels, height, width)
        video_tensor_pp = video_tensor_pp.unsqueeze(0)
        inputs = {"pixel_values": video_tensor_pp.to(self.device)}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

        softmax_scores = torch.nn.functional.softmax(logits, dim=-1).squeeze(0)
        confidences = {self.labels[i]: float(softmax_scores[i]) for i in range(len(self.labels))}
        label = max(confidences, key=confidences.get)
        return self.label2state[label]
