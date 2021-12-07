import numpy as np
import sys

# camera libraries
from pypylon import pylon
from pypylon import genicam
# signal handling for grace full shutdown
import signal
# time
import datetime
# include
from includes.dotdict import dotdict
from includes.MemMap import MemMap
import configparser
import sys
import time
import os
import psutil

# set the priority for this process
#psutil.Process(os.getpid()).nice(psutil.HIGH_PRIORITY_CLASS)
time.sleep(5)
config = configparser.ConfigParser()
config.read(sys.argv[1])#sys.argv[1]

# extern trigger
#ext_trigger= False

# setup ctrl + c handler
run = True
def signal_handler(sig, frame):
    global run  # we need to have this as global to work
    print("Ctrl+C received")
    print("Shutting down PylonStreamer ...")
    run = False
signal.signal(signal.SIGINT, signal_handler)

# TODO: add codes for color cameras!
fmt2depth = {'Mono8': 8,
             'Mono12': 12,
             'Mono12p': 12}

transpose_image = config["camera"]["transpose_image"] == "True"
flip_x = config["camera"]["flip_x"] == "False"
flip_y = config["camera"]["flip_y"] == "True"
slave = config["camera"]["slave"] == "True"

#externel Trigger 2 slaves
#if ext_trigger == True:
#    slave = True
#print("slave", slave)
#print(transpose_image)
""" PARAMETER """
# select the correct camera mmap cfg here
#output_mmap = "cfg/camera_acA5472-17um.xml"
#output_mmap = "cfg/camera_acA4112-30um.xml"
output_mmap = config["camera"]["output_mmap"]
settings_mmap = config["camera"]["settings_mmap"]

serial_number = config["camera"]["serial_number"]
info = pylon.DeviceInfo()
info.SetSerialNumber(serial_number)
# Setup USB Camera access via Pylon
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice(info))
camera.RegisterConfiguration(pylon.ConfigurationEventHandler(), pylon.RegistrationMode_ReplaceAll, pylon.Cleanup_Delete)
camera.Open()
camera.AcquisitionMode.SetValue("Continuous")
#camera.AcquisitionStart.Execute()
# activate chunkmode for frame timestamps, gain and exposure values
camera.ChunkModeActive = True
camera.ChunkSelector = "Timestamp"
camera.ChunkEnable = True
camera.ChunkSelector = "Gain"
camera.ChunkEnable = True
camera.ChunkSelector = "ExposureTime"
camera.ChunkEnable = True




# set camera parameters for Exposure and Gain control
# camera.ExposureAuto = "Continuous"
# TODO we need to expose these values if we want to change them during runtime
#camera.AutoExposureTimeLowerLimit = 30.0     # micro seconds
#camera.AutoExposureTimeUpperLimit = 1800     # micro seconds
camera.ExposureAuto = "Off"
camera.AutoTargetBrightness = 0.5
#slave = config["camera"]["slave"]
#camera.GainAuto = "Off"
# if slave is False:
#     #print(slave)
#     camera.GainAuto = "Continuous"
#     camera.AutoGainLowerLimit = 0
#     camera.AutoGainUpperLimit = 36
# else:
#     #print(slave)
#     camera.GainAuto = "Off"
#camera.Gain.SetValue(10)


#camera.ExposureTime = 1000

# init memmory map output
mmap = MemMap(output_mmap)
smap = MemMap(settings_mmap)
# start continious acquisition, default as Freerun

ext_trigger = smap.ext_trigger
print(ext_trigger, type(ext_trigger))
#externel Trigger 2 slaves
if ext_trigger == True:
    slave = True
if ext_trigger == True:
    camera.AcquisitionFrameRateEnable = False
else:
    camera.AcquisitionFrameRateEnable = True
    camera.AcquisitionFrameRate = 500

#slave = config["camera"]["slave"]
#print(slave)
#line1 as input
camera.MaxNumBuffer = 15
camera.LineSelector.SetValue("Line3")
camera.LineMode.SetValue("Input") #master stops triggering
if slave is True:
    print("slave")
# Set the line mode to Input
    camera.LineMode.SetValue("Input")
# Get the current line mode
    #e = camera.LineMode.GetValue()
    e = camera.TriggerMode.GetValue()
    print(e)
#Trigger
    camera.TriggerSelector.SetValue("FrameStart")
    camera.TriggerMode.SetValue("On")
#camera.TriggerDelay.SetValue(30)
    camera.ExposureMode.SetValue("Timed")
    camera.TriggerActivation.SetValue("RisingEdge")
    camera.TriggerSource.SetValue("Line3")
    camera.PixelFormat.SetValue('Mono8')

#camera.AcquisitionBurstFrameCount.SetValue(200)
    camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
    #camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
else:
    #print(slave, "master")
    time.sleep(1)
    camera.LineMode.SetValue("Output")
    # Set the source signal to User Output 1
    camera.LineSource.SetValue("ExposureActive")
    camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
    #camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
#camera.StartGrabbing(pylon.GrabStrategy_OneByOne)
#camera.OutputQueueSize = 2
#camera.StartGrabbing(pylon.GrabStrategy_LatestImages)

while not camera.IsGrabbing():
    print('waiting for camera to start')

if (smap.framerate)>0:
    framerate = float(smap.framerate)
else:
    framerate = camera.ResultingFrameRate.Value
    smap.framerate = framerate
camera.AcquisitionFrameRate = framerate
#else:
#    framerate = 500
#target_framerate = framerate
#camera.AcquisitionFrameRate = framerate #500

#smap.exposuretime=30
#print(smap.exposuretime)

exposuretime = float(smap.exposuretime)
camera.ExposureTime.SetValue(exposuretime)
#camera.GainAuto = "Off"
gain = float(smap.gain)
#print(gain)
if gain > 36:
    notauto = False
    #camera.Gain.SetValue(30)
    camera.GainAuto = "Continuous"
    camera.AutoGainLowerLimit = 0
    camera.AutoGainUpperLimit = 36
else:
    notauto = True
    camera.GainAuto = "Off"
    camera.Gain.SetValue(gain)
# if slave is True:
#     gain = float(smap.gain)
#     camera.Gain.SetValue(gain)
timings = []
counter = 0
dropped_counter = 0
slot = 0
##gain = 0
run = True
index  = 0
last_exposuretime = None
last_framerate = None
last_gain = None
buffer_size = len(mmap.rbf)
#recording_index = 0
#burst_frames = 2

if serial_number == str(40061901):
    print(serial_number)
    file = open("timestamp_Slave.txt","w")
    filesk = open("skipped_40061901.txt","w")
else:
    print(serial_number)
    file = open("timestamp_Master.txt", "w")
    filesk = open("skipped_40053148.txt", "w")
skipped_total = 0
failed_buffer=0
failed = 0
fail = 0
while camera.IsGrabbing() and run:
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    #camera.AcquisitionStart.Execute()
    #camera.AcquisitionStatusSelector.SetValue("FrameTriggerWait")
    #print(camera.AcquisitionStatus.GetValue())
    if grabResult.GrabSucceeded():
        #recording_index += 1
        TimeStampCam = grabResult.GetTimeStamp()
        #if index == 0:
            #print(TimeStampCam)
        image = grabResult.Array

        #if recording_index % int(np.round(camera.ResultingFrameRate.Value / target_framerate)) >= burst_frames:
        #    continue
        index += 1
        slot = (slot+1) % buffer_size

        if transpose_image is True:
            image = image.T
        if flip_y is True:
            image = image[::-1, ::]
        if flip_x is True:
            image = image[:, ::-1]
        skipped = grabResult.GetNumberOfSkippedImages()
        wait = camera.GetGrabResultWaitObject().Wait(0)
        #if index == 1:
        #    skipped_first = skipped
        #    print(skipped_first)
        #else:
        skipped_total = skipped_total + skipped
        mmap.rbf[slot].image[:, :, :] = image[:,:,None]
        mmap.rbf[slot].time_unix = TimeStampCam//1000000000  # floor to remove microseconds
        mmap.rbf[slot].time_us   = TimeStampCam//1000 % 1000000 # microseconds timestamp
        mmap.rbf[slot].timestamp = TimeStampCam//1000000
        mmap.rbf[slot].counter = index
        mmap.rbf[slot].skip = skipped
        mmap.rbf[slot].skip_total = skipped_total
        file.write(str(index) + "," + str(TimeStampCam) +  "," + str(failed_buffer) + "," + str(failed) + "," + str(fail) + "\n")
        #print(type(skipped), skipped)
        # if skipped != 0 and index:
        #     print("hello", skipped)
        #     for i in range(skipped):
        #         index = index + 1
        #         print(index)
        #         mmap.rbf[slot].image[:, :, :] = image[:, :, None]
        #         mmap.rbf[slot].time_unix = TimeStampCam // 1000000000  # floor to remove microseconds
        #         mmap.rbf[slot].time_us = TimeStampCam // 1000 % 1000000  # microseconds timestamp
        #         mmap.rbf[slot].counter = index
        #         file.write(str(index) + "," + str(TimeStampCam) + "," + str(skipped) + "\n")

        #if index ==100:
        #    print(TimeStampCam)


        if index % framerate == 0:
            ##gain = grabResult.ChunkGain.Value
            ##smap.gain = gain
            #gain = camera.Gain.GetValue()
            # only set the framerate if it is different

            #if slave == True:
            if float(smap.framerate) != last_framerate:
                last_framerate = float(smap.framerate)
            #target_framerate = last_framerate
                camera.AcquisitionFrameRate = last_framerate
            if float(smap.exposuretime) != last_exposuretime:
                last_exposuretime = float(smap.exposuretime)
                camera.ExposureTime = last_exposuretime
            if notauto: # if manual gain
                if float(smap.gain) != last_gain:
                    last_gain = float(smap.gain)
                    if last_gain != float(40): #40 is autogain
                        camera.Gain = last_gain
                        gain = camera.Gain.GetValue()
                    else: # user has activated autogain
                        notauto = False
                        camera.GainAuto = "Continuous"
                        camera.AutoGainLowerLimit = 0
                        camera.AutoGainUpperLimit = 36
                        gain = grabResult.ChunkGain.Value
            else: #autogain
                gain = grabResult.ChunkGain.Value
                if float(smap.gain) != last_gain:
                    last_gain = float(smap.gain)
                    if last_gain != float(40): #40 is autogain, user has changed to manual gain
                        camera.GainAuto = "Off"
                        camera.Gain = last_gain
                        gain = camera.Gain.GetValue()
                        notauto = True
                #smap.gain = gain
            # if slave == True:
            #     if float(smap.gain) != last_gain:
            #         last_gain = float(smap.gain)
            #         camera.Gain = last_gain
            #         gain = camera.Gain.GetValue()
            # else:
            #     gain = grabResult.ChunkGain.Value
            #     smap.gain = gain
            print('skipped: ', grabResult.GetNumberOfSkippedImages(), \
				'\t gain: ', gain, \
				'\t temperature: ',camera.DeviceTemperature.Value, \
            '\t framerate: ', camera.ResultingFrameRate.Value, camera.AcquisitionFrameRate.Value,\
                  '\t exposuretime: ', camera.ExposureTime.GetValue(), \
                  )
#            pylon.FeaturePersistence.Save("test.txt", camera.GetNodeMap())
        continue
    else:
        # in case of an error
        print("Err: %d\t - %s" % (grabResult.GetErrorCode(), grabResult.GetErrorDescription()))
        dropped_counter +=1
        #filesk.write(str(index) + "," + str(TimeStampCam) + ","+ "skipped"  + "\n")
    camera.LineMode.SetValue("Input")
    grabResult.Release()
    failed_buffer = camera.GetStreamGrabberParams().Statistic_Buffer_Underrun_Count.GetValue()
    failed = camera.GetStreamGrabberParams().Statistic_Failed_Buffer_Count.GetValue()
    fail = fail + failed_buffer + failed
file.close()
filesk.close()


