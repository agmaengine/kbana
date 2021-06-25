from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesno
from kbana import quick_plot, load_recording, save_recording
from kbana.analysis import simulate_recording

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import queue
import threading
from functools import wraps


class ThreadReturn(queue.Queue):
    def result(self):
        try:
            value = self.get(block=False)
        except Exception as e:
            value = 'there is no result yet'
        return value


thread_return = ThreadReturn()


def thread_function(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        thread_return.put(f(*args, **kwargs))
    return wrapper


def _quick_plot(recording, status):
    if len(recording) == 0:
        status.set('The record is empty')
    else:
        fig, recording = quick_plot(recording, numeric='percent')
        fig.set_size_inches(12, 9)
        graph_frame = PopMatplotlibCanvas(fig)


class MenuBar(Menu):
    def __init__(self, master, status, analysis_frame, record_session):
        Menu.__init__(self, master)
        file_menu = Menu(self, tearoff=0)
        file_menu.add_command(label='Open text', command=self.open_text)
        file_menu.add_separator()
        file_menu.add_command(label='Export Recording', command=self.export_recording)
        file_menu.add_separator()
        file_menu.add_command(label='Quit', command=master.quit)
        tools_menu = Menu(self, tearoff=0)
        tools_menu.add_command(label='Visualize record', command=self.visualize_record)
        tools_menu.add_separator()
        tools_menu.add_command(label='Records key stroke', command=self.record_key_stroke)
        # tools_menu.add_command(label='Clear record', command=self.clear_record)
        self.add_cascade(label='File', menu=file_menu)
        self.add_cascade(label='Tools', menu=tools_menu)

        self.status = status
        self.text_input = analysis_frame.text_input
        self.analysis_frame = analysis_frame
        self.record_session = record_session

    def open_text(self):
        answer = askyesno('Warning', 'The currently input text will be deleted, do you want to continue?')
        if answer:
            self.status.set('Choose text file')
            path_to_file = askopenfilename()
            if path_to_file:
                with open(path_to_file, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.text_input.delete('1.0', END)
                self.text_input.insert('1.0', text)
            else:
                self.status.set('File is not selected')

    def export_recording(self):
        if self.analysis_frame.recording is not None:
            self.status.set("loading simulated record")
            recording = self.analysis_frame.recording
        else:
            self.status.set("simulating recording")
            text = self.analysis_frame.text_input_read()
            if text != 0:
                recording = simulate_recording(text, layout=self.analysis_frame.option_var.get())
            else:
                return 0
        if recording is not None:
            self.status.set("saving...")
            save_filename = asksaveasfilename(defaultextension=".pyd",
                                              filetypes=(("python dict", "*.pyd"), ("json", "*.json")))
            if save_filename == "":
                self.status.set("save file name is not specified")
            else:
                save_recording(recording, save_filename)
                self.status.set("Done")
                self.status.set("Ready")
        return 0

    def visualize_record(self):
        self.status.set('Choose record file')
        path_to_file = askopenfilename()
        records = load_recording(path_to_file)
        _quick_plot(records, self.status)

    def record_key_stroke(self):
        panel = RecordPanel(self.record_session, self.status)
        panel.record()

    def clear_record(self):
        self.record_session._recording = {}


class RecordPanel(Toplevel):
    def __init__(self, record_session, status):
        Toplevel.__init__(self)
        self.record_button = Button(self, text='record', command=self.toggle_record)
        self.record_button.configure(bg='#fdedec', fg='#000000', width=10, height=4)
        self.record_button.pack(pady=2.5)
        self.state = BooleanVar(value=False)
        action_frame = Frame(self)
        Button(action_frame, text='Save', command=self.save).pack(side=LEFT, fill=X, expand=True)
        Button(action_frame, text='Clear', command=self.clear).pack(side=LEFT, fill=X)
        action_frame.pack(fill=X, padx=2.5, pady=2.5)
        Button(self, text='visualize', command=self.visualize).pack(fill=X, padx=2.5, pady=2.5)

        self.status = status
        self.record_session = record_session
        self.thread = threading.Thread(target=self._record_coro)

    def toggle_record(self):
        if self.state.get():    # switch to idle state
            self.state.set(False)
            self.record_button.configure(text='record', bg='#fdedec', fg='#000000')
            self.record_button.update()
        else:
            self.state.set(True)    # switch to record state
            self.record_button.configure(text='stop', bg='#c0392b', fg='#FFFFFF')
            self.record_button.update()

    def save(self):
        # print(self.record_session.records)
        filename = asksaveasfilename()
        if filename != '':
            self.record_session.save_recording(filename)

    def clear(self):
        answer = askyesno("Warning", "You are about to remove all of records, do you want to continue?")
        if answer:
            self.record_session._recording = {}

    def visualize(self):
        _quick_plot(self.record_session.recording, self.status)

    @thread_function
    def _record_coro(self):
        return self.record_session.record()

    def record(self):
        if self.state.get():
            # if there is no result and thread is alive then pass
            # if these is result its mean thread is dead start new thread
            x = thread_return.result()
            # print(x)
            if not ((x != 0) and self.thread.is_alive()):
                # print(f"alive: {self.thread.is_alive()}")
                try:
                    self.thread.start()
                except RuntimeError:
                    self.thread = threading.Thread(target=self._record_coro)
                    self.thread.start()
        self.after(2, self.record)      # support up to 500 words/minute


class StatusBar(Frame):
    def __init__(self, master, status_stringvar):
        Frame.__init__(self, master)
        self.status_text = status_stringvar
        self.status_text.set("Ready")
        self.status = Label(textvariable=self.status_text, relief=RIDGE)
        self.status.config(anchor=E)
        self.status.pack(fill=X, padx=5, pady=2.5)

    def set(self, status_text):
        self.status_text.set(status_text)
        self.status.update()


class MatplotlibCanvas(Frame):
    def __init__(self, master, fig):
        Frame.__init__(self, master)
        canvas = FigureCanvasTkAgg(fig, master=self)  # A tk.DrawingArea.
        canvas.draw()

        # pack_toolbar=False will make it easier to use a layout manager later on.
        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.update()

        canvas.mpl_connect(
            "key_press_event", lambda event: print(f"you pressed {event.key}"))
        canvas.mpl_connect("key_press_event", key_press_handler)

        # button = Button(master=self, text="Quit", command=self.quit)

        # Packing order is important. Widgets are processed sequentially and if there
        # is no space left, because the window is too small, they are not displayed.
        # The canvas is rather flexible in its size, so we pack it last which makes
        # sure the UI controls are displayed as long as possible.
        # button.pack(side=BOTTOM)
        toolbar.pack(side=BOTTOM, fill=X)
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)


class PopMatplotlibCanvas(Toplevel):
    def __init__(self, fig):
        Toplevel.__init__(self)
        canvas = MatplotlibCanvas(self, fig)
        canvas.pack()
        self.title('Visualization')


class AnalyseFrame(Frame):
    def __init__(self, master, status):
        Frame.__init__(self, master)
        Label(self, text='Input Text').pack()
        self.status = status
        self.text_input = Text(self)
        self.text_input.pack(padx=5, pady=2.5, fill=BOTH)
        panel = Frame(self)
        layout_nest = Frame(panel)
        layout_option = ['qwerty', 'pattachoat', 'kedmanee']
        Label(layout_nest, text='Layout: ').pack(side=LEFT)
        self.option_var = StringVar()
        self.option_var.set(layout_option[0])
        self.layout_select = OptionMenu(layout_nest, self.option_var, *layout_option)
        self.layout_select.pack(side=LEFT)
        layout_nest.pack(fill=X, side=LEFT)
        analyse_button = Button(panel, text='Visualize', command=self.analyze, bg='#abebc6')
        analyse_button.pack(side=LEFT, fill=X, expand=TRUE, padx=2.5)
        clear_button = Button(panel, text='Clear', command=self.clear_text, bg='#f1948a')
        clear_button.pack(side=LEFT)
        panel.pack(padx=5, pady=2.5, fill=X)

        self.recording = None

    def text_input_read(self):
        text = self.text_input.get('1.0', END)
        # if the input text is blank text return '\n, if input text is blank terminate function'
        if text == '\n':
            message = 'Please input some characters'
            print(message)
            self.status.set(message)
            return 0
        return text

    def analyze(self):
        text = self.text_input_read()
        if text == 0:
            return 0
        self.status.set('Analyzing')
        # fig = quick_plot(text, layout=self.option_var.get(), numeric='percent')
        try:
            fig, self.recording = quick_plot(text, layout=self.option_var.get(), numeric='percent')
            fig.set_size_inches(12, 9)
            graph_frame = PopMatplotlibCanvas(fig)
        except Exception as e:
            print(e)
            self.status.set(e)
        else:
            self.status.set('Done')
            self.status.set('Ready')
        
    def clear_text(self):
        answer = askyesno('Warning', 'You are about to remove all text, do you want to continue?')
        if answer:
            self.text_input.delete('1.0', END)


def _on_key_release(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")

    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")

    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")
