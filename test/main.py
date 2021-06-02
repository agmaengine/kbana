import keyboard

import kbana
from kbana.analysis import Analysis
from kbana.analysis import visualize_finger_load
from kbana.capture import RecordingSession
import matplotlib.pyplot as plt
rs = RecordingSession()
a = Analysis()

# def hold(keyboardEvent, key):
#     if key in keyboardEvent.name:
#         while True:
#             x = keyboard.read_event()
#             if not (key in x.name and x.event_type == 'down'):
#                 print(f"{x.scan_code} {x.name} {x.event_type} ")
#             if (key in x.name) and (x.event_type == 'up'):
#                 break

# layout = input('keyboard layout: ')
# print(f"keyboard layout: {layout}")
print("to start recording, press ctrl + r")
while True:
    x = keyboard.read_event()
    # print(x)
    if keyboard.is_pressed("ctrl + r"):
        # handling up event of r and ctrl keys super buggy though need improvement
        keyboard.read_event()
        keyboard.read_event()
        break
print("recording, press escape to stop recording")
language = kbana.get_keyboard_language()
while True:
    x = keyboard.read_event()
    # shift key hold
    if 'shift' in x.name:
        rs.shift_toggle()
        while True:
            x = keyboard.read_event()
            if ('shift' in x.name) and (x.event_type == 'up'):
                rs.shift_toggle()
                break
            elif not ('shift' in x.name and x.event_type == 'down'):
                # print(f"{x.scan_code} {x.name} {x.event_type} ")
                rs.record_key(x)
    # control key hold
    elif 'ctrl' in x.name:
        while True:
            x = keyboard.read_event()
            if ('ctrl' in x.name) and (x.event_type == 'up'):
                break
            elif not ('ctrl' in x.name and x.event_type == 'down'):
                # print(f"{x.scan_code} {x.name} {x.event_type} ")
                rs.record_key(x)
    # alternate key hold
    elif 'alt' in x.name:
        while True:
            x = keyboard.read_event()
            if ('alt' in x.name) and (x.event_type == 'up'):
                break
            elif ('shift' in x.name) and (x.event_type == 'up'):
                # print("change language")
                language = kbana.get_keyboard_language()
            elif not ('alt' in x.name and x.event_type == 'down'):
                # print(f"{x.scan_code} {x.name} {x.event_type} ")
                rs.record_key(x)
    # windows key hold
    elif 'windows' in x.name:
        while True:
            x = keyboard.read_event()
            if ('windows' in x.name) and (x.event_type == 'up'):
                break
            elif ('space' in x.name) and (x.event_type == 'up'):
                # print("change language")
                language = kbana.get_keyboard_language()
            elif not ('windows' in x.name and x.event_type == 'down'):
                # print(f"{x.scan_code} {x.name} {x.event_type} ")
                rs.record_key(x)

    # ordinary key stroke
    # print(f"{x.scan_code} {x.name} {x.event_type} ")
    rs.record_key(x)

    if keyboard.is_pressed("esc"):
        rs.save_recording()
        fig, ax = plt.subplots(2)
        a.visualize_key_stroke_freq(rs.records_key_only(),
                                    exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                                    axis_handle=ax[0], log_scale=True)
        visualize_finger_load(rs.records_key_only(), axis_handle=ax[1])

        # a.visualize_key_stroke_freq(rs.records_key_only(), plot=True)
        break
# plt.show()
print(rs.records)
