# kbana
keyboard key stroke recording and analysis modules

## there are two classes
kbana.**capture.RecordingSession** <br>
kbana.**analysis.Analysis**

kbana.capture.RecordingSession is used for managing recording's save-directory, and record keyboard.KeyboardEvent the recording is stores as dictionary of keystroke scan code

kbana.analysis.Analysis is used for visualizing and anlysing keystroke records from the kbana.capture.RecordingSession and also managing configuration of visualizing keyboard style

for quick usage see test/main.py

## kbana.capture.RecordingSession(filename=None, directory=None)

**filename**: records file name <br>
**directory**: records saving directory

filename and directory determined the behavior of **kbana.capture.RecordingSession.save_recording** method if filename is provided the **RecordingSession** will continue record key stroke to the file, if directory is provided the **RecordSession** will save each records into the directory with timestamp, if both filename and directory are provided directory will be ignored, else **RecordingSession** will save records with timestamp to the records directory relative to the file the object is called

### Methods
### kbana.capture.RecordingSession.record_key(keyboard.KeyboardEvent)
### kbana.capture.RecordingSession.save_recording()

### properties
### kbana.capture.RecordingSession.records
### kbana.capture.RecordingSession.filename

## kbana.analysis.Analysis(keyboard_style=None)

### methods
### kbana.analysis.Analysis.visualize_key_stroke_freq(records, *args, **kwargs)

see **kbana.analysis.visualize_key_stroke_freq()**

## generic functions
### kbana.capture.load_records(filename)

input
**filename**: records file name
output
**records**: records dict

### kbana.analysis.visualize_key_stroke_freq(records, keyboard_style=None, keyboard_offset=(0, 0), plot=False)

input
**records**: records from RecordingSesstion
return
if plot is Flase
**matplotlib.pyplot.figure**: plot for heatmap of key stroke frequency on keyboard
if plot is True
**0** and just plot on matplotlib.pyplot active axes

# Add more keyboard styles
add your style directory in kbana/analysis/keyboard_styles
file structure should be

analysis/keyboard_styles
  /keyboard_conifuration
    /keyboard_layout

in keyboard_layout includes your keyboard image (PNG format is preferred) and key_plot_map.json the detail is in kbana/analysis/keyboard_styles/key_plot_map_meta.txt
