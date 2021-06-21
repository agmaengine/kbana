import matplotlib.pyplot as plt
from .analysis import visualize_key_stroke, visualize_finger_load, simulate_records


def quick_plot(text, layout, numeric='freq'):
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
    visualize_key_stroke(records, log_scale=False, axis_handle=ax[0],
                         exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                         numeric=numeric)
    visualize_finger_load(records, axis_handle=ax[1], numeric=numeric)
    return 0
