#!/usr/bin/env python3
"""
Copyright 2016-2022 The FEAGI Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================
"""

from feagi_agent import feagi_interface as feagi
from feagi_agent import router
from time import sleep
import threading
import asyncio

# Variable storage #
raw_aptr = -1
global_ID_cortical_size = None
full_list_dimension = []
previous_genome_timestamp = 0
genome_tracker = 0
message_from_feagi = {}
refresh_rate = 0.01


def generate_feagi_data(rgb, msg_counter, date, message_to_feagi):
    """
    This function generates data for Feagi by combining RGB values, message counter, and date into
    the provided message.
    """
    try:
        if "data" not in message_to_feagi:
            message_to_feagi["data"] = dict()
        if "sensory_data" not in message_to_feagi["data"]:
            message_to_feagi["data"]["sensory_data"] = dict()
        message_to_feagi["data"]["sensory_data"]['camera'] = rgb['camera']
    except Exception as e:
        print("ERROR: ", e)
    message_to_feagi['timestamp'] = date
    message_to_feagi['counter'] = msg_counter
    return message_to_feagi


def append_sensory_data_for_feagi(sensory_category, sensory_data, message_to_feagi):
    """
    :param sensory_category: A name such as training, camera, IR, ultrasonic and so on.
    :param sensory_data: The data of dict only
    :param message_to_feagi: Use the existing dict to append
    :return: the updated dict called `message_to_feagi`
    """
    if "data" not in message_to_feagi:
        message_to_feagi["data"] = {}
    if "sensory_data" not in message_to_feagi["data"]:
        message_to_feagi["data"]["sensory_data"] = {}
    message_to_feagi["data"]["sensory_data"][sensory_category] = sensory_data
    return message_to_feagi


def signals_from_feagi(feagi_opu_channel):
    """ get OPU from FEAGI """
    return router.fetch_feagi(feagi_opu_channel)


def signals_to_feagi(message_to_feagi, feagi_ipu_channel, agent_settings):
    router.send_feagi(message_to_feagi, feagi_ipu_channel, agent_settings)


def fetch_resolution_selected(message_from_feagi, capabilities):
    if "o_vres" in message_from_feagi["opu_data"]:
        if message_from_feagi["opu_data"]["o_vres"]:
            for i in message_from_feagi["opu_data"]["o_vres"]:
                dev_data = feagi.block_to_array(i)  # TODO: remove use feagi interface
                if dev_data[0] == 0:
                    capabilities['camera']['current_select'][0] = \
                        capabilities['camera']['resolution_presets'][dev_data[2]]
                if dev_data[0] == 1:
                    capabilities['camera']['current_select'][1] = \
                        capabilities['camera']['resolution_presets'][dev_data[2]]
    return capabilities


def fetch_resolution_peripherals_selected(message_from_feagi, capabilities):
    if "o_pres" in message_from_feagi["opu_data"]:
        if message_from_feagi["opu_data"]["o_pres"]:
            for i in message_from_feagi["opu_data"]["o_pres"]:
                dev_data = feagi.block_to_array(i)  # TODO: remove use feagi interface
                if dev_data[0] == 0:
                    capabilities['camera']['current_select_peripheral'] = \
                        capabilities['camera']['resolution_presets'][dev_data[2]]
    return capabilities


def check_aptr(get_size_for_aptr_cortical):
    return router.fetch_aptr(get_size_for_aptr_cortical)


def check_id_size(get_size_for_ID):
    return router.fetch_ID(get_size_for_ID)


def grab_geometry():
    return router.fetch_geometry()


def generate_OPU_list(capabilities):
    sensor_list = []
    for i in capabilities:
        if "type" in capabilities[i]:
            if "opu" in capabilities[i]["type"]:
                sensor_list.append(i)
    return sensor_list


def obtain_opu_data(device_list, message_from_feagi):
    opu_signal_dict = {}
    opu_data = feagi.opu_processor(message_from_feagi)
    for i in device_list:
        if i in opu_data and opu_data[i]:
            for x in opu_data[i]:
                if i not in opu_signal_dict:
                    opu_signal_dict[i] = {}
                opu_signal_dict[i][x] = opu_data[i][x]
    return opu_signal_dict


def obtain_data_type(data):
    if type(data).__name__ == "ImagingCore":
        print("ImagingCore")
        return "ImagingCore"
    elif type(data).__name__ == "ndarray":
        print("numpy.ndarray")
        return "ndarray"
    elif type(data).__name__ == "list":
        print("list")
        return "list"
    else:
        print("Couldn't find: ", type(data).__name__, " and full name of the class: ", type(data))
        return "Unknown"


def obtain_blink_data(raw_frame, message_from_feagi, capabilities):
    if "o_blnk" in message_from_feagi["opu_data"]:
        if message_from_feagi["opu_data"]["o_blnk"]:
            capabilities['camera']['blink'] = raw_frame
    return capabilities


def obtain_genome_number(genome_tracker, message_from_feagi):
    if 'genome_num' in message_from_feagi:
        if message_from_feagi['genome_num'] != genome_tracker:
            return message_from_feagi['genome_num']
    return genome_tracker


def monitor_switch(message_from_feagi, capabilities):
    if "o__mon" in message_from_feagi["opu_data"]:
        if message_from_feagi["opu_data"]["o__mon"]:
            for i in message_from_feagi["opu_data"]["o__mon"]:
                monitor_update = feagi.block_to_array(i)
                capabilities['camera']['monitor'] = monitor_update[0]
    return capabilities


def gaze_control_update(message_from_feagi, capabilities):
    if 'o__gaz' in message_from_feagi["opu_data"]:
        for data_point in message_from_feagi["opu_data"]['o__gaz']:
            device_id = data_point.split('-')[0]
            if int(device_id) in [0, 1]:
                feagi_aptr = (int(data_point.split('-')[-1]))
                aptr_cortical_size = full_list_dimension['Vision_Gaze'][6] - 1
                max_range = capabilities['camera']['vision_range'][1]
                min_range = capabilities['camera']['vision_range'][0]
                capabilities['camera']["gaze_control"][int(device_id)] = int(
                    ((feagi_aptr / aptr_cortical_size) * (max_range - min_range)) + min_range)
            # Comment new method out
            # processed_data_point = feagi.block_to_array(data_point)
            # device_id = processed_data_point[0]
            # device_power = message_from_feagi["opu_data"]['o__gaz'][data_point]
            # if device_power == 100:
            #     device_power -= 1
            # capabilities['camera']['gaze_control'][device_id] = device_power
    return capabilities


def pupil_control_update(message_from_feagi, capabilities):
    if 'o__pup' in message_from_feagi["opu_data"]:
        for data_point in message_from_feagi["opu_data"]['o__pup']:
            device_id = data_point.split('-')[0]
            if int(device_id) in [0, 1]:
                feagi_aptr = (int(data_point.split('-')[-1]))
                aptr_cortical_size = full_list_dimension['Vision_Pupil'][6] - 1
                max_range = capabilities['camera']['vision_range'][1]
                min_range = capabilities['camera']['vision_range'][0]
                capabilities['camera']["pupil_control"][int(device_id)] = int(((feagi_aptr /
                                                                                aptr_cortical_size) * (
                                                                                       max_range - min_range)) + min_range)
        # comment new method out
        # for data_point in message_from_feagi["opu_data"]['o__pup']:
        #     processed_data_point = feagi.block_to_array(data_point)
        #     device_id = processed_data_point[0]
        #     device_power = message_from_feagi["opu_data"]['o__pup'][data_point]
        #     if device_power == 100:
        #         device_power -= 1
        #     capabilities['camera']['pupil_control'][device_id] = device_power
    return capabilities


def detect_ID_data(message_from_feagi):
    """
    :param message_from_feagi: Should be a dict from FEAGI data only
    :return: Return the data that given by FEAGI
    """
    if "o___id" in message_from_feagi["opu_data"]:
        if message_from_feagi["opu_data"]["o___id"]:
            return message_from_feagi["opu_data"]["o___id"]
    return {}


def detect_genome_change(message_from_feagi):
    if "genome_changed" in message_from_feagi:
        if message_from_feagi["genome_changed"]:
            return message_from_feagi["genome_changed"]


def check_refresh_rate(message_from_feagi, current_second):
    if message_from_feagi is not None:
        return message_from_feagi['burst_frequency']
    return current_second


def fetch_full_dimensions():
    return router.fetch_cortical_dimensions()


def check_genome_status(message_from_feagi):
    global previous_genome_timestamp, genome_tracker, full_list_dimension
    if message_from_feagi['genome_changed'] is not None:
        if full_list_dimension is None:
            full_list_dimension = []
        if len(full_list_dimension) == 0:
            full_list_dimension = fetch_full_dimensions()
        genome_changed = detect_genome_change(message_from_feagi)
        if genome_changed != previous_genome_timestamp:
            full_list_dimension = fetch_full_dimensions()
            previous_genome_timestamp = message_from_feagi["genome_changed"]
        current_tracker = obtain_genome_number(genome_tracker, message_from_feagi)
        if genome_tracker != current_tracker:
            full_list_dimension = fetch_full_dimensions()
            genome_tracker = current_tracker


def fetch_vision_turner(message_from_feagi, capabilities):
    if full_list_dimension:
        if "ovtune" in message_from_feagi["opu_data"]:
            if message_from_feagi["opu_data"]["ovtune"]:
                for data_point in message_from_feagi["opu_data"]['ovtune']:
                    device_id = data_point.split('-')[0]
                    feagi_aptr = (int(data_point.split('-')[-1]))
                    aptr_cortical_size = full_list_dimension['threshold'][6] - 1
                    max_range = capabilities['camera']["threshold_range"][1]
                    min_range = capabilities['camera']["threshold_range"][0]
                    capabilities['camera']["threshold_default"][int(device_id)] = int(
                        ((feagi_aptr / aptr_cortical_size) * (max_range - min_range)) + min_range)
                # for data_point in message_from_feagi["opu_data"]["ovtune"]:
                #     processed_data_point = feagi.block_to_array(data_point)
                #     device_id = processed_data_point[0]
                #     device_power = message_from_feagi["opu_data"]['ovtune'][data_point]
                #     capabilities['camera']['effect'][device_id] = device_power
    return capabilities


def fetch_threshold_type(message_from_feagi, capabilities):
    if "ov_thr" in message_from_feagi["opu_data"]:
        if message_from_feagi["opu_data"]["ov_thr"]:
            for data_point in message_from_feagi["opu_data"]["ov_thr"]:
                device_id = int(data_point.split('-')[0])
                capabilities['camera']["threshold_type"][int(device_id)] = True
    return capabilities


def fetch_enhancement_data(message_from_feagi, capabilities):
    if full_list_dimension:
        if "ov_enh" in message_from_feagi["opu_data"]:
            if message_from_feagi["opu_data"]["ov_enh"]:
                for data_point in message_from_feagi["opu_data"]['ov_enh']:
                    device_id = int(data_point.split('-')[0])
                    if device_id == 1:
                        feagi_aptr = (int(data_point.split('-')[-1]))
                        aptr_cortical_size = full_list_dimension['enhancement'][6] - 1
                        max_range = 1.4
                        min_range = 0.5
                        capabilities['camera']["enhancement"][int(device_id)] = float(((feagi_aptr
                                                                                        / aptr_cortical_size) * (
                                                                                               max_range - min_range)) + min_range)
                    if device_id == 2:
                        feagi_aptr = (int(data_point.split('-')[-1]))
                        aptr_cortical_size = full_list_dimension['enhancement'][6] - 1
                        max_range = 2.0
                        min_range = 0.8
                        capabilities['camera']["enhancement"][int(device_id)] = float(((feagi_aptr
                                                                                        / aptr_cortical_size) * (
                                                                                               max_range - min_range)) + min_range)
                    if device_id == 0:
                        feagi_aptr = (int(data_point.split('-')[-1]))
                        aptr_cortical_size = full_list_dimension['enhancement'][6]
                        max_range = 100
                        min_range = -100
                        capabilities['camera']["enhancement"][int(device_id)] = float(((feagi_aptr
                                                                                        / aptr_cortical_size) * (
                                                                                               max_range - min_range)) + min_range)
    return capabilities


def create_runtime_default_list(list, capabilities):
    if not list:
        list = {
            "camera": {
                "type": "ipu",
                "disabled": False,
                "index": "00",
                "threshold_default": [50, 255, 130, 51],  # min #1, max #1, min #2, max #2,
                "threshold_range": [1, 255],
                "threshold_type": {},
                # simple thresholding types. see the retina.threshold_detect function
                "threshold_name": 0,  # Binary_threshold as a default
                "mirror": True,  # flip the image
                "blink": [],  # cv2 ndarray raw data of an image. Controlled by blink OPU in genome
                "gaze_control": {0: 1, 1: 1},  # Controlled by gaze_control in genome
                "pupil_control": {0: 99, 1: 99},  # Controlled by pupil_control in genome
                "vision_range": [1, 99],  # min, max
                "size_list": [],  # To get the size in real time based on genome's change/update
                "enhancement": {}  # Enable ov_enh OPU on inside the genome
            }
        }
        camera_config_update(list, capabilities)
    return list


def camera_config_update(list, capabilities):
    if 'gaze_control' in capabilities['camera']:
        list['camera']['gaze_control'] = capabilities['camera']['gaze_control']
    if 'pupil_control' in capabilities['camera']:
        list['camera']['pupil_control'] = capabilities['camera']['pupil_control']
    if "enhancement" in capabilities['camera']:
        list['camera']['enhancement'] = capabilities['camera']['enhancement']

def feagi_listener(feagi_opu_channel):
    """
    thread for listening FEAGI.
    """
    asyncio.run(router.fetch_feagi(feagi_opu_channel))
