#!/usr/bin/env python3
"""Graphical Elite Recovery companion. No shell or disk installation commands."""
import json
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext
from pathlib import Path
import companion


def main():
    root = tk.Tk()
    root.title('Elite Recovery — Device companion')
    root.geometry('900x700')
    root.configure(bg='#0f172a')
    events = queue.Queue()
    tk.Label(root, text='Elite Recovery', font=('Sans', 26, 'bold'), bg='#0f172a', fg='#6ee7b7').pack(pady=(20, 8))
    tk.Label(root, text='Identify this computer • Pair with your website • Review recovery options', bg='#0f172a', fg='white').pack()
    status = tk.StringVar(value='Reading this computer…')
    tk.Label(root, textvariable=status, wraplength=830, bg='#0f172a', fg='#6ee7b7').pack(pady=10)
    report_view = scrolledtext.ScrolledText(root, height=16, font=('Monospace', 10))
    report_view.pack(fill='both', expand=True, padx=24)
    tk.Label(root, text='On another device, open eliteitemlisting.pages.dev/#recovery and create a pairing code.', wraplength=830, bg='#0f172a', fg='white').pack(pady=(15, 5))
    code = tk.Entry(root, width=58, font=('Monospace', 12))
    code.pack(padx=24, fill='x')
    tk.Label(root, text='Pairing shares the hardware report above. No passwords or personal files are collected.', bg='#0f172a', fg='#cbd5e1').pack(pady=8)

    def ask(prompt, word):
        answer = queue.Queue()
        events.put(('confirm', (prompt, word, answer)))
        return answer.get()

    class Output:
        def write(self, value):
            if value.strip(): events.put(('status', value.strip()))
        def flush(self): pass

    def worker(value):
        try:
            companion.confirm = ask
            # companion print output is shown in the window, never in a terminal.
            companion.print = lambda *items, **kwargs: events.put(('status', ' '.join(map(str, items))))
            sys.argv = [sys.argv[0]]
            companion.main(code_provider=lambda: value)
            events.put(('stopped', 'Companion disconnected. Close and reopen to pair again.'))
        except Exception as error:
            events.put(('stopped', str(error)))

    def pair():
        value = code.get().strip()
        if not companion.re.fullmatch(r'[a-f0-9]{48}', value):
            messagebox.showerror('Pairing code', 'Paste the complete 48-character code from your signed-in Recovery Studio.')
            return
        button.configure(state='disabled'); code.configure(state='disabled')
        status.set('Connecting… Keep this window open while using Recovery Studio.')
        threading.Thread(target=worker, args=(value,), daemon=True).start()

    button = tk.Button(root, text='Pair this computer', command=pair, bg='#6ee7b7', padx=30, pady=8)
    button.pack(pady=8)
    if Path('/opt/ty-recovery').exists():
        def network():
            try: subprocess.Popen(['/usr/bin/nm-connection-editor'])
            except OSError as error: messagebox.showerror('Network settings', str(error))
        tk.Button(root, text='Wi-Fi / network settings', command=network).pack(pady=4)
    tk.Label(root, text='This toolkit prepares recovery. It does not erase disks or install an operating system.\nUSB boot selection may require the computer’s boot menu; not all models are supported.', bg='#0f172a', fg='#cbd5e1', wraplength=840).pack(pady=12)

    def load_report():
        try: events.put(('report', companion.hardware_report()))
        except Exception as error: events.put(('stopped', str(error)))

    def process():
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'confirm':
                    prompt, word, answer = value
                    answer.put(messagebox.askyesno('Approve ' + word.lower(), prompt + '\n\nApprove on this computer?', parent=root))
                elif kind == 'report':
                    report_view.insert('1.0', json.dumps(value, indent=2)); report_view.configure(state='disabled')
                    status.set(value['manufacturer'] + ' ' + value['model'])
                else:
                    status.set(value[:1000])
        except queue.Empty: pass
        root.after(150, process)

    def close():
        if messagebox.askyesno('Disconnect', 'Close the companion and disconnect this computer?', parent=root): root.destroy()
    root.protocol('WM_DELETE_WINDOW', close)
    threading.Thread(target=load_report, daemon=True).start()
    if '--self-test' in sys.argv:
        root.after(500, root.destroy)
    process(); root.mainloop()


if __name__ == '__main__': main()
