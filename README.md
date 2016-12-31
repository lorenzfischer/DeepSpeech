# Project DeepSpeech

Project DeepSpeech is an open source Speech-To-Text engine that uses a model trained by machine learning techniques, based on [Baidu's Deep Speech research paper](https://arxiv.org/abs/1412.5567). Project DeepSpeech uses Google's [TensorFlow](https://www.tensorflow.org/) project to facilitate implementation.

## Prerequisites

* [TensorFlow](https://www.tensorflow.org/versions/r0.11/get_started/os_setup.html#download-and-setup)
* [Jupyter/IPython](https://jupyter.org/install.html)
* [SciPy](https://scipy.org/install.html)
* [PyXDG](https://pypi.python.org/pypi/pyxdg)
* [python_speech_features](https://pypi.python.org/pypi/python_speech_features)
* [python sox](https://pypi.python.org/pypi/sox)

## Recommendations

If you have a capable (Nvidia, at least 8GB of VRAM) GPU, it is highly recommended to install TensorFlow with GPU support. Training will likely be significantly quicker than using the CPU.

## Training a model

Open a terminal, change to the directory of the DeepSpeech checkout and run `jupyter-notebook DeepSpeech.ipynb`. This should open your default browser with the DeepSpeech notebook. From here, you can alter any variables with regards to what dataset is used, how many training iterations are run and the default values of the network parameters. Then, to train the network, select `Cell` from the notebook menu bar and choose `Run All`. By default, the notebook will train on a small sample dataset called LDC93S1, which can be easily overfitted on any CPU in a few minutes for demonstration purposes.

You can also use the utility scripts in `bin/` to train on different data sets, but keep in mind that the other speech corpora are *very large*, on the order of tens of gigabytes, and some aren't free. Downloading and preprocessing them can take a very long time, and training on them without a fast GPU (GTX 10 series recommended) takes even longer. If you experience GPU OOM errors while training, try reducing `batch_size`.

## Exporting a model for serving

If the `ds_export_dir` environment variable is set, or the `export_dir` variable is set manually, a model will have been exported to this directory during training. If training has been performed without exporting a model, a model can be exported by setting the variable to the directory you'd like to export to (e.g. `export_dir = os.path.join(checkpoint_dir, 'export')`) and running the model exporting cell manually. If the notebook has been restarted since training, you will need to run all the cells above the training cell first before running the export cell, to declare and initialise the required variables and functions.

Refer to the corresponding [README.md](client/README.md) for information on building and running the client.
