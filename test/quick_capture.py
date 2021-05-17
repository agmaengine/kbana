import keyboard
from kbana.analysis import Analysis
from kbana.capture import RecordingSession
import matplotlib.pyplot as plt
import argparse

# parser setup
prog_desc = """record key strokes and visualize their frequency, to start recording simply run this program 
                to stop recording press F11+F12"""
parser = argparse.ArgumentParser(description="record key stroke and visualize frequency")
parser.add_argument('--sdir', dest='save_directory', type=str, help='what ever')
args = parser.parse_args()


# main program
def main():
    rs = RecordingSession()
    a = Analysis()
    fig = plt.figure()
    while True:
        x = keyboard.read_event()
        if x.event_type == 'down':
            rs.record_key(x)
        if keyboard.is_pressed("F11+F12"):
            rs.save_recording()
            a.visualize_key_stroke_freq(rs.records, plot=True)
            break
    plt.show()
    print(rs.records)


if __name__ == "__main--":
    main()
