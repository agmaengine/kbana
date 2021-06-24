import keyboard
import kbana
from kbana.analysis import Analysis
from kbana.analysis import visualize_finger_load
from kbana.capture import RecordingSession
import matplotlib.pyplot as plt
from tkinter import *
from tkinter.filedialog import *
from gui_element import MenuBar, StatusBar, AnalyseFrame


def cli():
    rs = RecordingSession()
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

    rs.record_built_in()
    rs.save_recording()
    fig, ax = plt.subplots(2)
    a.visualize_key_stroke(rs.records,
                           exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                           axis_handle=ax[0], log_scale=True)
    visualize_finger_load(rs.records, axis_handle=ax[1])
    print(rs.records)


def gui():
    rs = RecordingSession()
    root = Tk()
    root.title('kbana')
    status_text = StringVar()
    analyze_f = AnalyseFrame(root, status_text)
    analyze_f.pack(fill=BOTH)
    status_bar = StatusBar(root, status_text)
    status_bar.pack(fill=X, anchor=S)
    menu_bar = MenuBar(root, status_text, analyze_f.text_input, rs)
    root.config(menu=menu_bar)
    root.mainloop()


if __name__ == '__main__':
    gui()
