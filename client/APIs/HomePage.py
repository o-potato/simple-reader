import tkinter as tk
from tkinter import *
from tkinter import messagebox
from client import info
from protocol.transmission import send_message
from protocol.transmission import recv_message
from protocol.message_type import MessageType
from client.APIs.ReadPage import ReaderForm
from tkinter.filedialog import askdirectory
from protocol.transmission import recv_file


class HomePageForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(self, master=None)
        self.master = master
        self.s = info.s
        self.create_form()
        master.protocol("WM_DELETE_WINDOW", self.destroy_window)

    def create_form(self):
        self.master.title("Home Page")

        self.scrb = Scrollbar(self)
        self.scrb.pack(side=RIGHT, fill=Y)

        self.book_list = Listbox(self, height=15, width=30, yscrollcommand=self.scrb.set)
        bklist = self.get_booklist()
        for bkname in bklist:
            self.book_list.insert(END, bkname)
        self.book_list.pack(side=RIGHT, fill=BOTH, expand=YES)

        self.scrb.config(command=self.book_list.yview)

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=LEFT, fill=BOTH, expand=YES)
        self.refreshbtn = Button(self.buttonframe, text="刷新", command=self.refresh)
        self.refreshbtn.pack(side=TOP, fill=Y, expand=YES)
        self.readbtn = Button(self.buttonframe, text="阅读", command=self.read)
        self.readbtn.pack(side=TOP, fill=Y, expand=YES)
        self.downloadbtn = Button(self.buttonframe, text="下载", command=self.download)
        self.downloadbtn.pack(side=TOP, fill=Y, expand=YES)

        self.pack()

    def get_booklist(self):
        send_message(self.s, MessageType.requireList)
        msg = recv_message(self.s)
        if not msg:
            messagebox.showerror("Error", "connection wrong")
            return
        if msg['type'] == MessageType.bookList:
            return msg['parameters']
        else:
            messagebox.showerror("请求失败", "服务器未返回书籍列表")
            return

    def refresh(self):
        self.book_list.delete(0, END)
        booklist = self.get_booklist()
        for bookname in booklist:
            self.book_list.insert(END, bookname)

    def read(self):
        bookname = self.book_list.get(self.book_list.curselection())
        reader = Toplevel(info.tk_root, takefocus=True)
        ReaderForm(bookname, reader)
        return

    def download(self):
        path = askdirectory()
        if not path:
            return
        bookname = self.book_list.get(self.book_list.curselection())
        send_message(self.s, MessageType.download, bookname)
        print("下载中……")
        recv_file(self.s, path + '/' + bookname + '.txt')
        print("下载成功！")
        return

    def destroy_window(self):
        info.tk_root.destroy()
