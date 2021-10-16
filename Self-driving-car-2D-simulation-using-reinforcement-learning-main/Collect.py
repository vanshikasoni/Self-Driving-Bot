# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 11:18:12 2019

@author: VANSHIKA
"""

# Drive in remote control mode
# Take the web cam footage
# Receiving steering information including gas paddle (direction)
# Record all in convinient formate

import os
import math
import numpy as np
import glob
import scipy
import scipy.misc
import datetime
import cv2

import argparse

parser = argparse.ArgumentParser(description='Steer autonomours Car')

parser.add_argument('-n','--num_frames', action = 'store', default=100)

parser.add_argument('-d','--debug', action = 'store_true', default='Flase')

args = parser.parse_args()
num_frames = args.num_frames
debug = args.debug

import serial
from PIL import Image, ImageDraw
import pygame
import pygame.camera
from pygame.locals import *
from VideoCapture import Device
pygame.init()
pygame.camera.init()

#______________________________Initialize the webcam___________________________

print('Initializing webcam')
cams = pygame.camera.list_cameras()
cam = pygame.camera.Camera(cams[0],(64,64),'RGB')
cam.start()  

date = datetime.datetime.now()
time_format = '%Y-%m-%d_%H:%M:%S'
imgs_file = 'imgs_{0}'.format(date.strftime(time_format))
speedx_file = 'speedx_{0}'.format(date.strftime(time_format))
targets_file = 'targets_{0}'.format(date.strftime(time_format))

print('Connect to serial ports')
if not debug:
    ser = serial.Serial('/dev/ttyUSB0')
    if(ser.isOpen == False):
        ser.open()
        
else:
    ser = open('test_collect.csv')
    
#________________________________Drive in RC mode______________________________

imgs = np.zeros((num_frames,3,64,64),dtype = np.uint8)
speedx = np.zeros((num_frames,2),dtype = np.uint8)
targets = np.zeros((num_frames,2),dtype = np.uint8)

idx = 0    
while(True):
    #Take web cam footage every second
    img = pygame.surfarray.array3d(cam.get_image())
    #Squaring the sides
    img = img[20:-20]
    #image resizing
    img = scipy.misc.imresize(img,(64,64),'cubic','RGB').transpose(2,1,0)
    
    #Steering  direction
    if not debug:
        d = ser.readline()
        data = list(map(int,str(d,'ascii').split(',')))
    else:
        d = ser.readline()
        line = d.strip()
        data = list(map(int,line.split(',')))
        
#_____________________________Record data in convinient format_________________
        
    steer = data[0]
    direction = data[1]
    if direction:
        gas = data[2]
    else:
        gas = -1*data[2]
    time = data[3]
    speed = data[4]
    accel = data[5]    

#_____________________________Storing in the form of arrays____________________
    
    imgs[idx] = np.array(img,dtype = np.uint8)
    targets[idx] = np.array([steer,gas],dtype = np.float16)
    speedx[idx] = np.array([speed,accel],dtype = np.float16)
    
    idx = idx + 1
    
    if (idx % num_frames == 0):
        np.savez(imgs_file,imgs)
        np.savez(speedx_file,speedx)
        np.savez(targets_file,targets)
        imgs_file = 'imgs_{0}'.format(date.strftime(time_format))
        speedx_file = 'speedx_{0}'.format(date.strftime(time_format))
        targets_file = 'targets_{0}'.format(date.strftime(time_format))
        
        # To zero out storage
        imgs[:] = 0
        speedx[:] = 0
        targets[:] = 0
        
    time.sleep(1)
        
        
    


