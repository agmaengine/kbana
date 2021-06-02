import matplotlib.pyplot as plt
from .analysis import visualize_key_stroke_freq, visualize_finger_load, simulate_records

def quick_plot(text, layout):
    """
    text: string
    layout: string
    support layouts
    Thai: kebmanee, pattachoat
    English: qwerty

    please specify layout so that input text can be mapped to scan codes associated to the layout
    """
    records = simulate_records(text, layout)
    fig, ax = plt.subplots(2)
    visualize_key_stroke_freq(records, log_scale=False, axis_handle=ax[0])
    visualize_finger_load(records, axis_handle=ax[1])
    return 0
