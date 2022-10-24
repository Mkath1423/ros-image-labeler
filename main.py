#!/usr/bin/env python3
import os.path

import PySimpleGUI as sg
import numpy as np

from PIL import Image as PilImage
from io import BytesIO

import numpy

import rospy
import sensor_msgs

import pickle

from sensor_msgs.msg import Image

# -------------------- CONSTANTS --------------------#

# rostopic for the camera feed
camera_feed_topic = "/camera/color/image_raw"

# color of the location indicator
dot_color = "red"

# for resizing images, width takes precedent over height
target_w = 400
target_h = 400

# give a valid file path to continue adding to an existing file
load_from_file = "" # "~/test/things.pkl"
load_from_file = os.path.expanduser(load_from_file)

# -------------------- UTILITIES --------------------#

def pil_to_data(im):
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


def array_to_data(array):
    im = PilImage.fromarray(array)
    return pil_to_data(im)


def resize_image(im, w, h, target_w, target_h):
    if target_w is not None:
        return im.resize((int(target_w), int(h * target_w / w))), int(target_w), int(h * target_w / w)

    elif target_h is not None:
        return im.resize((int(w * target_h / h), int(target_w))), int(w * target_h / h), int(target_w)

    return im, w, h


def update_location_text(obj, x, y):
    obj.Update(value=f"Location: ({x}, {y})")


class ImageViewer:
    def __init__(self, x, y, w, h, key):
        self.graph = sg.Graph(
            canvas_size=(w, h),
            graph_bottom_left=(0, h),
            graph_top_right=(w, 0),
            key=key,
            enable_events=True,  # mouse click events
            background_color='white')

        self.image = None
        self.image_id = None

        self.location = None
        self.location_id = None

    def reset(self):
        self.graph.erase()

        self.image = None
        self.image_id = None

        self.location = None
        self.location_id = None

    def updateImage(self, arr):
        h, w, _ = arr.shape
        im, scaled_w, scaled_h = resize_image(PilImage.fromarray(arr), w, h, target_w, target_h)
        self.graph.set_size((scaled_w, scaled_h))
        self.graph.change_coordinates((0, h), (w, 0))

        if self.image is not None:
            self.graph.delete_figure(self.image_id)

        self.image = arr
        self.image_id = self.graph.draw_image(location=(0, 0), data=pil_to_data(im))

    def updatePoint(self, x, y):
        # if self.image_id is None:
        #     return

        if self.location is not None:
            self.graph.delete_figure(self.location_id)

        self.location = (x, y)
        self.location_id = self.graph.draw_point((x, y), 5, dot_color)


# -------------------- WINDOW SETUP --------------------#

live_data = None
live = sg.Image(size=(400, 400), key="live_graph")
live_col = sg.Column([[sg.Text("live view")], [live]])

im1 = ImageViewer(0, 0, 400, 400, "im1_graph")

im1_col = sg.Column([[sg.Text("img2")], [im1.graph],
                     [sg.Button("Capture", key="im1_cap"), sg.Text("Location: (None, None)", key="im1_text")]],
                    element_justification="center")

im2 = ImageViewer(0, 0, 400, 400, "im2_graph")
im2_col = sg.Column([[sg.Text("img2")], [im2.graph],
                     [sg.Button("Capture", key="im2_cap"), sg.Text("Location: (None, None)", key="im2_text")]],
                    element_justification="center")

layout = [
    [live_col, im1_col, im2_col],
    [sg.Button(button_text="add", key="add", size=(10, 1), visible=True)],
    [sg.Text("Save Location: "),
     sg.Input(key="save_location"),
     sg.Button("save")],

    [sg.Text("feedback", key="feedback", text_color="black", visible=False)],
]

window = sg.Window('ROS IMAGES SELECTOR', layout=layout, margins=(100, 100), element_justification="c")
window.finalize()

# -------------------- DATASET --------------------#

# schema is list of dicts
# [ {'img1': array(), 'img2': array(), 'loc_1': (123,456), 'loc_2':(789,101) }, {...} ]
dataset = []

if os.path.exists(load_from_file):
    with open(load_from_file, 'rb') as pf:
        dataset = pickle.load(pf)
    # dataset = list(np.load(load_from_file, allow_pickle=True))
    print(f"loaded {len(dataset)} images from file")


def add_dataset_element(img1, img2, loc_1, loc_2):
    global dataset
    dataset.append({"img1": img1, "img2": img2, "loc_1": loc_1, "loc_2": loc_2})


# -------------------- IMAGE FEED --------------------#

def live_camera_feed(data: Image):
    global live_data
    arr = np.frombuffer(data.data, dtype=np.uint8).reshape(data.height, data.width, -1)
    h, w, _ = arr.shape

    im, scaled_w, scaled_h = resize_image(PilImage.fromarray(arr), w, h, target_w, target_h)

    live.set_size((scaled_w, scaled_h))

    data = pil_to_data(im)
    live_data = arr
    live.update(data=data)


rospy.init_node("imagelabeler", anonymous=True)
rospy.Subscriber(camera_feed_topic, Image, live_camera_feed, queue_size=1, buff_size=10000000)  # My condolences to your RAM, but this killed all the latency.

# ----------------- EVENT HANDLING -----------------#

while True:
    event, values = window.read()

    # img 1
    if event == "im1_graph":
        x, y = values['im1_graph'][0], values['im1_graph'][1]
        im1.updatePoint(x, y)
        update_location_text(window["im1_text"], x, y)

    elif event == "im1_cap":
        update_location_text(window["im1_text"], None, None)
        im1.reset()

        if live_data is not None:
            im1.updateImage(live_data)

    # img 2
    elif event == "im2_graph":
        x, y = values['im2_graph'][0], values['im2_graph'][1]
        im2.updatePoint(x, y)
        window["im2_text"].Update(value=f"Location: ({x}, {y})")

    elif event == "im2_cap":
        update_location_text(window["im2_text"], None, None)
        im2.reset()
        if live_data is not None:
            im2.updateImage(live_data)

    # dataset
    elif event == "add":
        if any([i is None for i in [im1.image, im2.image, im1.location, im2.location]]):
            print("failed to add element")

        else:
            add_dataset_element(im1.image, im2.image, im1.location, im2.location)

            im1.reset()
            im2.reset()
            update_location_text(window["im1_text"], None, None)
            update_location_text(window["im2_text"], None, None)

            print("added element")

    # saving
    elif event == "save":
        path = window["save_location"].get()
        path = os.path.expanduser(path)

        if path != "" and (os.path.dirname(path) == "" or os.path.isdir(os.path.dirname(path))):
            # np.save(path, dataset)
            with open(path, 'wb') as pf:
                pickle.dump(dataset, pf)
            print(f"saved {len(dataset)} items to {path}")

        else:
            print(f"bad path, did not save")

    # break the loop and close the window
    elif event == sg.WINDOW_CLOSED:
        break

window.close()