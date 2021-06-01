import keyboard
import json
import pickle
import os
import datetime
import copy
import ctypes


def get_keyboard_language():
    # only language not variant layout
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)
    lid = klid & (2 ** 16 - 1)
    lid_hex = f"{lid:#0{6}x}"
    root = os.path.dirname(__file__)
    with open(root + 'misc/win-language-id.json', 'r') as f:
        win_layout = json.load(f)
    return win_layout[lid_hex]


def load_records(filename):
    with open(filename, "rb") as f:
        records = pickle.load(f)
    return records


def flatten_records(records):
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
            records = load_records(self._filename)

        else:
            records = {True: {}, False: {}}
        self._records = records

    def record_key(self, key_event):
        record_book = self._records
        if key_event.event_type == 'up':
            k = key_event.scan_code
            if k in record_book[self._shift_state]:
                record_book[self._shift_state][k] += 1
            else:
                record_book[self._shift_state][k] = 1

    def shift_toggle(self):
        if self._shift_state:
            self._shift_state = False
        else:
            self._shift_state = True

    def save_recording(self):
        with open(self._filename, "wb") as f:
            pickle.dump(self._records, f)

    def records_key_only(self):
        records = self.records
        combined = records[False]
        shifted = records[True]
        for k in shifted:
            if k in combined:
                combined[k] += shifted[k]
            else:
                combined[k] = shifted[k]
        return combined

    # use property decorator so that user cannot directly modified records
    @property
    def records(self):
        return copy.deepcopy(self._records)

    @property
    def filename(self):
        return self._filename
