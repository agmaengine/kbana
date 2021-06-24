import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.image as mpimg
from matplotlib import ticker
import pickle
import json
import os

# preferred .png format for more information
# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html
# https://matplotlib.org/stable/tutorials/introductory/images.html?highlight=mpimg
image_extension_list = ['.bmp', '.dib', '.eps', '.gif', '.icns', '.ico', '.im', '.jpeg', '.msp', '.pcx', '.png', 'ppm',
                   '.sgi', '.spider', '.tga', 'tiff', 'webp', '.xbm']


# code adapt from stackoverflow https://stackoverflow.com/questions/42481203/heatmap-on-top-of-image
def _transparent_cmap(cmap, n=255):
    """transparent heat map color map"""
    mycmap = cmap
    mycmap._init()
    mycmap._lut[:, -1] = np.linspace(0, 0.8, n + 4)
    return mycmap


def _gaussian2d(coordinates, center, sigma_x, sigma_y):
    """simple Gaussian function for visualization"""
    x, y = coordinates
    xo, yo = center
    a = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
    c = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
    g = np.exp( - (a*((x-xo)**2) + c*((y-yo)**2)))
    return g


def _load_keyboard_map(key_plot_map_directory):
    """keyboard style parser"""
    # directory input correction
    key_plot_map_file = None
    img_file = None
    if key_plot_map_directory[-1] != '/':
        key_plot_map_directory = key_plot_map_directory + '/'
    file_list = os.listdir(key_plot_map_directory)
    for file_name in file_list:
        if ".json" in file_name:
            key_plot_map_file = file_name
        elif os.path.splitext(file_name)[1].lower() in image_extension_list:
            img_file = file_name
    if key_plot_map_file and img_file:
        with open(key_plot_map_directory + key_plot_map_file, 'r') as f:
            key_plot_map = json.load(f)

        coor_key_map = {}
        coordinate = key_plot_map['coordinate']
        scan_code = key_plot_map['scan_code']
        for k in coordinate:
            row = coordinate[k]
            y = row[0]
            for i in range(len(row[1])):
                x = row[1][i]
                coor_key_map[scan_code[k][i]] = (y, x)

        kb_img = mpimg.imread(key_plot_map_directory + img_file)
        return coor_key_map, kb_img
    else:
        print("file(s) missing")


def visualize_key_stroke(recording, keyboard_style=None, keyboard_offset=(0, 0), exclude_key_list=[],
                         axis_handle=plt, numeric='freq', log_scale=False):
    """
    arguments
    recording (dict-like):    is dictionary generated by RecordingSession
                            (flatten current version of recording is not supported)
    keyboard_style (str):   specified plotted keyboard image (default: None)
                                options
                                'MainType/blank'
                                'MainType/Thai_Pattachoat_shift'
                                'MainType/Thai_Pattachoat_no_shift'
    keyboard_offset (tuple(int, int)):  specified offset when keyboard_style key coordinates
                                        are not align with keyboard image, it design as a quick solution
                                        but directly editing the associated key_plot_map.json file is preferred
                                        (default: (0, 0))
    exclude_key_list (list): list of scan_code which is not desired to be displayed (default: empty list)
    axis_handle (matplotlib.pyplot.Axes): 2d Axes which the visualize are drawn (default: matplotlib.pyplot)
    numeric (str): specifies numeric values are displayed on the plot. (default 'freq')
                options
                'prop': proportion
                'percent': percent
                'freq': frequency
    log_scale (bool):   specify weather to log the key stroke frequencies. being used when
                        the frequency of keys are more than 10 times different, the linear scale will
                        only shown the most frequently pressed keys to lower the sensitivity of linear scale.
                        (default: False)
    """
    # load key_map associated with keyboard_styles pictures
    if not keyboard_style:
        keyboard_style = os.path.dirname(__file__) + '/keyboard_styles/MainType/blank'
    key_map, kb_img = _load_keyboard_map(keyboard_style)

    # process record
    total = 0
    for k in exclude_key_list:
        key_map.pop(k)
    for k in key_map:
        if k not in recording:
            key_map[k] = (key_map[k], 0)
        else:
            value = recording[k]
            key_map[k] = (key_map[k], value)
            total += value

    h, w, d = kb_img.shape
    y, x = np.mgrid[0:h, 0:w]

    xy_z = list(key_map.values())
    zz = np.zeros_like(x)
    for m in xy_z:
        high = m[1]
        if high != 0:
            if log_scale:
                high = np.log10(high)
            x_offset, y_offset = keyboard_offset
            cy, cx = m[0]
            cx += x_offset
            cy += y_offset
            zz = zz + high * _gaussian2d((x, y), (cx, cy), .07 * x.max(), .07 * y.max())

    # Plot image and overlay colormap
    mycmap = _transparent_cmap(plt.cm.jet)
    axis_handle.imshow(kb_img)
    axis_handle.contourf(x, y, zz, 15, cmap=mycmap)
    # remove ticks
    axis_handle.set_xticks([])
    axis_handle.set_yticks([])
    # preparing label data
    value_label_dict = {'freq': [], 'prop': [], 'percent': []}
    for m in xy_z:
        xy = m[0]
        # frequency
        value_label_dict['freq'].append([xy, "%d" % m[1]])
        # proportion
        value_label_dict['prop'].append([xy, "%.3f" % (m[1]/total)])
        # percent
        value_label_dict['percent'].append([xy, "%.2f%%" % (m[1]*100/total)])
    for m in value_label_dict[numeric]:
        y, x = m[0]
        axis_handle.text(x, y, m[1], ha='center')
    return 0


def visualize_finger_load(recording, axis_handle=plt, numeric='freq', exclude_shift=True):
    """
    visualize finger load of key strokes recording by plotting

    arguments
    recording (dict-like): key stroke recording generated by kbana.capture.Recorder or kbana.analysis.simulate_recording
    axis_handle (matplotlib.pyplot.Axes):  2d Axes which the visualize are drawn (default: matplotlib.pyplot)
    numeric (str): specifies numeric values are displayed on the plot. (default 'freq')
                options
                'prop': proportion
                'percent': percent
                'freq': frequency
    exclude_shift (bool): specifies if shift key pressed are taken into account of the plot
    """
    finger_scode_map_json = os.path.dirname(__file__) + '/maps/finger_scode_map.json'
    with open(finger_scode_map_json, 'r') as f:
        finger_scode_map = json.load(f)
    # convert finger_scode_map key to int
    finger_scode_map_temp = {}
    for k in finger_scode_map:
        finger_scode_map_temp[int(k)] = finger_scode_map[k]
    finger_scode_map = finger_scode_map_temp
    if exclude_shift:
        # remove left shift
        finger_scode_map.pop(42)
        # remove right shift
        finger_scode_map.pop(54)

    # prepare finger_frequency
    total = 0
    finger_set = set(finger_scode_map.values())
    finger_frequency = {}
    for finger in finger_set:
        finger_frequency[finger] = 0
    for k in recording:
        # exclude non character keys
        if k in finger_scode_map:
            finger = finger_scode_map[k]
            # calculate finger analysis
            value = recording[k]
            finger_frequency[finger] += value
            total += value

    if total == 0:
        raise Exception("The record is empty")

    finger_image_path = os.path.dirname(__file__) + '/misc/hands.png'
    hands = mpimg.imread(finger_image_path)
    h, w, d = hands.shape
    # create grid array
    y, x = np.mgrid[0:h, 0:w]
    z = np.zeros_like(x)

    finger_points = {'l_pinky': (145, 384),
                     'r_pinky': (1264, 384),
                     'l_ring': (225, 211),
                     'r_ring': (1179, 211),
                     'l_middle': (350, 154),
                     'r_middle': (1059, 154),
                     'l_index': (498, 199),
                     'r_index': (905, 199)}

    # color map
    mycmap = _transparent_cmap(plt.cm.jet)
    # plot hands
    # hand load
    left = 0
    right = 0
    axis_handle.imshow(hands)
    # value_label_dict = {'freq': [], 'prop': [], 'percent': []}
    for finger in finger_frequency:
        high = finger_frequency[finger]
        finger_coordinate = finger_points[finger]
        if numeric == "prop":
            axis_handle.text(*finger_coordinate, "%.3f" % (high/total))
        elif numeric == 'percent':
            axis_handle.text(*finger_coordinate, "%.2f%%" % (high*100 / total))
        elif numeric == 'freq':
            axis_handle.text(*finger_coordinate, "%d" % high)
        if finger[0] == 'l':
            left += high
        elif finger[0] == 'r':
            right += high
        z = z + high * _gaussian2d((x, y), finger_points[finger], .04 * x.max(), .04 * y.max())
    # plot hand loads
    left_xy = (317, 655)
    right_xy = (1083, 655)
    value_hand_label_dict = {
        'prop': [
            [left_xy, "%.3f" % (left/total)], [right_xy, "%.3f" % (right/total)]
        ], 'percent': [
            [left_xy, "%.2f%%" % (left * 100 / total)], [right_xy, "%.2f%%" % (right * 100 / total)]
        ], 'freq': [
            [left_xy, "%d" % (left)], [right_xy, "%d" % (right)]
        ]}
    for m in value_hand_label_dict[numeric]:
        axis_handle.text(*m[0], m[1], ha='center')

    axis_handle.contourf(x, y, z, 15, cmap=mycmap)
    # remove ticks
    axis_handle.set_xticks([])
    axis_handle.set_yticks([])
    return finger_frequency


def simulate_recording(text, layout):
    """
    simulate keystroke of input text according to keyboard layout using scan code map
    Note : space and enter are ignored

    arguments
    text (str): a string of characters
    layout  (str): specify layout to simulate input data currently support layout options are
                Thai: 'kedmanee', 'pattachoat'
                Endlish: 'qwerty'
    """
    if layout is None:
        raise ValueError("layout must be stringType")
    scode_name_map_path = os.path.dirname(__file__) + '/maps/scode_name_map.json'
    with open(scode_name_map_path, 'r') as f:
        scode_name_map = json.load(f)

    shift_key_name_map_path = os.path.dirname(__file__) + '/maps/shift_key_name_map.json'
    with open(shift_key_name_map_path, 'r') as f:
        shift_key_name_map = json.load(f)

    scode_name_map = scode_name_map[layout]
    # enable simulate shift key pressed in available layout
    if layout in shift_key_name_map:
        shift_key_name_map = shift_key_name_map[layout]
    else:
        shift_key_name_map = None
    recording = {}
    c_previous = None
    for c in text:
        # if simulate shift key is available then simulate shift key pressed
        if shift_key_name_map is not None:
            # verify if the character is shifted character
            if c in shift_key_name_map:
                shift_key = shift_key_name_map[c]
                # if previous character is not None
                if c_previous is not None:
                    # if previous character is not shifted character or
                    # previous character is shifted character but shift key is in the opposite hand
                    if c_previous not in shift_key_name_map:
                        # record shift key pressed
                        if shift_key in recording:
                            recording[shift_key] += 1
                        else:
                            recording[shift_key] = 1
                    elif c_previous in shift_key_name_map:
                        shift_key_previous = shift_key_name_map[c_previous]
                        if shift_key_previous != shift_key:
                            if shift_key in recording:
                                recording[shift_key] += 1
                            else:
                                recording[shift_key] = 1
                # if first character are shifted character
                else:
                    if shift_key in recording:
                        recording[shift_key] += 1
                    else:
                        recording[shift_key] = 1
                # other wise assume shift is held
        # map character into scan code
        if c in scode_name_map:
            key_stroke = scode_name_map[c]
            if key_stroke in recording:
                recording[key_stroke] += 1
            else:
                recording[key_stroke] = 1

        c_previous = c
    if len(recording) == 0:
        raise Exception('none of input text characters are recognized in this layout')
    return recording


def load_words_from_file(path_to_file, allow_duplicate=False):
    """
    load words which are contained in text file and removes duplicates only works if each words are separated.

    arguments
    path_to_file (str): absolute path to text file
    allow_duplicate (bool): leaves duplicated words as is (default False) set as True when loading articles
    """
    with open(path_to_file, 'r', encoding='utf-8') as f:
        words = f.read()
    words = words.split(' ')
    if not allow_duplicate:
        # because set cannot have duplicate values
        words = list(set(words))
    words = ' '.join(words)
    return words


class Analysis:
    """
    class for gui development
    """
    def __init__(self, keyboard_style=None):
        if not keyboard_style:
            self.keyboard_style = os.path.dirname(__file__) + '/keyboard_styles/MainType/blank'

    def visualize_key_stroke(self, recording, axis_handle=plt, *args, **kwargs):
        return visualize_key_stroke(recording, self.keyboard_style, axis_handle=axis_handle, *args, **kwargs)

