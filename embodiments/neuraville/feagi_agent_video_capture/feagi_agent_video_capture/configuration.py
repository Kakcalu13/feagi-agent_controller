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

feagi_settings = {
    # "feagi_auth_url": "http://127.0.0.1:9000/v1/k8/feagi_settings/auth_token",
    "feagi_url": None,
    "feagi_dns": None,
    "feagi_host": "127.0.0.1",
    "feagi_api_port": "8000",
}

agent_settings = {
    "agent_data_port": "10005",
    "agent_id": "camera_1",
    "agent_type": "embodiment",
    'TTL': 2,
    'last_message': 0,
    'compression': True
}

capabilities = {
    "camera": {
        "type": "ipu",
        "disabled": False,
        "index": "00",
        "video_device_index": 0,
        "image": "",
        "video_loop": False,
        "mirror": False,
        # "enhancement": {1:80, 2:80, 4: 80}, # Example. Brightness, Constrast, Shadow
        # "gaze_control": {0: 25, 1: 55}, # Gaze shifts right
        # "pupil_control": {0: 25, 1: 55}, # Pupil shifts up
        # "threshold_default": [50, 255, 130, 51] # min value, max value, min value, max value in
        # threshold setting. first and second is for regular webcam. Second is for vision blink OPU
    }
}

message_to_feagi = {"data": {}}
