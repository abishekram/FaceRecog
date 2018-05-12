# This is a demo of running face recognition on a Raspberry Pi.
# This program will print out the names of anyone it recognizes to the console.

# To run this, you need a Raspberry Pi 2 (or greater) with face_recognition and
# the picamera[array] module installed.
# You can follow this installation instructions to get your RPi set up:
# https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65
from tkinter import Pack

import face_recognition
import picamera
import numpy as np
from subprocess import call
import os
from os.path import isfile, join, basename
import pickle
from pathlib import Path

# Get a reference to the Raspberry Pi camera.
# If this fails, make sure you have a camera connected to the RPi and that you
# enabled your camera in raspi-config and rebooted first.
camera = picamera.PiCamera()
camera.resolution = (320, 240)
output = np.empty((240, 320, 3), dtype=np.uint8)

# Load a sample picture and learn how to recognize it.
print("Loading known face image(s)")

# Initialize some variables
face_locations = []
face_encodings = []
espeak_cmd = 'espeak -v ta+f3 '

imagesPath = "known"
picklePath = "pickle"

known_face_encodings = []
known_face_names = []


def getImage():
    for f in os.listdir(imagesPath):
        if isfile(join(imagesPath, f)):
            temp_image = face_recognition.load_image_file(join(imagesPath, f))
            pickle_path = basename(f) + ".pickle";
            temp_pickle_file = Path(join(picklePath, pickle_path))
            if temp_pickle_file.is_file():
                print("Pickle file found for : " + pickle_path)
                with open(join(picklePath, pickle_path), 'rb') as read_file:
                    temp_coding = pickle.load(read_file)
            else:
                temp_coding = face_recognition.face_encodings(temp_image)[0]
                with open(join(picklePath, pickle_path), 'wb') as write_file:
                    print("Pickle writing  for : " + pickle_path)
                    pickle.dump(temp_coding, write_file)
            known_face_encodings.append(temp_coding)
            print("Adding  " + (os.path.splitext(f)[0]))
            known_face_names.append(os.path.splitext(f)[0])


getImage()
face_names = []
print(known_face_names)
print("Total no of images Loaded :- {}".format(len(known_face_encodings)))
while True:
    print("Capturing image.")
    # Grab a single frame of video from the RPi camera as a numpy array
    camera.capture(output, format="rgb")

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(output)

    print("Found {} faces in image.".format(len(face_locations)))

    face_encodings = face_recognition.face_encodings(output, face_locations)

    # Loop over each face found in the frame to see if it's someone we know.
    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, 0.5)
        matchedFace = np.where(matches)[0]  # Checking which image is matched
        print("Matches array : {}".format(matches))

        if len(matchedFace) > 0:
            print("Position of found image : {}".format(matchedFace[0]))
            name = str(known_face_names[matchedFace[0]])
            face_names.append(name)
        else:
            face_names.append("Unknown ")

        print("I found :")
        for names in face_names:
            try:
                print("found :" + names)
                cmd = espeak_cmd + names
                call(cmd, shell=True, timeout=10)
            except:
                print()
