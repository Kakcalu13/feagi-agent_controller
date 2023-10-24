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

from PIL import Image


def obtain_size(data):
    print("here: ", data.size)
    # return data.size()


def obtain_astype(data):
    return data.astype(np.uint8)


def pitina_to_ndarray(data, size):
    rgb_value = list(data)
    new_rgb = np.array(rgb_value)
    return new_rgb.reshape(size[1], size[0], 3)
