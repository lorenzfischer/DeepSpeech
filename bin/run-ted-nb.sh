#!/bin/bash

export ds_importer="ted"
export ds_checkpoint_dir="/mnt/data/ds_checkpoints/$ds_importer"
export ds_export_dir="/mnt/data/ds_models/$ds_importer"
export ds_dataset_path="/mnt/data/datasets/$ds_importer"

export ds_limit_train=1
export ds_limit_dev=1
export ds_limit_test=1

export ds_train_batch_size=1 # 16
export ds_dev_batch_size=1
export ds_test_batch_size=1

export ds_learning_rate=0.001 # 0.0001
export ds_validation_step=1 # 20

export ds_epochs=1
export ds_display_step=1  # 10
export ds_checkpoint_step=1


jupyter-notebook DeepSpeech.ipynb
