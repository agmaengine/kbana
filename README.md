# kbana
keyboard keystroke recorder and analysis packages, the keystroke recorder related classes and functions are collected 
in **capture module**, analysis tools are collected in **analysis module**. Currently, the analysis module 
has only visualization of keystroke on keyboard and finger load. 

## Installation

PYPI<br>
`pip install kbana`

from git repository<br>
`git clone https://github.com/agmaengine/kbana.git` <br>
`pip install .`

## kbana.capture
### Recorder(filename=None, directory=None)
if recording file is exists then increment the existing recording<br>
if recording file is not exists then creating new recording file when save_recording is called<br>
if recording file is provided directory is ignored<br>
if directory is provided create directory if not exists. When save_recording is called, Recorder saves recording<br>
with timestamps, when the Recorder is constructed, to the directory.<br>
if none is provided, create records directory in the directory where the module is called.<br>
When save_recording is called, Recorder saves recording with timestamps, when the Recorder is constructed,<br>
to the directory.<br>

**filename** (str): path to recording file (default: None)<br>
**directory** (str): path to recording directory (default: None)

_kbana.capture.Recorder.**record()**_<br>
record a single keystroke

_kbana.capture.Recorder.**record_built_in()**_<br>
continuously record keystrokes, stop when pressing esc

_kbana.capture.Recorder.**save_recording(filename=None)**_<br>
if filename is provided save recording to the filename, otherwise the behavior determined when Recorder is constructed
**filename** (str): recording save file name

_kbana.capture.Recorder.**recording**_<br>
return copy of recording

_kbana.capture.Recorder.**filename**_<br>
return copy of filename

## kbana.analysis
kbana.analysis._**visualize_key_stroke(recording, keyboard_style=None, keyboard_offset=(0, 0), exclude_key_list=[],
                         axis_handle=plt, numeric='freq', log_scale=False)**_

visualize keystroke on keyboard

keyboard_style options
* 'MainType/blank'
* 'MainType/Thai_Pattachoat_shift'
* 'MainType/Thai_Pattachoat_no_shift'

numeric options
* 'prop': proportion
* 'percent': percent
* 'freq': frequency

kbana.analysis._**visualize_finger_load(recording, axis_handle=plt, numeric='freq', exclude_shift=True)**_

visualize finger load

numeric options
* 'prop': proportion
* 'percent': percent
* 'freq': frequency

kbana.analysis._**simulate_recording(text, layout)**_

**text** (str)

simulate recording from input text

layout options
* English
  * 'qwerty'
* Thai
  * 'kedmanee'
  * 'pattachoat'

kbana.analysis._**load_words_from_file(path_to_file, allow_duplicate=False)**_

read list of word from text file. if words are separated by space, remove duplicated word.

return text (str)


# Add more keyboard styles
add your style directory in kbana/analysis/keyboard_styles
file structure should be

analysis/keyboard_styles
  /keyboard_conifuration
    /keyboard_layout

in keyboard_layout includes your keyboard image (PNG format is preferred) and key_plot_map.json the detail is in kbana/analysis/keyboard_styles/key_plot_map_meta.txt
