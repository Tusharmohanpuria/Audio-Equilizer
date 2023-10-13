# Audio Equalizer

**By Tushar Mohanpuria**

## Table of Contents
1. [Introduction](#introduction)
2. [Definitions](#definitions)
3. [Implementation](#implementation)
4. [Working](#working)
5. [Code](#code)
6. [Results](#results)
7. [Conclusion](#conclusion)
8. [References](#references)

## Introduction

The aim of this project is to create a simple audio equalizer application. This application allows users to open an audio file, adjust the gains for different frequency bands, and save the processed audio to a file. Additionally, it can play and plot the processed audio.

## Definitions

### Peaking Filter
A peaking filter is used in audio processing to boost or attenuate a specific frequency range while maintaining a relatively flat response at other frequencies. It's called "peaking" because it has a peak or dip at the center frequency being boosted or attenuated. The filter's Q factor determines the width of the frequency range affected.

### Clipping
Clipping occurs when the amplitude of a signal exceeds the system's maximum possible value, leading to distortion. It's crucial to prevent clipping in audio processing.

### Filter
A filter is a device used to selectively modify, attenuate, or amplify specific components of a signal while leaving other components unchanged. Filters include low-pass, high-pass, band-pass, band-stop, notch, and all-pass filters.

### Peaking Equalizers
A peaking equalizer provides a boost or cut near a center frequency. The analog transfer function for a peak filter is described, and the bilinear transform is used to convert it into digital form.

### Weiner Filter
The Wiener filter reduces noise in a signal, assuming the noise is additive, Gaussian, and uncorrelated with the signal. It estimates the power spectrum of the signal and noise to minimize the mean square error between the original and filtered signals.

## Implementation

The software is created in Python and uses the Tkinter library for the graphical user interface (GUI). It allows users to open and process audio files. The code uses the PyDub, SciPy, NumPy, and Matplotlib libraries for audio processing and visualization.

## Working

The application defines functions for opening and saving audio files, processing audio data, playing audio in real-time, and plotting the audio. It uses sliders to control gains for each frequency band, making it easy to customize audio processing.

## Code

The code for the Audio Equalizer is provided in the repository. It uses PyDub for audio handling, SciPy for filtering, NumPy for data manipulation, and Matplotlib for plotting.

## Results

The repository includes input and output examples, showing the effects of different gain settings on audio quality. The output demonstrates the impact of clipping and noise in the processed audio.

## Conclusion

In conclusion, the project successfully implements a simple audio equalizer using Python libraries. However, some noise and clipping issues may arise when using extreme gain settings or processing audio with many channels.

## References

- [Stanford CCRMA](https://ccrma.stanford.edu/)
- [GeeksforGeeks](https://www.geeksforgeeks.org/)
- [TutorialsPoint](https://www.tutorialspoint.com/)
- "Digital Signal Processing: A Computer-Based Approach," Tata McGraw Hill
