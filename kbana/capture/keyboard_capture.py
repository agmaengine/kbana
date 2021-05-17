import keyboard
import pickle
import os
import datetime
import copy


def load_records(filename):
    with open(filename, "rb") as f:
        records = pickle.load(f)
    return records


class RecordingSession:
    def __init__(self, filename=None, directory=None):
        self.time_stamp = datetime.datetime.now().strftime("%y_%m_%d-%H_%M_%S")
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
            records = {}
        self._records = records

    def record_key(self, key_event):
        record_book = self._records
        k = key_event.scan_code
        if k in record_book:
            record_book[k] += 1
        else:
            record_book[k] = 1

    def save_recording(self):
        with open(self._filename, "wb") as f:
            pickle.dump(self._records, f)

    # use property decorator so that user cannot directly modified records
    @property
    def records(self):
        return copy.deepcopy(self._records)

    @property
    def filename(self):
        return self._filename
