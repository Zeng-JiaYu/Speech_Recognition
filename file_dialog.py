#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

# @FileName   : file_dialog.py
# @Software   : PyCharm
# @Description：文件窗口

import tkinter as tk
from tkinter import filedialog


class FileDialog(tk.Frame):
    """
    文件窗口操作类，如打开文件
    """
    def __init__(self, parent, title: str, file_type: str):
        """
        构造函数，初始化窗口参数、文件选项、目录选项
        :param parent: 父窗口句柄
        :param title: 窗口标题
        :param file_type: 文件的类型
        """
        tk.Frame.__init__(self, parent)

        self.__dialog_title = title
        self.__file_type = file_type
        # 打开或保存文件的选项
        self.__file_opt = options = {}
        options['filetypes'] = [('doc files', '.doc'), ('wav files', '.wav'), ('all files', '.*')]  # 此项目值涉及对doc和wav文件的操作
        options['initialdir'] = 'D:\\'
        options['initialfile'] = 'record' + self.__file_type
        options['parent'] = parent
        options['title'] = self.__dialog_title
        # 打开目录选项
        self.__dir_opt = options = {}
        options['initialdir'] = 'D:\\'
        options['mustexist'] = False
        options['parent'] = parent
        options['title'] = self.__dialog_title

    def get_open_file_name(self):
        """
        返回选择的文件的绝对路径
        """
        return tk.filedialog.askopenfilename(**self.__file_opt)

    def get_save_file_name(self):
        """
        返回保存的文件的绝对路径
        """
        return tk.filedialog.asksaveasfilename(**self.__file_opt)

    def get_directory(self):
        """
        返回选定的目录名称
        """
        return tk.filedialog.askdirectory(**self.__dir_opt)


if __name__ == '__main__':
    root = tk.Tk()
    FileDialog(root, "文件窗口", "doc").pack()
    root.mainloop()
