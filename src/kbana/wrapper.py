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
        recording = text
    elif type(text) == str:
        recording = simulate_recording(text, layout)
    else:
        raise ValueError('text must be stringType or dictionaryType')
    fig = plt.figure()
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(223)
    ax3 = plt.subplot(224)
    visualize_key_stroke(recording, log_scale=False, axis_handle=ax1,
                         exclude_key_list=[29, 91, 56, 57, 14, 42, 54, 15, 58, 28, 'n/a'],
                         numeric=numeric)
    ax1.set_title("key stroke on keyboard")
    visualize_finger_load(recording, axis_handle=ax2, numeric=numeric, exclude_shift=False)
    ax2.set_title("finger load include shift key press")
    visualize_finger_load(recording, axis_handle=ax3, numeric=numeric, exclude_shift=True)
    ax3.set_title("finger load exclude shift key press")
    return fig, recording
