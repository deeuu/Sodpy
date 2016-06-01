Simple Onset Detection in Python (Sodpy)
==============================================

Sodpy is a simple onset detection library written in pure python. Hopefully this
is useful for learning about onset detection algorithms, parameter tuning with
supporting visualisation and batch processing audio files.

You will need to install version 2.7.* of python and the following modules:
ipython, numpy, scipy, matplotlib, and pysoundfile

For scientific python in Ubuntu you can do:

<code>$ sudo apt-get install python-dev ipython python-numpy python-matplotlib
python-scipy </code>

PySoundFile is necessary for reading and writing audio files:

<code>$ https://github.com/bastibe/PySoundFile.git </code>

The basic GUI lives in the directory <code>interface/</code>; just type:

<code>$ python onsetGUI </code>

Acknowledgments
--------------
GUI and STFT support: https://github.com/MTG/sms-tools

Implementation support: https://github.com/johnglover/modal

Implementation support: https://github.com/MTG/essentia
