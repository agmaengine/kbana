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
    mycmap = cmap
    mycmap._init()
    mycmap._lut[:,-1] = np.linspace(0, 0.8, n + 4)
    return mycmap


def _gaussian2d(coordinates, center, sigma_x, sigma_y):
    x, y = coordinates
    xo, yo = center
    a = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
    c = 1./(2*sigma_x**2) + 1./(2*sigma_y**2)
    g = np.exp( - (a*((x-xo)**2) + c*((y-yo)**2)))
    return g


def _load_keyboard_map(key_plot_map_directory):
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


def visualize_key_stroke(records, keyboard_style=None, keyboard_offset=(0, 0), exclude_key_list=[],
                         axis_handle=plt, numeric='freq', log_scale=False):
    """
    records is dictionary generated by RecordingSession
    plot True plot on matplotlib active plot otherwise create a new figure
    keyboard_offset is used if the keyboard_style key coordinates are not align keyboard image
        it is quick solution but directly editing the associated key_plot_map.json file is preferred

    log_scale:  if the frequency of key are more than 10 times different the linear scale will
    only shown the most frequently pressed keys to lower the sensitivity of linear scale log scale is used


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
        if k not in records:
            key_map[k] = (key_map[k], 0)
        else:
            value = records[k]
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


def visualize_finger_load(records, axis_handle=plt, numeric='freq'):
    """
    visualize finger load of key strokes records
    """
    finger_scode_map_json = os.path.dirname(__file__) + '/maps/finger_scode_map.json'
    with open(finger_scode_map_json, 'r') as f:
        finger_scode_map = json.load(f)
    # convert finger_scode_map key to int
    finger_scode_map_temp = {}
    for k in finger_scode_map:
        finger_scode_map_temp[int(k)] = finger_scode_map[k]
    finger_scode_map = finger_scode_map_temp

    # prepare finger_frequency
    total = 0
    finger_set = set(finger_scode_map.values())
    finger_frequency = {}
    for finger in finger_set:
        finger_frequency[finger] = 0
    for k in records:
        # exclude non character keys
        if k in finger_scode_map:
            finger = finger_scode_map[k]
            # calculate finger analysis
            value = records[k]
            finger_frequency[finger] += value
            total += value

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


def simulate_records(text, layout):
    """
    simulate keystroke of input text according to keyboard layout using scan code map
    layout options :
    Thai: kedmanee, pattachoat
    Endlish: qwerty

    Note: the space enter and shift keys are ignored
    """
    scode_name_map_path = os.path.dirname(__file__) + '/maps/scode_name_map.json'
    with open(scode_name_map_path, 'r') as f:
        scode_name_map = json.load(f)

    scode_name_map = scode_name_map[layout]
    records = {}
    for c in text:
        if c in scode_name_map:
            key_stroke = scode_name_map[c]
            if key_stroke in records:
                records[key_stroke] += 1
            else:
                records[key_stroke] = 1
    return records


def load_words_from_file(path_to_file, allow_duplicate=False):
    with open(path_to_file, 'r', encoding='utf-8') as f:
        words = f.read()
    words = words.split(' ')
    if not allow_duplicate:
        # because set cannot have duplicate values
        words = list(set(words))
    words = ' '.join(words)
    return words


class Analysis:
    def __init__(self, keyboard_style=None):
        if not keyboard_style:
            self.keyboard_style = os.path.dirname(__file__) + '/keyboard_styles/MainType/blank'

    def visualize_key_stroke_freq(self, records, *args, **kwargs):
        return visualize_key_stroke(records, self.keyboard_style, *args, **kwargs)

