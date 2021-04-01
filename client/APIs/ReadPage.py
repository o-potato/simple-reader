import tkinter as tk
from tkinter import *
from client import info
from protocol.transmission import send_message
from protocol.transmission import recv_message
from protocol.message_type import MessageType
from tkinter import messagebox
from tkinter.simpledialog import askinteger


class ReaderForm(tk.Frame):
    def __init__(self, bookname, master=None):
        super().__init__(master)
        self.master = master
        self.s = info.s
        self.bookname = bookname
        self.user = info.current_user
        self.page_num = 0   # 当前页数
        self.total_num = 0  # 总页数
        self.chapter = []   # 章节列表
        self.chapter_num = 0    # 当前章数
        self.total_chapter = 0  # 总章数
        self.create_form()
        master.protocol("WM_DELETE_WINDOW", self.update_bookmark)

    def create_form(self):
        self.master.title("My Book Reader")
        self.chapbtn = Button(self, command=self.jump_chapter)
        self.chapbtn.pack(side=TOP, fill=X, expand=YES)

        self.text = Text(self, height=35)
        self.text.pack(side=TOP, fill=BOTH)
        self.start_read()

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.prechap = Button(self.buttonframe, text="上一章", command=self.pre_chapter)
        self.prechap.pack(side=LEFT, fill=X, expand=YES)
        self.prepage = Button(self.buttonframe, text="上一页", command=self.pre_page)
        self.prepage.pack(side=LEFT, fill=X, expand=YES)
        self.pagebtn = Button(self.buttonframe, text=str(self.page_num+1) + '/' + str(self.total_num), command=self.jump_page)
        self.pagebtn.pack(side=LEFT, fill=X, expand=YES)
        self.nextpage = Button(self.buttonframe, text="下一页", command=self.next_page)
        self.nextpage.pack(side=LEFT, fill=X, expand=YES)
        self.nextchap = Button(self.buttonframe, text="下一章", command=self.next_chapter)
        self.nextchap.pack(side=LEFT, fill=X, expand=YES)

        self.pack()

    def get_chapter(self):
        """ 通过章节列表获得当前页所处章号 """
        for i in range(self.total_chapter):
                if self.page_num >= self.chapter[i][1]:
                    if i == self.total_chapter or self.page_num < self.chapter[i+1][1]:
                        return i

    def start_read(self):
        # 查找书签
        send_message(self.s, MessageType.startRead, self.user + '&' + self.bookname)
        msg = recv_message(self.s)
        if msg['type'] == MessageType.noBook:
            messagebox.showerror("Error", "No such book!")
            return
        elif msg['type'] == MessageType.pageNum:
            self.page_num = msg['parameters']
        else:
            messagebox.showerror("Error", "Can not receive bookmark! {}".format(msg['type']))
            return

        # 接收总页数
        msg = recv_message(self.s)
        if msg['type'] == MessageType.totalPage:
            self.total_num = msg['parameters']
        else:
            messagebox.showerror("Error", "Can not receive total page! {}".format(msg['type']))
            return

        # 接收章节列表
        msg = recv_message(self.s)
        if msg['type'] == MessageType.sendChapter:
            self.chapter = msg['parameters']
            self.total_chapter = len(self.chapter)
            self.chapter_num = self.get_chapter()
            self.chapbtn['text'] = self.chapter[self.chapter_num]
        else:
            messagebox.showerror("Error", "Can not receive chapter list! {}".format(msg['type']))
            return

        # 接收书签那一页
        msg = recv_message(self.s)
        if not msg:
            messagebox.showerror("Error", "Connection wrong...")
        elif msg['type'] == MessageType.sendPage:
            if msg['parameters'][0] == '#':
                msg['parameters'] = msg['parameters'][1:]
            self.text.insert(1.0, msg['parameters'])
        else:
            messagebox.showerror("Error", "Can not receive the text! {}".format(msg['type']))
        return

    def show_page(self):
        send_message(self.s, MessageType.requirePage, [self.bookname, self.page_num])
        msg = recv_message(self.s)
        if not msg:
            messagebox.showerror("Error", "Connection wrong!")
        elif msg['type'] == MessageType.sendPage:
            self.chapter_num = self.get_chapter()
            self.chapbtn['text'] = self.chapter[self.chapter_num][0]
            self.pagebtn['text'] = str(self.page_num + 1) + '/' + str(self.total_num + 1)
            self.text.delete('1.0', 'end')
            if msg['parameters'][0] == '#':
                msg['parameters'] = msg['parameters'][1:]
            self.text.insert(1.0, msg['parameters'])
        else:
            messagebox.showerror("Error", "Can not jump to the page {}".format(msg['type']))
        return

    def jump_page(self):
        self.page_num = askinteger("页面跳转", "要跳转的页数", initialvalue=self.page_num+1, maxvalue=self.total_num+1, minvalue=1) - 1
        self.show_page()
        return

    def pre_page(self):
        if self.page_num == 0:
            messagebox.showerror("Warning", "Already at the first page!")
            return
        self.page_num = self.page_num-1
        self.show_page()
        return

    def next_page(self):
        if self.page_num == self.total_num:
            messagebox.showerror("Waring", "Already at the last page!")
            return
        self.page_num = self.page_num-1
        self.show_page()
        return

    def pre_chapter(self):
        if self.chapter_num == 0:
            messagebox.showerror("Warning", "Already at the first chapter!")
            return
        self.chapter_num = self.chapter_num-1
        self.page_num = self.chapter[self.chapter_num][1]
        self.chapbtn['text'] = self.chapter[self.chapter_num][0]
        self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_num+1)

        self.show_page()
        return

    def next_chapter(self):
        if self.chapter_num == self.total_chapter:
            messagebox.showerror("Warning", "Already at the last chapter!")
            return
        self.chapter_num = self.chapter_num+1
        self.page_num = self.chapter[self.chapter_num][1]
        self.chapbtn['text'] = self.chapter[self.chapter_num][0]
        self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_num+1)

        self.show_page()
        return

    def jump_chapter(self):
        dialog = ChapterList(self.chapter)
        self.wait_window(dialog)
        chapter_name = dialog.chapter_name
        if chapter_name is None:
            return
        for i in range(self.total_chapter):
            if chapter_name == self.chapter[i][0]:
                self.chapter_num = i
                self.page_num = self.chapter[i][1]
                self.chapbtn['text'] = chapter_name
                self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_num+1)

                self.show_page()
        return

    def update_bookmark(self):
        send_message(self.s, MessageType.updateBookmark, [self.user, self.bookname, self.page_num])
        self.master.destroy()
        return


class ChapterList(tk.Toplevel):
    def __init__(self, chapter):
        super().__init__()
        self.chapter = chapter
        self.chapter_name = ''
        self.create_form()

    def create_form(self):
        self.title("请选择章节")

        self.scrb = Scrollbar(self)
        self.scrb.pack(side=RIGHT, fill=Y)

        self.chaplist = Listbox(self, heigth=15, width=40, yscrollcommand=self.scrb.set)
        for chapter in self.chapter:
            self.chaplist.insert(END, chapter[0])
        self.chaplist.pack(side=TOP, fill=BOTH)

        self.scrb.config(command=self.chaplist.yview)

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.jumpbtn = Button(self.buttonframe, text="跳转", command=self.jump)
        self.jumpbtn.pack(side=LEFT, fill=X, expand=YES)
        self.ccbtn = Button(self.buttonframe, text="取消", command=self.cancel)
        self.ccbtn.pack(side=LEFT, fill=X, expand=YES)

    def jump(self):
        self.chapter_name = self.chaplist.get(self.chaplist.curselection())
        self.destroy()

    def cancel(self):
        self.destroy()
