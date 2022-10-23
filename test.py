import logging

import PIL.ImageShow
import PySimpleGUI as sg
import numpy as np

from PIL import Image
from io import BytesIO

import numpy

test_img = np.asarray(Image.open("im1.jpg"))


# GameMenu = [[sg.Column([
#     [sg.Text('roomName', size=(20, 1), key='RoomName', visible=False)],
#     [sg.Text('roomDescription', size=(20, 5), key='RoomDescription', visible=False)],
#     [sg.Button('North', key='NorthButton', visible=False)],
#     [sg.Button('East', key='EastButton', visible=False)],
#     [sg.Button('South', key='SouthButton', visible=False)],
#     [sg.Button('West', key='WestButton', visible=False)],
#     [sg.Button('Back to MainMenu', key='Back', visible=True)],
# ])]]
#
# # MAIN MENU #
# # the layout box that lets you select what gameSave you want to play in
# GameSaveSelector = [
#     [sg.Listbox(findGamePaths(), select_mode='LISTBOX_SELECT_MODE_SINGLE', size=(10, 10), key='GameSavesListBox')],
#     [sg.Button('Ok', key='GameSaveSelectButton')],
#     [sg.Text(findGamePaths()[0], size=(20, 1), key='SelectedGameSave')],
#     [sg.Sizer(250, 100)]]
#
# # the buttons that take you to the edit menu or start the game
# MainMenuOptions = [[sg.Text('WELCOME TO CHOOSE YOUR OWN ADVENTURE')],
#                    [sg.Button('Start Game', key='StartGame')],
#                    [sg.Button('Edit Saves', key='EditSaves')],
#                    [sg.Sizer(750, 400)]]
#
# # the layout that will be displayed in the main menu
# MainMenu = [[sg.Frame('Choose Save File:', GameSaveSelector, vertical_alignment='t'),
#              sg.Column(MainMenuOptions, element_justification='center', vertical_alignment='c')],
#             [sg.Column([[sg.Button('Exit')]], size=(1000, 100), element_justification='right')]]
#
# # EDIT MENU #
# # the listbox that lets you select what database you want to edit
# # also lets you create new databases
# DatabaseSelector = [
#     [sg.Listbox(findGamePaths(), select_mode='LISTBOX_SELECT_MODE_SINGLE', size=(10, 10), key='DataBaseListBox')],
#     [sg.Button('Ok', key='SelectDatabase')],
#     [sg.Input(size=(16, 1), key='NewDatabaseName'), sg.Button('New', key='CreateNewDatabase')]]
#
# # the listbox that lets you select what room you want to edit
# RoomSelector = [[sg.Listbox(list(editorLevelInfo.keys())[:-1], select_mode='LISTBOX_SELECT_MODE_SINGLE', size=(10, 10),
#                             key='RoomSelectorListBox')],
#                 [sg.Button('Ok', key='SelectRoom')],
#                 [sg.Button('New Room', key='CreateNewRoom')]]
#
# # the input field to set the new room values
# # the button to save the values
# RoomEditor = [[sg.Text(editorSave, key='SaveName', size=(20, 1))],
#
#               [sg.Column([
#                   [sg.Text('Room Id:', size=(16, 1)), sg.Text('id', key='RoomIdText', size=(16, 1))],
#                   [sg.Text('Room Name', size=(16, 1)), sg.Input(size=(16, 1), key='RoomNameInput')],
#                   [sg.Text('Room Description', size=(16, 1)), sg.Input(size=(16, 1), key='RoomDescriptionInput')]],
#                   element_justification='right')],
#
#               [sg.Column([
#                   [sg.Text('Connections (input a room id)')],
#                   [sg.Text('North', size=(16, 1)), sg.Input(size=(16, 1), key='NorthConnectionInput')],
#                   [sg.Text('East', size=(16, 1)), sg.Input(size=(16, 1), key='EastConnectionInput')],
#                   [sg.Text('South', size=(16, 1)), sg.Input(size=(16, 1), key='SouthConnectionInput')],
#                   [sg.Text('West', size=(16, 1)), sg.Input(size=(16, 1), key='WestConnectionInput')]],
#                   element_justification='center')],
#
#               [sg.Button('Submit Changes', key='SubmitChanges')],
#               [sg.Button('Back to Main Menu', key='Back')]]
#
# # the layout that will be displayed in the edit menu
# EditMenu = [[sg.Column(DatabaseSelector, size=(200, 500)),
#              sg.Column(RoomEditor, size=(600, 500), element_justification='center'),
#              sg.Column(RoomSelector, size=(200, 500))]]
#
# # all the layouts that will be used in the game
# layout = [[sg.Column(MainMenu, size=(1000, 500), key='MainMenu', visible=True),
#            sg.Column(EditMenu, size=(1000, 500), key='EditMenu', visible=False),
#            sg.Column(GameMenu, size=(1000, 500), key='GameMenu', visible=False)]]

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

    def updateImage(self, arr):
        if self.image is not None:
            self.graph.delete_figure(self.image_id)

        self.image = arr
        self.image_id = self.graph.draw_image(data=array_to_data(arr))

    def updatePoint(self, x, y):
        # if self.image_id is None:
        #     return

        if self.location is not None:
            self.graph.delete_figure(self.location_id)

        self.location = (x, y)
        self.location_id = self.graph.draw_point((x, y), 5, "black")


live = ImageViewer(0, 0, 300, 300, "live_graph")
live_col = sg.Column([[sg.Text("live view")], [live.graph]])

w, h = 400, 400

graph = sg.Graph(
            canvas_size=(w, h),
            graph_bottom_left=(0, h),
            graph_top_right=(w, 0),
            enable_events=True,  # mouse click events
            background_color='white')

window = sg.Window('ROS IMAGES SELECTOR', layout=[[graph]],  margins=(100, 100), element_justification="c")
window.finalize()

print(graph.draw_image(location=(0, 0), filename="img.png"))
print(test_img)
# game loop
while True:
    event, values = window.read()
    print(event, values)


    # break the loop and close the window
    if event == sg.WINDOW_CLOSED:
        break

window.close()
