from multiprocessing.resource_sharer import stop
import tkinter as tk
import threading
import time
from tkinter import Menu, filedialog
import numpy as np
import pydub
from scipy import signal
import queue
import pyaudio
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
import warnings
matplotlib.use('TkAgg') # set the backend to TkAgg

warnings.filterwarnings("ignore", category=UserWarning) # removes unrequired warnings

##########################################################################################

# global variables to be used in multiple function for intercommunication.
global val, p, p_val, stream, toolbar, playing, plot, prev_plot
val = None
p = None
p_val = None
stream = None
plot = None
toolbar = None
playing = False
prev_plot = None
 
lock = threading.Lock()
thread = None

##########################################################################################

# Defining the frequency bands for the equalizer
bands = [
    {"freq": 30, "label": "30 Hz"},
    {"freq": 60, "label": "60 Hz"},
    {"freq": 120, "label": "120 Hz"},
    {"freq": 270, "label": "270 Hz"},
    {"freq": 520, "label": "520 Hz"},
    {"freq": 1200, "label": "1.2 kHz"},
    {"freq": 2400, "label": "2.4 kHz"},
    {"freq": 4800, "label": "4.8 kHz"},
    {"freq": 9200, "label": "9.2 kHz"},
    {"freq": 12400, "label": "12.4 kHz"},
    {"freq": 16000, "label": "16 kHz"}
]

##########################################################################################

# Initialize the gains for each band to 0
gains = np.zeros(len(bands))

# Defining a function to open an audio file
def open_audio():

    global val, p_val

    file_path = filedialog.askopenfilename()
    if not file_path:
        return
    val = pydub.AudioSegment.from_file(file_path)
    p_val = val
    return

##########################################################################################

# Defining a function to save an audio file
def save_audio(audio):
    save_path = filedialog.asksaveasfilename(defaultextension=".mp3")
    if not save_path:
        return
    audio.export(save_path, format="mp3")

##########################################################################################

# Defining a function to process the selected audio file with the specified gains for each frequency band
def process_audio(audio, q=5): # Q = Qualtiy Factor
    global p_val 

##########################################################################################

    # To Get the audio data as a numpy array
    data = np.frombuffer(audio.raw_data, dtype=np.int16).reshape(-1, audio.channels)

##########################################################################################

    # To Get the audio properties
    sample_rate = audio.frame_rate
    channels = audio.channels
    sample_width = audio.sample_width
    max_val = 2 ** (8 * sample_width - 1)

##########################################################################################

    # Applying a filter for each frequency band using the specified gain
    for i, band in enumerate(bands):
        freq = band["freq"]
        gain = gains[i]

##########################################################################################

        # Calculating the filter coefficients for a peaking filter of order 4
        w0 = 2 * np.pi * freq / sample_rate
        alpha = np.sin(w0) / (2 * q)
        cos_w0 = np.cos(w0)
        cos_2w0 = np.cos(2 * w0)
        b0 = 1 + alpha * (10**(gain / 20))
        b1 = -2 * cos_w0
        b2 = 1 - alpha * (10**(gain / 20))
        a0 = 1 + alpha / (10**(gain / 20))
        a1 = -2 * cos_w0
        a2 = 1 - alpha / (10**(gain / 20))
        a3 = -alpha**2 * cos_2w0 / (2 * 10**(gain / 20))
        a4 = alpha**2 / (2 * 10**(gain / 20))

##########################################################################################

        # Applying the filter to each channel of the audio data
        filtered = np.zeros_like(data)
        for j in range(channels):

            # To genrate a filter response for the given coffecients and filter the input as required
            filtered[:, j] = signal.lfilter([b0, b1, b2, 0, 0], [a0, a1, a2, a3, a4], data[:, j])

            # Clip the filtered values to avoid sound bursting
            filtered[:, j] = np.clip(filtered[:, j], -max_val, max_val - 1)

        data = filtered

##########################################################################################

    # To Convert the processed audio data back to an AudioSegment object
    processed_audio = pydub.AudioSegment(
        data.tobytes(),
        frame_rate=sample_rate,
        sample_width=sample_width,
        channels=channels
    )

    p_val = processed_audio
    return

##########################################################################################

audio_queue = queue.Queue()

# Defining a function to create another thread to run the audio_play function
def play(audio):
    global p, stream, playing

    if not playing:
        playing = True
        thread = threading.Thread(target=play_audio, args=(audio,))
        thread.start()

##########################################################################################

# Defining a function to play audio in real-time      
def play_audio(audio):
    global p, stream, playing, plot

    CHUNK_SIZE = 1024
    SLEEP_INTERVAL = 0.01

    def callback(in_data, frame_count, time_info, status):
        data = audio.raw_data[:frame_count * audio.sample_width * audio.channels]
        audio._data = audio._data[frame_count * audio.sample_width * audio.channels:]
        return (data, pyaudio.paContinue)

    if not p:
        try:
            p = pyaudio.PyAudio()
        except Exception as e:
            print(e)
            playing = False
            return
    if not stream:
        try:
            stream = p.open(format=p.get_format_from_width(audio.sample_width),
                            channels=audio.channels,
                            rate=audio.frame_rate,
                            output=True,
                            stream_callback=callback)
        except Exception as e:
            print(e)
            playing = False
            return

    with stream:
        def stop_play(): # To stop the stream
            global playing
            playing = False

        root.after(int(audio.duration_seconds*1000), stop_play)

        stream.start_stream()

        while playing:
            data = audio.raw_data[:CHUNK_SIZE]
            audio._data = audio._data[CHUNK_SIZE:]
            if not data:
                break
            stream.write(data)
            time.sleep(SLEEP_INTERVAL)

    stream = None
    p = None

##########################################################################################

# defining a function to plot the audio output
def display_audio(audio):
    global fig, canvas, toolbar, prev_plot

    duration = audio.duration_seconds
    rate = audio.frame_rate
    samples = audio.get_array_of_samples()
    times = [t / rate for t in range(len(samples))]
    fig, ax = plt.subplots()
    ax.plot(times, samples)
    ax.set_xlim([0, duration])
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Amplitude')

    if toolbar: # Delete the previous toolbar
        toolbar.destroy()

    if prev_plot:
        prev_plot.get_tk_widget().destroy() # Delete the previous plot

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    
    # To add Interactive functions for graph (Toolbar)
    toolbar = NavigationToolbar2Tk(canvas, root) 
    toolbar.update()
    toolbar.pack()

    prev_plot = canvas

    return canvas

##########################################################################################

# Defining a function to stop the real-time audio
def stop_audio():
    global p, stream, playing
    playing = False
    if stream is not None:
        stream.stop_stream()
        stream.close()
    if p:
        p.terminate()
    p = None
    stream = None

##########################################################################################

# Defining a function to update the gain for a frequency band
def update_gain(i, val):
    gains[i] = float(val)
    print("Updated gain for band {}: {}".format(i+1, val))

##########################################################################################
    
# Initializing the Tkinter GUI
root = tk.Tk()
root.title("Audio Equalizer")

##########################################################################################

# Create a frame to hold the frequency band sliders
slider_frame = tk.Frame(root)
slider_frame.pack(side="left", padx=10, pady=10)

# Create a list to hold the sliders
slider_list = []

# Create a slider for each frequency band
for i, band in enumerate(bands):
    # Create a label for the frequency band
    freq_label = tk.Label(slider_frame, text=band["label"])
    freq_label.grid(row=i, column=0, padx=10, pady=10)

    # Create a slider for the gain of the frequency band
    slider = tk.Scale(
        slider_frame,
        from_=-10,
        to=10,
        resolution=0.1,
        length=200,
        orient="horizontal",
        command=lambda val, i=i: update_gain(i, val)
    )
    slider.grid(row=i, column=1, padx=10, pady=10)
    slider_list.append(slider)

button = tk.Button(slider_frame, text="Process File", command=lambda: process_audio(val))
button.grid(row=i+1, column=1, padx=10, pady=10, sticky="w")

# Create a button to set all sliders to 0
reset_button = tk.Button(slider_frame, text="Reset", command=lambda: [slider.set(0) for slider in slider_list])
reset_button.grid(row=i+1, column=1, padx=10, pady=10, sticky="e")

# set the same width and height for both buttons
button.config(width=12, height=2)
reset_button.config(width=12, height=2)

##########################################################################################

# Creating a intaractive Menu for User
menu = Menu(root)
root.config(menu = menu)

menu1 = Menu(menu, tearoff=0)
menu2 = Menu(menu, tearoff=0)
menu3 = Menu(menu, tearoff=0)
menu.add_cascade(label="File",menu=menu1)
menu1.add_command(label="Open File",command=lambda: open_audio())
menu1.add_command(label="Save File",command=lambda: save_audio(p_val))
menu1.add_command(label="Process File",command=lambda: process_audio(val))
menu.add_cascade(label="Playback",menu=menu2)
menu2.add_command(label="Play",command=lambda: play(p_val))
menu2.add_command(label="Stop",command=stop_audio)
menu.add_cascade(label="Graph",menu=menu3)
menu3.add_command(label="Plot",command=lambda: display_audio(p_val))

##########################################################################################

# Create a frame to hold figure
fig_frame = tk.Frame(root)
fig_frame.pack(side="left", padx=10, pady=10)

if plot is not None:
    plot.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
    plot.configure(width=1000, height=600)

##########################################################################################

# Defining function to close the application when delete window button is pressed (cross right corner)
def exit_app():
    global playing, stream, thread
    
    # set flag to signal the thread to stop running
    playing = False
    
    # stop the audio stream if it's playing
    if stream is not None:
        stream.stop_stream()
        stream.close()
        p.terminate()
    
    # join the thread to wait for it to finish
    if thread is not None:
        thread.join()
    
    # destroy the tkinter window
    root.destroy()

# bind the on_closing function to the WM_DELETE_WINDOW event
root.protocol("WM_DELETE_WINDOW", exit_app)

##########################################################################################

# Marks the end of root mainloop
root.mainloop()

##########################################################################################