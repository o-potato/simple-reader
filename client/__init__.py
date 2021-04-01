import tkinter as tk
from tkinter import messagebox
import client.info
import socket
from client.APIs.login import LoginForm


def init_client():
    root = tk.Tk()
    client.info.tk_root = root

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(client.info.ADDR)
        client.info.s = s
    except ConnectionError:
        messagebox.showerror("Error", "can not connect the server")
        exit(1)

    login = tk.Toplevel(root)
    LoginForm(master=login)

    root.withdraw()
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass
