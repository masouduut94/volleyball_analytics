import os
import torch
import numpy as np
import pandas as pd
import seaborn as sn
from pathlib import Path
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
from sklearn.metrics import precision_recall_fscore_support, accuracy_score

import pytorchvideo.data
from torchvision.transforms import Compose, Lambda, Resize
from pytorchvideo.transforms import ApplyTransformToKey, UniformTemporalSubsample, Normalize
from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor, TrainingArguments, Trainer

# https://pytorch.org/hub/facebookresearch_pytorchvideo_x3d/
# https://github.com/OpenGVLab/VideoMAEv2
# https://github.com/daniel-code/TubeViT
# https://github.com/opengvlab/internvideo


def compute_metrics(pred):
    """Computes accuracy on a batch of predictions."""
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='macro')
    acc = accuracy_score(labels, preds)

    predictions = np.argmax(pred.predictions, axis=1)

    # confusion matrix
    labels = class_labels
    cm = confusion_matrix(pred.label_ids, predictions)
    df_cfm = pd.DataFrame(cm, index=labels, columns=labels)
    plt.figure(figsize=(10, 7))
    cfm_plot = sn.heatmap(df_cfm, annot=True, cmap='Blues', fmt='g')
    cfm_plot.figure.savefig("confusion_matrix_model.jpg")

    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }


def collate_fn(examples):
    """The collation function to be used by `Trainer` to prepare data batches."""
    # permute to (num_frames, num_channels, height, width)
    pixel_values = torch.stack(
        [example["video"].permute(1, 0, 2, 3) for example in examples]
    )
    labels = torch.tensor([example["label"] for example in examples])
    return {"pixel_values": pixel_values, "labels": labels}


if __name__ == '__main__':
    batch_size = 8
    model_ckpt = "MCG-NJU/videomae-base-finetuned-kinetics"
    data_path = '/home/masoud/Desktop/projects/volleyball_analytics/data/processed/game-status'

    dataset_root_path = Path(data_path)
    train_files = list(dataset_root_path.glob("train/*/*.mp4"))
    test_files = list(dataset_root_path.glob("test/*/*.mp4"))
    # val_files = list(dataset_root_path.glob("test/*/*.mp4"))

    video_count_train = len(train_files)
    video_count_val = len(test_files)
    # video_count_test = len(val_files)

    video_total = video_count_train + video_count_val
    print(f"Total videos: {video_total}")

    all_video_file_paths = train_files + test_files

    class_labels = sorted({path.parent.stem for path in all_video_file_paths})
    label2id = {label: i for i, label in enumerate(class_labels)}
    id2label = {i: label for label, i in label2id.items()}

    print("class_labels: ", class_labels)

    feature_extractor = VideoMAEImageProcessor.from_pretrained(model_ckpt)
    model = VideoMAEForVideoClassification.from_pretrained(
        model_ckpt,
        label2id=label2id,
        id2label=id2label,
        ignore_mismatched_sizes=True,
    )

    mean = feature_extractor.image_mean
    std = feature_extractor.image_std
    resize_to = (224, 224)

    num_frames_to_sample = model.parse_args.num_frames
    sample_rate = 3
    fps = 30
    clip_duration = num_frames_to_sample * sample_rate / fps
    print("clip_duration", clip_duration)

    # Training dataset transformations.
    train_transform = Compose(
        [
            ApplyTransformToKey(
                key="video",
                transform=Compose(
                    [
                        UniformTemporalSubsample(num_frames_to_sample),
                        Lambda(lambda x: x / 255.0),
                        Normalize(mean, std),
                        Resize(resize_to)
                    ]
                ),
            ),
        ]
    )

    # Validation and evaluation datasets' transformations.
    val_transform = Compose(
        [
            ApplyTransformToKey(
                key="video",
                transform=Compose(
                    [
                        UniformTemporalSubsample(num_frames_to_sample),
                        Lambda(lambda x: x / 255.0),
                        Normalize(mean, std),
                        Resize(resize_to),
                    ]
                ),
            ),
        ]
    )

    # Training dataset.
    train_dataset = pytorchvideo.data.Ucf101(
        data_path=os.path.join(dataset_root_path, "train"),
        clip_sampler=pytorchvideo.data.make_clip_sampler("random", clip_duration),
        decode_audio=False,
        transform=train_transform,
    )

    test_dataset = pytorchvideo.data.Ucf101(
        data_path=os.path.join(dataset_root_path, "test"),
        clip_sampler=pytorchvideo.data.make_clip_sampler("uniform", clip_duration),
        decode_audio=False,
        transform=val_transform,
    )

    new_model_name = "triple"
    num_epochs = 3

    args = TrainingArguments(
        new_model_name,
        remove_unused_columns=False,
        evaluation_strategy="epoch",
        save_strategy="epoch",
        learning_rate=5e-5,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        warmup_ratio=0.1,
        logging_steps=100,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        push_to_hub=False,
        max_steps=(train_dataset.num_videos // batch_size) * num_epochs,
        fp16=True,
        # optim="adamw_bnb_8bit"
    )

    trainer = Trainer(
        model,
        args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        tokenizer=feature_extractor,
        compute_metrics=compute_metrics,
        data_collator=collate_fn,
    )

    # start training
    train_results = trainer.train()
    # save model
    trainer.save_model()

    # final evaluation on test data
    test_results = trainer.evaluate(test_dataset)
    print("test_results", test_results)
    trainer.log_metrics("test", test_results)
    trainer.save_metrics("test", test_results)
    trainer.save_state()
