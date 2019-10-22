#!/usr/bin/env python3

"""
https://trac.ffmpeg.org/wiki/Encode/H.264
"""

import os
import sys
import signal
import subprocess
from multiprocessing import Process
from threading import Thread

import tkinter as tk
from tkinter import filedialog, ttk


# ---/ Lib

def get_files(root_path: str) -> list:
    """Получает все файлы и возвращает их массив"""
    ext_filter = [".mts"]

    result = []

    root = os.path.abspath(root_path)
    with os.scandir(root) as listOfEntries:
        for entry in listOfEntries:
            if not entry.is_file():
                continue
            _, ext = os.path.splitext(entry.name)
            if ext not in ext_filter:
                continue
            result.append(entry.path)
    return result


def get_path_ffmpeg():
    bpath = "c:\\ffmpeg\\bin\\"
    if sys.platform == "win32":
        name = "ffmpeg.exe"
        return "{}{}".format(bpath, name)
    else:
        name = "ffmpeg"
        return name


def convert_mts_to_mp4(fin, fout):
    p = subprocess.Popen([
        get_path_ffmpeg(), '-i', str(fin),
        '-acodec', 'aac',
        '-ab', '320k',
        '-ac', '2',
        '-vcodec', 'libx264',
        '-crf', '23',
        # '-strict', '-2',
        # '-vpre', 'ipod640',
        # '-threads', '8',
        # '-s', '1280x720',
        # '-b:v', '2000k',
        # '-pass', '1',
        '-y',
        fout
    ])
    return p


def get_out_file(file, ext):
    head, tail = os.path.split(file)
    name, _ = os.path.splitext(tail)
    file_out = os.path.join(head, name + ext)
    return file_out


# ---/ Main

class Application(tk.Frame):

    def __init__(self):
        self.p_convert = None
        self.is_quit = False

        self.root = tk.Tk()
        self.root.title("Архив видео работ")
        self.root.geometry("460x200")
        self.root.resizable(False, False)

        super().__init__(self.root)

        self.path = tk.StringVar()

        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # ---
        btSelectFolder = tk.Button(
            master=self.root,
            text="Browse",
            command=self.bt_browse,
            width=10
        )

        lbPath = tk.Entry(
            master=self.root,
            textvariable=self.path,
            bd=1,
            bg='#ffffff',
            justify=tk.LEFT,
            width=35
        )

        lbPath.grid(row=0, column=0, sticky=tk.N + tk.W)
        btSelectFolder.grid(row=0, column=1, sticky=tk.N + tk.E)

        # --
        self.btStart = tk.Button(
            master=self.root,
            text="Начать",
            command=self.bt_start,
            width=10
        )
        self.btStart.grid(row=1, column=1, sticky=tk.E)

        # --
        self.btStop = tk.Button(
            master=self.root,
            text="Остановить",
            command=self.bt_stop,
            state=tk.DISABLED,
            width=10
        )
        self.btStop.grid(row=2, column=1, sticky=tk.E)

        # --
        ErLb = tk.Label(text="Состояние:")
        ErLb.grid(row=3, column=0, sticky=tk.W)

        self.ErText = tk.Text(
            width=45, height=6,
            fg='black', wrap=tk.WORD
        )
        self.ErText.grid(row=4)

    def on_closing(self):
        self.is_quit = True
        self.bt_stop()
        self.root.destroy()

    def bt_browse(self):
        name = filedialog.askdirectory()
        if name:
            self.path.set(name)

    def bt_start(self):
        self.btStart.configure(state=tk.DISABLED)
        self.btStop.configure(state=tk.ACTIVE)

        self.th = Thread(target=self.process)
        self.th.start()

    def bt_stop(self):
        if self.p_convert is not None:
            os.kill(self.p_convert.pid, signal.SIGTERM)

        self._ch_stop()

    def _ch_stop(self):
        """Изменить состояние"""
        if self.is_quit:
            return
        self.btStart.configure(state=tk.ACTIVE)
        self.btStop.configure(state=tk.DISABLED)

    def _write_log(self, msg):
        """Пишет в лог"""
        if self.is_quit:
            return
        self.ErText.insert(1.0, msg)
        self.ErText.insert(1.0, "\n")

    def process(self):
        is_error = False
        description = ""

        self.ErText.delete('1.0', tk.END)

        try:
            files = get_files(self.path.get())
        except FileNotFoundError as e:
            self._write_log("Указана не директория")
            self._ch_stop()
            return

        self._write_log("Найдено {} файлов".format(len(files)))

        # Bar

        for i, file in enumerate(files):
            self._write_log(
                "Началась обработка {}/{}: {}".format(i + 1, len(files), file)
            )
            file_out = get_out_file(file, ".mp4")
            self.p_convert = convert_mts_to_mp4(file, file_out)
            self.p_convert.wait()
            r = self.p_convert.returncode
            self.p_convert = None
            if r != 0:
                is_error = True
                break

        if is_error:
            self._write_log(
                "Произошла ошибка:\n{}".format(description)
            )
        else:
            self.ErText.insert(1.0, "Завершено успешно")

        self._ch_stop()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
