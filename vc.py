import socket
import sounddevice as sd
import threading
import numpy as np
import pickle
from SeSP.data.data_handler import data_decoder, data_encoder
import time
import pyaudio

send_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)
recv_sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_UDP)

send_sock.connect(("localhost", 64328))
recv_sock.bind(("localhost", 64328))

def recv_audio():
    chunk = 1024  # Number of frames per buffer

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the audio stream
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        output=True)

    # Start playing the audio
    size = int.from_bytes(recv_sock.recv(8), byteorder='little')
    byte_data = recv_sock.recv(size)
    
    stream.start_stream()
    while len(byte_data) > 0:
        stream.write(byte_data)
        
        size = int.from_bytes(recv_sock.recv(8), byteorder='little')
        byte_data = recv_sock.recv(size)

    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    audio.terminate()
        

def send_audio():
    chunk = 1024  # Number of frames per buffer

    # Initialize PyAudio
    audio = pyaudio.PyAudio()

    # Open the audio stream
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=chunk)

    print("Recording started...")
    while True:
        try:
            data = stream.read(chunk)
            send_sock.send(len(data).to_bytes(byteorder='little', length=8))
            send_sock.send(data)
        except KeyboardInterrupt:
            send_sock.send(bytes([0]*8))
            break

    # Stop and close the audio stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    

recv_thread = threading.Thread(target=recv_audio)
recv_thread.start()
time.sleep(.1)
send_audio()