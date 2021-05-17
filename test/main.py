import keyboard
from kbana.analysis import Analysis
from kbana.capture import RecordingSession
import matplotlib.pyplot as plt
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
