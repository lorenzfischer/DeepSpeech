#!/bin/bash

ds_checkpoint_dir="/mnt/data/ds_checkpoints"
export ds_checkpoint_dir

ds_dataset_path="/mnt/data/datasets/ted"
export ds_dataset_path

ds_importer="ted"
export ds_importer

ds_batch_size=32
export ds_batch_size

ds_training_iters=15
export ds_training_iters

ds_validation_step=15
export ds_validation_step

jupyter-notebook DeepSpeech.ipynb
