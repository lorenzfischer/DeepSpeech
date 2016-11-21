#!/bin/sh

set -xe

ds_dataset_path="/data/LIUM/"
export ds_dataset_path

ds_importer="ted"
export ds_importer

ds_batch_size=32
export ds_batch_size

ds_training_iters=300
export ds_training_iters

ds_validation_step=50
export ds_validation_step

ds_display_step=50
export ds_display_step

ds_checkpoint_step=50
export ds_checkpoint_step

ds_use_warpctc=1
export ds_use_warpctc

if [ ! -f DeepSpeech.ipynb ]; then
    echo "Please make sure you run this from DeepSpeech's top level directory."
    exit 1
fi;

jupyter-nbconvert --to script DeepSpeech.ipynb --stdout | python -u
