import json
import math
import os
import random
import sys
import time
import uuid

import cv2
import dlib
import paho.mqtt.client as mqtt
import pygame
import pygame.surface
import pygame_gui
import pyttsx3
import requests
import socketio
import socketio.exceptions
import speech_recognition as sr

engine = pyttsx3.init()
engine.say("working download")
engine.runAndWait()
