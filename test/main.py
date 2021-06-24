import keyboard
import kbana
from kbana.analysis import Analysis
from kbana.analysis import visualize_finger_load
from kbana.capture import Recorder
import matplotlib.pyplot as plt


def simple_record_interface():
    rs = Recorder()
    a = Analysis()

    # application response
    print("to start recording, press ctrl + r")
    while True:
        x = keyboard.read_event()
        if keyboard.is_pressed("ctrl + r"):
            # handling up event of r and ctrl keys super buggy though need improvement
            keyboard.read_event()
            keyboard.read_event()
            break
    print("recording, press escape to stop recording")
    # language = kbana.get_keyboard_language()

    rs.record()
    rs.save_recording()
    fig, ax = plt.subplots(2)
    a.visualize_key_stroke(rs.recording,
                           exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                           axis_handle=ax[0], log_scale=True)
    visualize_finger_load(rs.recording, axis_handle=ax[1])
    print(rs.recording)


if __name__ == '__main__':
    simple_record_interface()
