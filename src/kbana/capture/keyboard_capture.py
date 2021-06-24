import keyboard
import json
import pickle
import os
import datetime
import copy
import ctypes


def get_keyboard_language():
    """
    get current keyboard language
    os: windows
    """
    # only language not variant layout
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)
    lid = klid & (2 ** 16 - 1)
    lid_hex = f"{lid:#0{6}x}"
    root = os.path.dirname(__file__)
    with open(root + '/misc/win-language-id.json', 'r') as f:
        win_layout = json.load(f)
    return win_layout[lid_hex]


def load_recording(filename):
    with open(filename, "rb") as f:
        records = pickle.load(f)
    return records


def flatten_recording(records):
    records = records
    combined = records[False]
    shifted = records[True]
    for k in shifted:
        if k in combined:
            combined[k] += shifted[k]
        else:
            combined[k] = shifted[k]
    return combined


class RecordingSession:
    def __init__(self, filename=None, directory=None):
        self.time_stamp = datetime.datetime.now().strftime("%y_%m_%d-%H_%M_%S")
        self._shift_state = False
        if filename:
            # if filename is provided ignore directory
            self._filename = filename
        elif directory:
            if not os.path.exists(directory):
                os.mkdir(directory)
            if directory[-1] != '/':
                directory = directory + '/'
            self._directory = directory
            self._filename = directory + filename
        else:
            # if both are not provided generate filenames and records directory
            # relative to the file that call this module
            if not os.path.exists('./records'):
                os.mkdir('./records')
            self._filename = "./records/recordings-" + self.time_stamp + '.pyd'
        # if provided filename exists continue record from the recording otherwise create new records
        if os.path.exists(self._filename):
            recording = load_recording(self._filename)

        else:
            recording = {}
        self._recording = recording
        # list of key strokes
        self._recording_2 = []

    def _record_key_preserve_order(self, key_event):
        record_book = self._recording_2
        if key_event.event_type == 'up':
            k = key_event.scan_code
            record_book.append(k)

    def _shift_toggle_preserve_order(self, key_event):
        shift_key = key_event.scan_code
        if key_event.event_type == 'down':
            self._recording_2.append(shift_key)

    def _record_key_just_count(self, key_event):
        record_book = self._recording
        if key_event.event_type == 'up':
            k = key_event.scan_code
            if k in record_book:
                record_book[k] += 1
            else:
                record_book[k] = 1

    def _shift_toggle_just_count(self, key_event):
        shift_key = key_event.scan_code
        if key_event.event_type == 'down':
            if shift_key in self._recording:
                self._recording[shift_key] += 1
            else:
                self._recording[shift_key] = 1

    def _record_key(self, key_event, mode='just_count'):
        if mode == 'just_count':
            self._record_key_just_count(key_event)
        elif mode == 'preserve_order':
            self._record_key_preserve_order(key_event)

    def _shift_toggle(self, key_event, mode='just_count'):
        if mode == 'just_count':
            self._shift_toggle_just_count(key_event)
        if mode == 'preserve_order':
            self._shift_toggle_preserve_order(key_event)

    def record_built_in(self):
        while True:
            self.record()
            if keyboard.is_pressed("esc"):
                break

    def record(self):
        x = keyboard.read_event()
        # shift key hold
        if 'shift' in x.name:
            self._shift_toggle(x)
            while True:
                x = keyboard.read_event()
                if ('shift' in x.name) and (x.event_type == 'up'):
                    self._shift_toggle(x)
                    break
                elif not ('shift' in x.name and x.event_type == 'down'):
                    # print(f"{x.scan_code} {x.name} {x.event_type} ")
                    self._record_key(x)
        # control key hold
        elif 'ctrl' in x.name:
            while True:
                x = keyboard.read_event()
                if ('ctrl' in x.name) and (x.event_type == 'up'):
                    break
                elif not ('ctrl' in x.name and x.event_type == 'down'):
                    # print(f"{x.scan_code} {x.name} {x.event_type} ")
                    self._record_key(x)
        # alternate key hold
        elif 'alt' in x.name:
            while True:
                x = keyboard.read_event()
                if ('alt' in x.name) and (x.event_type == 'up'):
                    break
                elif ('shift' in x.name) and (x.event_type == 'up'):
                    # print("change language")
                    language = get_keyboard_language()
                elif not ('alt' in x.name and x.event_type == 'down'):
                    # print(f"{x.scan_code} {x.name} {x.event_type} ")
                    self._record_key(x)
        # windows key hold
        elif 'windows' in x.name:
            while True:
                x = keyboard.read_event()
                if ('windows' in x.name) and (x.event_type == 'up'):
                    break
                elif ('space' in x.name) and (x.event_type == 'up'):
                    # print("change language")
                    language = get_keyboard_language()
                elif not ('windows' in x.name and x.event_type == 'down'):
                    # print(f"{x.scan_code} {x.name} {x.event_type} ")
                    self._record_key(x)
        # ordinary key stroke
        # print(f"{x.scan_code} {x.name} {x.event_type} ")
        self._record_key(x)
        return 0

    def save_recording(self, filename=None):
        if filename:
            with open(filename, "wb") as f:
                pickle.dump(self._recording, f)
        else:
            with open(self._filename, "wb") as f:
                pickle.dump(self._recording, f)

    # def records_key_only(self):
    #     records = self.records
    #     combined = records[False]
    #     shifted = records[True]
    #     for k in shifted:
    #         if k in combined:
    #             combined[k] += shifted[k]
    #         else:
    #             combined[k] = shifted[k]
    #     return combined

    # use property decorator so that user cannot directly modified records
    @property
    def recording(self):
        return copy.deepcopy(self._recording)

    @property
    def filename(self):
        return self._filename
