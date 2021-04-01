import tkinter as tk
from tkinter import *
from tkinter import messagebox
from client import info
from protocol.transmission import send_message
from protocol.message_type import MessageType
from protocol.transmission import recv_message


class SignupForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_form()
        self.s = info.s

    def create_form(self):
        self.master.resizable(width=False, height=False)
        self.master.geometry('300x140')
        self.master.title("My Book Reader -- sign up")

        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")
        self.label_3 = Label(self, text="确认密码")

        self.username = Entry(self)
        self.password = Entry(self, show='*')
        self.password_confirm = Entry(self, show='*')

        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.label_3.grid(row=2, sticky=E)

        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))
        self.password_confirm.grid(row=2, column=1, pady=(0, 6))

        self.btn = Button(self, text="注册", command=self.do_signup)
        self.btn.grid(row=4, column=0, columnspan=2)

        self.pack()

    def do_signup(self):
        username = self.username.get()
        password = self.password.get()
        password_confirm = self.password_confirm.get()

        if not username:
            messagebox.showerror("Error", "username can not be blank")
            return
        if not password or not password_confirm:
            messagebox.showerror("Error", "password can not be blank")
            return
        if password != password_confirm:
            messagebox.showerror("Error", "passwords are not the same")
            return

        send_message(self.s, MessageType.signup, [username, password])
        msg = recv_message(self.s)
        if not msg:
            messagebox.showerror("Error", "connection wrong")
            return
        if msg['type'] == MessageType.usernameTaken:
            messagebox.showerror("Error", "the username has been used")
            return
        if msg['type'] == MessageType.signupSucc:
            messagebox.showerror("注册成功！")
            self.master.destroy()
            return
