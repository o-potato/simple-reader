import tkinter as tk
from tkinter import *
from tkinter import messagebox
from client import info
from protocol.transmission import send_message
from protocol.message_type import MessageType
from protocol.transmission import recv_message
from client.APIs.HomePage import HomePageForm
from client.APIs.signup import SignupForm


class LoginForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.create_form()
        self.s = info.s
        master.protocol("WM_DELETE_WINDOW", self.destroy_window)

    def create_form(self):
        self.master.resizable(width=False, height=False)
        self.master.geometry('300x100')
        self.master.title("My Book Reader -- Login")

        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")

        self.username = Entry(self)
        self.password = Entry(self, show='*')

        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)

        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))

        self.buttonframe = Frame(self)
        self.buttonframe.grid(row=2, column=0, columnspan=2, pady=(4, 6))
        self.logbtn = Button(self.buttonframe, text="登录", command=self.do_login)
        self.logbtn.grid(row=0, column=0)
        self.signupbtn = Button(self.buttonframe, text="注册", command=self.show_signup)
        self.signupbtn.grid(row=0, column=1)

        self.pack()

    def do_login(self):
        username = self.username.get()
        password = self.password.get()
        if not username:
            messagebox.showerror("Error", "username can not be blank")
            return
        if not password:
            messagebox.showerror("Error", "password can not be blank")

        send_message(self.s, MessageType.login, [username, password])
        print("登录请求已发送")

        msg = recv_message(self.s)
        if not msg:
            messagebox.showerror("Error", "connection wrong")
            self.destroy_window()
            return

        if msg[type] == MessageType.loginFailed:
            messagebox.showerror("登录失败", "用户名或密码错误！")
            return

        if msg[type] == MessageType.loginSucc:
            info.current_user = username
            print("登录成功")
            self.master.destroy()
            homepage = Toplevel(info.tk_root, takefocus=True)
            HomePageForm(homepage)
            return

    def show_signup(self):
        signup_form = Toplevel()
        SignupForm(master=signup_form)

    def destroy_window(self):
        info.tk_root.destroy()
