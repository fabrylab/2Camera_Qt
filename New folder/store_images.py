# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 15:10:40 2020

@author: Ben
"""
from includes.MemMap import MemMap
import numpy as np
import os
# import time, sys
import tkinter as tk
from tkinter import filedialog
import tifffile
from datetime import datetime, time # , timedelta
import configparser
import configparser
import time
import sys
from configparser import ConfigParser


##### read config files and smap (there the measurement settings are saved)

config_cam = configparser.ConfigParser()
config_cam.read("Config_Slave.txt")

global config_setup
config_setup="config_setup.txt"

settings_mmap_slave = config_cam["camera"]["settings_mmap"]

config_cam.read("Config_Master.txt")
settings_mmap_master = config_cam["camera"]["settings_mmap"]

smap_slave = MemMap(settings_mmap_slave)
smap_master = MemMap(settings_mmap_master)


##### Defining global variables
#cam1 = Slave, cam2 = Master
global gain1, gain2, frame_rate1, frame_rate2, exposure_time1, exposure_time2, ext_trigger1, ext_trigger2
gain1 = smap_slave.gain
gain2 = smap_master.gain
frame_rate1 = smap_slave.framerate
frame_rate2 = smap_master.framerate
exposure_time1 = smap_slave.exposuretime
exposure_time2 = smap_master.exposuretime
ext_trigger1 = smap_slave.ext_trigger
ext_trigger2 = smap_master.ext_trigger

global finish, running
finish = False
running = False


#read default settings from config_stup.txt
config_0 = configparser.ConfigParser()
config_0.read(config_setup)
for section_name in config_0:
    section = config_0[section_name]
    for name in section:
        if name=="pressure":
            pressure_1=(section[name])
        if name=="imaging position after inlet":
            imaging_position_1=(section[name])
        if name=="room temperature":
            room_temperature_1=(section[name])
        if name=="bioink":
            bioink_1=(section[name])
        if name=="condensor aperture":
            aperture_1=(section[name])
        if name=="cell type":
            cell_type_1=(section[name])
        if name=="cell passage number":
            cell_passage_number_1=(section[name])
        if name=="time after harvest":
            time_after_harvest_1=(section[name])
        if name=="treatment":
            treatment_1=(section[name])
        if name=="objective":
            objective_1=(section[name])
        if name=="na":
            na_1=(section[name])
        if name=="coupler":
            coupler_1=(section[name])



    print()


#####  Functions for Saving

def sync_cams(cam1,cam2):
    time1 = 0
    time2 = 1
    time3 = 0
    time4 = 1
    while time4-time2 < 0.0009: #if the time difference between the reception of two images of the second cam is less than 0.9 ms, start all over
        print("time", time4 - time2)
        # make sure you get an image from cam1 right after its arrival & and than immediately get an image from cam2
        while time2 - time1 > 0.000001: #time difference between cam1 & cam2 should be < 1 us
            new = False
            timestamp1_old = cam1.setCounterToNewestImage()
            while new == False:
                timestamp1_old = cam1.getNextCounter()
                if timestamp1_old != None:
                    new = True
                    time1 = datetime.now().timestamp()
            timestamp2_old = cam2.setCounterToNewestImage()
            timestamp2_o = cam2.getNewestCounter()
            time2 = datetime.now().timestamp()
            print(time2)
            counter = cam1.counter_last
            counter_2 = cam2.counter_last
            counter2f= cam2.counter_f
        # measure the time until the next cam2 image is received
        counter_2_new = counter2f
        #time3 = datetime.now().timestamp()
        while counter_2_new == counter2f:
            timestamp2_o = cam2.getNewestCounter()
            counter_2_new = cam2.counter_f
            time4 = datetime.now().timestamp()
            print(counter_2_new, counter2f, time4)
        print("timeend", time2, time4, time4 - time2)
    return timestamp1_old, timestamp2_old, counter, counter_2


def acquire_images():
    global tif_name_1, tif_name_2, config_cam
    counter = 0
    counter_end = 0
    counter_2 = 0
    counter_end2 = 0
    button_Start.configure(state='disabled')
    global running, finish
    running = True
    label_no_of_im1.config(text=('opening Tiff Writer1'))
    label_no_of_im2.config(text=('opening Tiff Writer2'))
    root.update()
    date_time = datetime.now()
    tif_name_1 = str(date_time.year) + '_' + \
                 '{0:02d}'.format(date_time.month) + '_' + \
                 '{0:02d}'.format(date_time.day) + '_' + \
                 '{0:02d}'.format(date_time.hour) + '_' + \
                 '{0:02d}'.format(date_time.minute) + '_' + \
                 '{0:02d}'.format(date_time.second) + '_' + 'Fl'
    tif_name1 = folder_selected + '/' + tif_name_1 + '.tif'
    tif_name_2 = str(date_time.year) + '_' + \
                 '{0:02d}'.format(date_time.month) + '_' + \
                 '{0:02d}'.format(date_time.day) + '_' + \
                 '{0:02d}'.format(date_time.hour) + '_' + \
                 '{0:02d}'.format(date_time.minute) + '_' + \
                 '{0:02d}'.format(date_time.second) + '_' + 'B'
    tif_name2 = folder_selected + '/' + tif_name_2 + '.tif'
    print(tif_name1)
    print(tif_name2)
    tiffWriter1 = tifffile.TiffWriter(tif_name1, bigtiff=True)
    tiffWriter2 = tifffile.TiffWriter(tif_name2, bigtiff=True)
    label_no_of_im1.config(text=('opening camera'))
    label_no_of_im2.config(text=('opening camera2'))
    root.update()
    config_cam.read("Config_Slave.txt")
    cam1 = GigECam(config_cam["camera"]["output_mmap"])
    config_cam.read("Config_Master.txt")
    cam2 = GigECam(config_cam["camera"]["output_mmap"])
    label_no_of_im1.config(text=('starting image aquisition'))
    label_no_of_im2.config(text=('starting image aquisition2'))
    root.update()

    timestamp1_old, timestamp2_old, counter, counter_2 = sync_cams(cam1,cam2)

    ext_trigger2 = smap_master.ext_trigger
    ext_trigger1 = smap_slave.ext_trigger
    if ext_trigger2 == False:
        counter_end = cam1.counter_last + int(duration_1) * frame_rate1
        counter_end2 = cam2.counter_last + int(duration_1) * frame_rate2
    else:
        counter_end = cam1.counter_last + int(duration_1) * 500
        counter_end2 = cam2.counter_last + int(duration_1) * 500

    if ext_trigger2 == True:
        a = np.around(500 / frame_rate1)
        i = 0
    while counter_2 < counter_end2:
        im = None
        im2 = None
        while (im2 is None):
            im2, timestamp2, skipped2, skipped_total2 = cam2.getNextImage()
        while (im is None):
            im, timestamp, skipped, skipped_total = cam1.getNextImage()
        dif1 = timestamp  - timestamp1_old
        dif2 = timestamp2  - timestamp2_old

        if dif1 > 1000/frame_rate1 +1 or dif2 > 1000/frame_rate2 +1:
            print('skipped at least one image, dif1 = %3.1f  dif2 = %3.1f ' % (dif1, dif2))
            counter2_old = counter_2
            counter_old = counter
            timestamp1_old, timestamp2_old, counter, counter_2 = sync_cams(cam1, cam2)
            timestamp = timestamp1_old
            timestamp2 = timestamp2_old
            counter_end2 = counter_end2 + counter_2 - counter2_old
            counter_end = counter_end + counter - counter_old
            print('camers newly synchronized', str(counter_2 - counter2_old))
        else:
            if ext_trigger2 == False:
                metad = {'timestamp': str(timestamp)}
                tiffWriter1.save(im, compression=0, metadata=metad, contiguous=False)
                counter = counter + 1

                metad2 = {'timestamp': str(timestamp2)}
                tiffWriter2.save(im2, compression=0, metadata=metad2, contiguous=False)
                counter_2 = counter_2 + 1
            else: #if external trigger with framerate 500 and you want to choose another framerate
                if i%a ==0:
                    metad = {'timestamp': str(timestamp)}
                    tiffWriter1.save(im, compression=0, metadata=metad, contiguous=False)
                    counter = counter + 1

                    metad2 = {'timestamp': str(timestamp2)}
                    tiffWriter2.save(im2, compression=0, metadata=metad2, contiguous=False)
                    counter_2 = counter_2 + 1
                    i +=1
                else:
                    counter = counter + 1
                    counter_2 = counter_2 + 1
                    i +=1
            if (counter_end2 - counter_2) % (frame_rate2 / 10) == 0:
                label_no_of_im1.config(text=str(counter - counter_end + int(duration_1) * frame_rate1))
                label_no_of_im2.config(text=str(counter_2 - counter_end2 + int(duration_1) * frame_rate2))
                root.update()
        timestamp1_old = timestamp
        timestamp2_old = timestamp2
        if running == False:
            break
    print(counter_end, counter_end2)
    tiffWriter1.close()
    tiffWriter2.close()
    del cam1
    del cam2

    button_Start.configure(state='normal')
    running = False

#create config file
    config = configparser.ConfigParser()
    config['Default'] = {'version': '1'}
    pressure_str = str(pressure_1)  # + ' kPa'
    imaging_pos_str = str(imaging_position_1)  # + ' cm'
    room_temperature_str = str(room_temperature_1)  # + ' deg C'
    cell_temperature_str = room_temperature_str
    bioink_str = str(bioink_1)
    config['SETUP'] = {'pressure': pressure_str, 'channel width': '200 um',
                       'channel length': '5.8 cm', 'imaging position after inlet': imaging_pos_str,
                       'bioink': bioink_str, 'room temperature': room_temperature_str,
                       'cell temperature': cell_temperature_str}
    aperture_str = str(aperture_1)
    objective_str = str(objective_1)
    na_str = str(na_1)
    coupler_str = str(coupler_1)
    config['MICROSCOPE'] = {'microscope': 'Leica DM 6000', 'objective': objective_str,
                            'na': na_str , 'coupler': coupler_str , 'condensor aperture': aperture_str}
    frame_rate_str1 = str(frame_rate1) + ' fps'
    gain_str1 = str(gain1)
    exposure_time_str1 = str(exposure_time1) + 'us'
    frame_rate_str2 = str(frame_rate2) + ' fps'
    gain_str2 = str(gain2)
    exposure_time_str2 = str(exposure_time2) + 'us'
    config['CAMERA'] = {'exposure time': exposure_time_str1, 'gain': gain_str1, 'frame rate': frame_rate_str1,
                        'camera': 'Basler acA20-520', 'camera pixel size': '6.9 um'}
    config['CAMERA2'] = {'exposure time': exposure_time_str2, 'gain': gain_str2, 'frame rate': frame_rate_str2,
                        'camera': 'Basler acA20-520', 'camera pixel size': '6.9 um'}
    cell_type_str = str(cell_type_1)
    cell_passage_number_str = str(cell_passage_number_1)
    time_after_harvest_str = str(time_after_harvest_1)  # + ' min'
    treatment_str = str(treatment_1)
    config['CELL'] = {'cell type': cell_type_str, 'cell passage number': cell_passage_number_str,
                      'time after harvest': time_after_harvest_str, 'treatment': treatment_str}

    config_name = folder_selected + '/' + tif_name_2 + '_config' + '.txt'  # config_name
    with open(config_name, 'w') as configfile:
        config.write(configfile)
    with open(config_setup, 'w') as configfile:
        config.write(configfile)
    configfile.close()

    if finish == True:
        root.destroy()


def stop_images():
    global running
    running = False



def exit_program():
    global finish, running
    if running == False:
        root.destroy()
    finish = True
    running = False


def change_frame_rate1():
    global frame_rate1 , frame_rate2
    if int(framerate1.get()) != frame_rate1:
        try:
            frame_rate1 = int(framerate1.get())
        except:
            frame_rate1 = smap_slave.framerate
        if frame_rate1 > 500:
            frame_rate1 = 500

    if int(framerate2.get()) != frame_rate2:
        try:
            frame_rate2 = int(framerate2.get())
        except:
            frame_rate2 = smap_master.framerate
        if frame_rate2 > 500:
            frame_rate2 = 500
        frame_rate1 = frame_rate2
    frame_rate2 = frame_rate1
    smap_slave.framerate = frame_rate1
    smap_master.framerate = frame_rate2

    framerate1.delete(0, tk.END)
    framerate1.insert(10, str(smap_slave.framerate))
    print(frame_rate1)

    framerate2.delete(0, tk.END)
    framerate2.insert(10, str(smap_master.framerate))
    print(frame_rate2)

    root.update()

def change_gain1():
    global gain1
    try:
        gain1 = int(gain_1.get())
    except:
        gain1 = smap_slave.gain
    if gain1 > 36:
        gain1 = 40
    if gain1 < 0:
        gain1 = 0
    smap_slave.gain = gain1
    gain_1.delete(0, tk.END)
    gain_1.insert(10, str(smap_slave.gain))
    print(gain1)
    root.update()

def change_gain2():
    global gain2
    try:
        gain2 = int(gain_2.get())
    except:
        gain2 = smap_slave.gain
    if gain2 > 36:
        gain2 = 40
    if gain2 < 0:
        gain2 = 0
    smap_master.gain = gain2
    gain_2.delete(0, tk.END)
    gain_2.insert(10, str(smap_master.gain))
    print(gain2)
    root.update()


def change_exposure_time1():
    global exposure_time1
    try:
        exposure_time1 = int(exposuretime1.get())
    except:
        exposure_time1 = smap_slave.exposuretime
    if exposure_time1 > 1800:
        exposure_time1 = 1800
    if exposure_time1 < 30:
        exposure_time1 = 30
    smap_slave.exposuretime = exposure_time1
    exposuretime1.delete(0, tk.END)
    exposuretime1.insert(10, str(smap_slave.exposuretime))
    print(exposure_time1)
    root.update()

def change_exposure_time2():
    global exposure_time2
    try:
        exposure_time2 = int(exposuretime2.get())
    except:
        exposure_time2 = smap_master.exposuretime
    if exposure_time2 > 1800:
        exposure_time2 = 1800
    if exposure_time2 < 30:
        exposure_time2 = 30
    smap_master.exposuretime = exposure_time2
    exposuretime2.delete(0, tk.END)
    exposuretime2.insert(10, str(smap_master.exposuretime))
    print(exposure_time2)
    root.update()


def change_pressure():
    global pressure, pressure_1
    pressure_1 = pressure.get()
    print(pressure_1)
    root.update()


def change_objective():
    global objective, objective_1
    objective_1 = objective.get()
    print(objective_1)
    root.update()

def change_na():
    global na, na_1
    na_1 = na.get()
    print(na_1)
    root.update()

def change_coupler():
    global coupler, coupler_1
    coupler_1 = coupler.get()
    print(coupler_1)
    root.update()


def change_imaging_position():
    global imaging_position, imaging_position_1
    imaging_position_1 = imaging_position.get()
    print(imaging_position_1)
    root.update()


def change_bioink():
    global bioink, bioink_1
    bioink_1 = bioink.get()
    print(bioink_1)
    root.update()


def change_room_temperature():
    global room_temperature, room_temperature_1
    room_temperature_1 = room_temperature.get()
    print(room_temperature_1)
    root.update()


def change_cell_type():
    global cell_type, cell_type_1
    cell_type_1 = cell_type.get()
    print(cell_type_1)
    root.update()


def change_cell_passage_number():
    global cell_passage_number, cell_passage_number_1
    cell_passage_number_1 = cell_passage_number.get()
    print(cell_passage_number_1)
    root.update()


def change_time_after_harvest():
    global time_after_harvest, time_after_harvest_1
    time_after_harvest_1 = time_after_harvest.get()
    print(time_after_harvest_1)
    root.update()


def change_treatment():
    global treatment, treatment_1
    treatment_1 = treatment.get()
    print(treatment_1)
    root.update()

def change_aperture():
    global aperture, aperture_1
    aperture_1 = aperture.get()
    print(aperture_1)
    root.update()


def change_duration():
    global duration, duration_1
    duration_1 = duration.get()
    print(duration_1)
    root.update()


def change_dir():
    root1 = tk.Tk()
    root1.withdraw()
    global folder_selected
    folder_selected = filedialog.askdirectory()
    print(folder_selected)
    if folder_selected != '':
        label_path.config(text=folder_selected)
    root1.destroy()
    root.update()

# fuctions for reading the mmap (buffer)
class GigECam():
    def __init__(self, mmap_xml):
        self.mmap = MemMap(mmap_xml)
        self.counter_last = -1
        # percentil calc paramter
        self.pct_counter = 0
        self.pct_min = None
        self.pct_max = None

    def getNewestImage(self):
        # get newest counter
        counters = [slot.counter for slot in self.mmap.rbf]
        counter_max = np.max(counters)
        counter_max_idx = np.argmax(counters)
        image = self.mmap.rbf[counter_max_idx].image
        timestamp = self.mmap.rbf[counter_max_idx].timestamp
        self.counter_last = counter_max
        self.last_slot_index = counter_max_idx
        return image, timestamp

    def setCounterToNewestImage(self):
        # get newest counter
        counters = [slot.counter for slot in self.mmap.rbf]
        counter_max = np.max(counters)
        counter_max_idx = np.argmax(counters)
        timestamp = self.mmap.rbf[counter_max_idx].timestamp
        self.counter_last = counter_max
        self.last_slot_index = counter_max_idx
        return timestamp

    def getNewestCounter(self):
        # get newest counter
        counters_f = [slot.counter for slot in self.mmap.rbf]
        counter_max_f = np.max(counters_f)
        counter_max_idx_f = np.argmax(counters_f)
        timestamp = self.mmap.rbf[counter_max_idx_f].timestamp
        self.counter_f = counter_max_f
        self.last_slot_index_f = counter_max_idx_f
        return timestamp

    def getNextCounter(self):
        next_slot_index = (self.last_slot_index + 1) % len(self.mmap.rbf)
        if self.counter_last < self.mmap.rbf[next_slot_index].counter:
            self.last_slot_index = next_slot_index
            self.counter_last = self.mmap.rbf[next_slot_index].counter
            timestamp = self.mmap.rbf[next_slot_index].timestamp
            return timestamp
        else:
            return None

    def getNextImage(self):
        next_slot_index = (self.last_slot_index + 1) % len(self.mmap.rbf)
        if self.counter_last < self.mmap.rbf[next_slot_index].counter:
            # if self.counter_last+1 != self.mmap.rbf[next_slot_index].counter:
            # raise ValueError("Skipped Frames")
            self.last_slot_index = next_slot_index
            self.counter_last = self.mmap.rbf[next_slot_index].counter
            image = self.mmap.rbf[next_slot_index].image
            timestamp = self.mmap.rbf[next_slot_index].timestamp
            skipped = self.mmap.rbf[next_slot_index].skip
            skipped_total = self.mmap.rbf[next_slot_index].skip_total
            return image, timestamp, skipped, skipped_total
        else:
            return None, None, None, None


#####   User interface

root = tk.Tk()
root.title("Acquire Images")

# change directory where images are saved
dateAc = datetime.now()
folderName =  str(dateAc.year) + '.' + str(dateAc.month) + '.' + str(dateAc.day)
defaultPath = 'C:\\Users\\User\\Desktop\\'  + folderName

label_path = tk.Label(root, fg="dark green")
label_path.grid(row=0, column=1, columnspan=2)
label_path.config(text=defaultPath)

button_ChangeDir = tk.Button(root, width=10,
                             text="Change Dir",
                             command=change_dir)
button_ChangeDir.grid(row=0, column=0, sticky='w', pady=2)

#displays how many images are already saved
txt_no_of_im = tk.Label(root, text="# of images")
txt_no_of_im.grid(row=2, column=0, sticky='w', pady=2)

label_no_of_im1 = tk.Label(root, width=20, fg="dark green")
label_no_of_im1.grid(row=2, column=1, sticky='w', pady=2)

txt_no_of_im2 = tk.Label(root, text="# of images2")
txt_no_of_im2.grid(row=2, column=3, sticky='w', pady=2)

label_no_of_im2 = tk.Label(root, width=20, fg="dark green")
label_no_of_im2.grid(row=2, column=4, sticky='w', pady=2)

#different setting options
txt_gain1 = tk.Label(root, text="gain (>36: Auto Gain)")
txt_gain1.grid(row=3, column=0, sticky='w', pady=2)

gain_1 = tk.Entry(root)
gain_1.grid(row=3, column=1, sticky='w', pady=2)
gain_1.insert(10, str(smap_slave.gain))

txt_gain2 = tk.Label(root, text="gain2 (>36: Auto Gain)")
txt_gain2.grid(row=3, column=3, sticky='w', pady=2)

gain_2 = tk.Entry(root)
gain_2.grid(row=3, column=4, sticky='w', pady=2)
gain_2.insert(10, str(smap_master.gain))

txt_framerate1 = tk.Label(root, text="framerate1")
txt_framerate1.grid(row=4, column=0, sticky='w', pady=2)

framerate1 = tk.Entry(root)
framerate1.grid(row=4, column=1, sticky='w', pady=2)
framerate1.insert(10, str(smap_slave.framerate))

txt_framerate2 = tk.Label(root, text="framerate2")
txt_framerate2.grid(row=4, column=3, sticky='w', pady=2)

framerate2 = tk.Entry(root)
framerate2.grid(row=4, column=4, sticky='w', pady=2)
framerate2.insert(10, str(smap_master.framerate))


txt_exposuretime1 = tk.Label(root, text="exposuretime1")
txt_exposuretime1.grid(row=5, column=0, sticky='w', pady=2)

exposuretime1 = tk.Entry(root)
exposuretime1.grid(row=5, column=1, sticky='w', pady=2)
exposuretime1.insert(10, str(smap_slave.exposuretime))

txt_exposuretime2 = tk.Label(root, text="exposuretime2")
txt_exposuretime2.grid(row=5, column=3, sticky='w', pady=2)

exposuretime2 = tk.Entry(root)
exposuretime2.grid(row=5, column=4, sticky='w', pady=2)
exposuretime2.insert(10, str(smap_master.exposuretime))

txt_pressure = tk.Label(root, text="Parameter:" , fg="dark blue")
txt_pressure.grid(row=6, column=0, sticky='w', pady=2 )

txt_pressure = tk.Label(root, text="Pressure")
txt_pressure.grid(row=7, column=0, sticky='w', pady=2)

pressure = tk.Entry(root)
pressure.grid(row=7, column=1, sticky='w', pady=2)
pressure.insert(10, pressure_1)

txt_imaging_position = tk.Label(root, text="Imaging position")
txt_imaging_position.grid(row=8, column=0, sticky='w', pady=2)

imaging_position = tk.Entry(root)
imaging_position.grid(row=8, column=1, sticky='w', pady=2)
imaging_position.insert(10, imaging_position_1)

txt_aperture = tk.Label(root, text="Aperture")
txt_aperture.grid(row=9, column=0, sticky='w', pady=2)

aperture = tk.Entry(root)
aperture.grid(row=9, column=1, sticky='w', pady=2)
aperture.insert(10, 8)

txt_bioink = tk.Label(root, text="Bioink")
txt_bioink.grid(row=10, column=0, sticky='w', pady=2)

bioink = tk.Entry(root)
bioink.grid(row=10, column=1, sticky='w', pady=2)
bioink.insert(10, bioink_1)

txt_room_temperature = tk.Label(root, text="Room temperature")
txt_room_temperature.grid(row=11, column=0, sticky='w', pady=2)

room_temperature = tk.Entry(root)
room_temperature.grid(row=11, column=1, sticky='w', pady=2)
room_temperature.insert(10, room_temperature_1)

txt_cell_type = tk.Label(root, text="Cell type")
txt_cell_type.grid(row=12, column=0, sticky='w', pady=2)

cell_type = tk.Entry(root)
cell_type.grid(row=12, column=1, sticky='w', pady=2)
cell_type.insert(10, cell_type_1)

txt_cell_passage_number = tk.Label(root, text="Cell passage number")
txt_cell_passage_number.grid(row=13, column=0, sticky='w', pady=2)

cell_passage_number = tk.Entry(root)
cell_passage_number.grid(row=13, column=1, sticky='w', pady=2)
cell_passage_number.insert(10, cell_passage_number_1)

txt_time_after_harvest = tk.Label(root, text="Time after harvest")
txt_time_after_harvest.grid(row=14, column=0, sticky='w', pady=2)

time_after_harvest = tk.Entry(root)
time_after_harvest.grid(row=14, column=1, sticky='w', pady=2)
time_after_harvest.insert(10, time_after_harvest_1)

txt_treatment = tk.Label(root, text="Treatment")
txt_treatment.grid(row=15, column=0, sticky='w', pady=2)

treatment = tk.Entry(root)
treatment.grid(row=15, column=1, sticky='w', pady=2)
treatment.insert(10, treatment_1)

txt_duration = tk.Label(root, text="Duration in s")
txt_duration.grid(row=16, column=0, sticky='w', pady=2)

duration_1 = '20'
duration = tk.Entry(root)
duration.grid(row=16, column=1, sticky='w', pady=2)
duration.insert(10, duration_1)

txt_objective = tk.Label(root, text="Objective")
txt_objective.grid(row=7, column=3, sticky='w', pady=2)

objective = tk.Entry(root)
objective.grid(row=7, column=4, sticky='w', pady=2)
objective.insert(10, objective_1)

txt_na = tk.Label(root, text="NA")
txt_na.grid(row=8, column=3, sticky='w', pady=2)

na = tk.Entry(root)
na.grid(row=8, column=4, sticky='w', pady=2)
na.insert(10, na_1)

txt_coupler = tk.Label(root, text="Coupler")
txt_coupler.grid(row=9, column=3, sticky='w', pady=2)

coupler = tk.Entry(root)
coupler.grid(row=9, column=4, sticky='w', pady=2)
coupler.insert(10, coupler_1)

#start, stop & quit button
button_Quit = tk.Button(root, width=20,
                        text="Quit",
                        fg="red",
                        command=exit_program)
button_Quit.grid(row=4, column=2, sticky='w', pady=2)

button_Start = tk.Button(root, width=20,
                         text="Start",
                         command=acquire_images)
button_Start.grid(row=2, column=2, sticky='w', pady=2)

button_Stop = tk.Button(root, width=20,
                        text="Stop",
                        command=stop_images)
button_Stop.grid(row=3, column=2, sticky='w', pady=2)

#Trigger On/Off switch

# Keep track of the button state on/off
is_on = False
ext_trigger2 = False
ext_trigger1 = False
smap_master.ext_trigger = ext_trigger2
smap_slave.ext_trigger = ext_trigger1

# Define trigger switch function
def switch():
    global is_on

    # Determin is on or off
    if is_on:
        on_button.config(image=off)
        is_on = False
        ext_trigger2 = False
        ext_trigger1 = False
        smap_master.ext_trigger = ext_trigger2
        smap_slave.ext_trigger = ext_trigger1
    else:
        on_button.config(image=on)
        is_on = True
        ext_trigger2 = True
        ext_trigger1 = True
        smap_master.ext_trigger = ext_trigger2
        smap_slave.ext_trigger = ext_trigger1

# Create trigger On/Off switch
on = tk.PhotoImage(file="on.png")
off = tk.PhotoImage(file="off.png")

on_button = tk.Button(root, image=off, bd=0,
                   command=switch)
on_button.grid(row=10, column=4, sticky='w', pady=2)

txt_trigger = tk.Label(root, text="External trigger")
txt_trigger.grid(row=10, column=3, sticky='w', pady=2)

button_ChangeConfig = tk.Button(root, width=20,
                                text="Change Configuration",
                                fg="black",
                                command=lambda: [change_frame_rate1(), change_gain1() ,  change_gain2(), change_exposure_time1(), change_exposure_time2(), change_duration(), change_pressure(),
                                                 change_aperture(), change_imaging_position(), change_bioink(),
                                                 change_room_temperature(), change_cell_type(),
                                                 change_cell_passage_number(), change_time_after_harvest(),
                                                 change_treatment(), change_objective() , change_na() , change_coupler()])

button_ChangeConfig.grid(row=5, column=2, sticky='w', pady=2)


#folder_selected = os.getcwd()
folder_selected = defaultPath
if os.path.exists(folder_selected)==False:
    os.mkdir(folder_selected)
label_path.config(text=folder_selected)

root.mainloop()




