import logging
import os.path
import time

import PIL.ImageShow
import PySimpleGUI as sg
import numpy as np

from PIL import Image
from io import BytesIO

import numpy

test_img = np.asarray(Image.open("im1.jpg"))
print(f"test img: {test_img.shape}")


def array_to_data(array):
    im = Image.fromarray(array)
    with BytesIO() as output:
        im.save(output, format="PNG")
        data = output.getvalue()
    return data


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

        self.graph.set_size((w, h))

        if self.image is not None:
            self.graph.delete_figure(self.image_id)

        self.image = arr
        self.image_id = self.graph.draw_image(location=(0, 0), data=array_to_data(arr))

    def updatePoint(self, x, y):
        # if self.image_id is None:
        #     return

        if self.location is not None:
            self.graph.delete_figure(self.location_id)

        self.location = (x, y)
        self.location_id = self.graph.draw_point((x, y), 5, "black")


live = ImageViewer(0, 0, 600, 480, "live_graph")
live_col = sg.Column([[sg.Text("live view")], [live.graph]])

im1 = ImageViewer(0, 0, 600, 480, "im1_graph")

im1_col = sg.Column([[sg.Text("img2")], [im1.graph],
                     [sg.Button("Capture", key="im1_cap"), sg.Text("Location: (None, None)", key="im1_text")]],
                    element_justification="center")

im2 = ImageViewer(0, 0, 600, 480, "im2_graph")
im2_col = sg.Column([[sg.Text("img2")], [im2.graph],
                     [sg.Button("Capture", key="im2_cap"), sg.Text("Location: (None, None)", key="im2_text")]],
                    element_justification="center")

layout = [
    [live_col, im1_col, im2_col],
    [sg.Button(button_text="add", key="add", size=(10, 1), visible=True)],
    [sg.Text("Save Location: "),
     sg.Input(key="save_location"),
     sg.Button("Save")],

    [sg.Text("feedback", key="feedback", text_color="black", visible=False)],
]

window = sg.Window('ROS IMAGES SELECTOR', layout=layout, margins=(100, 100), element_justification="c")
window.finalize()

dataset = []
current_datum = None


def add_dataset_element(img1, img2, loc_1, loc_2):
    dataset.append({"img1": img1, "img2": img2, "loc_1": loc_1, "loc_2": loc_2})


def update_location_text(obj, x, y):
    obj.Update(value=f"Location: ({x}, {y})")


live.updateImage(test_img)

while True:
    event, values = window.read()

    live.graph.draw_image(filename="img.png", location=(0, 400))

    # img 1
    if event == "im1_graph":
        x, y = values['im1_graph'][0], values['im1_graph'][1]
        im1.updatePoint(x, y)
        update_location_text(window["im1_text"], x, y)

    elif event == "im1_cap":
        im1.reset()
        update_location_text(window["im1_text"], None, None)
        if live.image is not None:
            im1.updateImage(live.image)

    # img 2
    elif event == "im2_graph":
        x, y = values['im2_graph'][0], values['im2_graph'][1]
        im2.updatePoint(x, y)
        window["im2_text"].Update(value=f"Location: ({x}, {y})")

    elif event == "im2_cap":
        update_location_text(window["im2_text"], None, None)
        im2.reset()
        if live.image is not None:
            im2.updateImage(live.image)

    # dataset
    elif event == "add":
        if any([i is None for i in [im1.image, im2.image, im1.location, im2.location]]):
            print("failed to add element")

        else:
            add_dataset_element(im1.image, im2.image, im1.location, im2.location)

            im1.reset()
            im2.reset()

            print("added element")

    # saving
    elif event == "save":
        path = window["save_location"].get()

        if os.path.dirname(path) == "" or os.path.isdir(os.path.dirname(path)):
            np.save(path, dataset)
            print(f"saved {len(dataset)} items to {path}")

        else:
            print(f"bad path, folder does not exits")

    # break the loop and close the window
    elif event == sg.WINDOW_CLOSED:
        break

window.close()
