import keyboard

import kbana
from kbana.analysis import Analysis
from kbana.capture import RecordingSession
import matplotlib.pyplot as plt
rs = RecordingSession()
a = Analysis()
fig = plt.figure()

# def hold(keyboardEvent, key):
#     if key in keyboardEvent.name:
#         while True:
#             x = keyboard.read_event()
#             if not (key in x.name and x.event_type == 'down'):
#                 print(f"{x.scan_code} {x.name} {x.event_type} ")
#             if (key in x.name) and (x.event_type == 'up'):
#                 break
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

    if keyboard.is_pressed("F11+F12"):
        rs.save_recording()
        a.visualize_key_stroke_freq(rs.records_key_only(), exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                                    plot=True, log_scale=True)
        # a.visualize_key_stroke_freq(rs.records_key_only(), plot=True)
        break
plt.show()
print(rs.records)
