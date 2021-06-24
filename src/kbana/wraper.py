import matplotlib.pyplot as plt
from .analysis import visualize_key_stroke, visualize_finger_load, simulate_recording


def quick_plot(text, layout=None, numeric='freq'):
    """
    text (str, dict):
    layout (str):
    support layouts
        Thai: kebmanee, pattachoat
        English: qwerty

    please specify layout so that input text can be mapped to scan codes associated to the layout
    """
    if type(text) == dict:
        records = text
    elif type(text) == str:
        records = simulate_recording(text, layout)
    else:
        raise ValueError('text must be stringType or dictionaryType')
    fig, ax = plt.subplots(2)
    visualize_key_stroke(records, log_scale=False, axis_handle=ax[0],
                         exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                         numeric=numeric)
    visualize_finger_load(records, axis_handle=ax[1], numeric=numeric)
    return fig
