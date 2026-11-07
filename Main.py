# -*- coding: utf-8 -*-
import time
import psutil

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from utils.themes import themes_frame, page_frame
import json
import sys
import os
import colorama
from colorama import Fore, Back, Style
from PIL import ImageGrab
from deep_translator import GoogleTranslator, MyMemoryTranslator, LibreTranslator
from winotify import Notification
import pytesseract
import pyautogui
import threading
import deepl
import re
import webbrowser
import keyboard

colorama.init()
path_to_script = os.path.dirname(os.path.abspath(__file__))
pytesseract.pytesseract.tesseract_cmd = f"{path_to_script}\\Tesseractfiles\\tesseract.exe"
with open(f"{path_to_script}\\settings.json") as f:
    settings = json.load(f)

sys.path.append(f"{path_to_script}\\themes\\{settings['theme_now']}")

from ui_settings import ui_settings
from ui_translator import ui_translator

# from ui_initializing import ui_initializing

try:
    from ui_resources import resources
except Exception as error:
    print("failure to import resources: ", error)

if len(settings['auth_key']) > 10:
    deepl_tr = deepl.Translator(settings['auth_key'])
else:
    deepl_tr = None


class MyObject(QObject):
    mySignal = pyqtSignal()
    signal_incomingText = pyqtSignal(list)


def reformat_recognized_string(string):
    string = string.replace('\n ', " ")
    string = string.replace(' \n', " ")
    string = string.replace(' \n ', " ")
    string = string.replace('\n', "")
    string = string.replace('|', "I")
    return string


class Translatorwin(QtWidgets.QWidget):
    def __init__(self):
        super(Translatorwin, self).__init__()
        self.ui = ui_translator.Ui_Frame()
        self.ui.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.obj = MyObject()
        self.closed = False
        self.endler = 0
        self.winmode = 0
        self.xy1 = None
        self.xy2 = None
        self.press = False
        self.last_pos = QtCore.QPoint(0, 0)

        # thread = threading.Thread(target=self.accept, args=(self,))
        self.obj.signal_incomingText.connect(lambda data: self.change_text(data))
        self.ui.translate_realtime_check.stateChanged.connect(self.start_thread)

        class Some_error(str):
            pass

        self.error = Some_error("some error")

        self.ui.translate_btn.clicked.connect(self.text)
        self.ui.settings_btn.clicked.connect(self.start_settings)
        self.ui.minsize_btn.clicked.connect(self.change_win_mode)
        self.ui.exit_btn.clicked.connect(lambda: self.close())
        self.ui.max_btn.clicked.connect(self.change_win_mode)
        self.ui.topdisplay_check.stateChanged.connect(self.pin_top)

        self.ui.first_coord_label.setText(settings["ctrl_1st_point"] + ": x None")
        self.ui.second_coord_label.setText(settings["ctrl_2nd_point"] + ": y None")

        hotkeys_thread = threading.Thread(target=self.hotkeys)
        hotkeys_thread.start()

        if settings["checking_folder"] == 1:
            check_folder_thread = threading.Thread(target=self.check_folder)
            check_folder_thread.start()

    def check_folder(self):
        while True:
            if self.closed is True: break
            first_items = os.listdir(settings['check_folder'])
            time.sleep(1.5)
            second_items = os.listdir(settings['check_folder'])
            if len(first_items) < len(second_items):
                print("items count irregular")
                for item in second_items:
                    if item in first_items:
                        continue
                    else:
                        print("translating: ", item)
                        self.text()

    def hotkeys(self):
        while True:
            if self.closed is True: break
            try:
                if settings['checking_folder'] == 0:
                    if keyboard.is_pressed(settings['ctrl_translate']):
                        print("printscreen pressed")
                        time.sleep(4)
                        print("translating")
                        self.text()
                if keyboard.is_pressed(settings["ctrl_1st_point"]): self.get_x()
                if keyboard.is_pressed(settings["ctrl_2nd_point"]): self.get_y()
                if keyboard.is_pressed(settings["ctrl_changewinmode"]): self.change_win_mode()
                if keyboard.is_pressed(settings["translate_in_realtime"]): self.trans_in_realtime_checkbox_handler()
            except Exception as error:
                print(f"key exception: {error}")
                continue

    def notificate(self, header, content, duration, icon):
        if settings['show_notification'] == 1:
            toast = Notification(
                    app_id = f"{header}",
                    title = "Translated",
                    msg = f"{content}",
                    duration="short",
                    icon=icon
                    )

            toast.show()

    def closeEvent(self, event):
        print("closed")
        self.endler = 1
        self.closed = True
        self.close()

    # mouse event for drag-able window label
    def mouseMoveEvent(self, event):
        if self.press:
            self.move(event.globalPos() - self.last_pos)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.press = True

        self.last_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.press = False

    def change_win_mode(self):
        if self.winmode == 0:
            self.resize(370, 170)
            self.ui.stackedWidget.setCurrentIndex(1)
            self.winmode = 1
        else:
            self.resize(810, 615)
            self.ui.stackedWidget.setCurrentIndex(0)
            self.winmode = 0

    def trans_in_realtime_checkbox_handler(self):
        if self.ui.translate_realtime_check.isChecked():
            self.ui.translate_realtime_check.setChecked(False)
        else:
            self.ui.translate_realtime_check.setChecked(True)

    def start_settings(self):
        self.settings_win = Settings_win(parent=self)
        self.settings_win.show()

    def change_text(self, data):
        self.ui.not_translated_textedit.setText(data[0])
        self.ui.translated_textedit.setText(data[1])
        self.ui.translated_textedit_pg2.setText(data[1])

    def start_thread(self, state):
        print("state in start_thread:", state)
        if state == QtCore.Qt.Checked:
            self.endler = 0
            th = threading.Thread(target=self.trans_real_time)
            th.start()
        else:
            self.endler = 1

    def get_x(self):
        self.xy1 = pyautogui.position()
        self.ui.first_coord_label.setText(settings["ctrl_1st_point"] + f": xy1 = {self.xy1[0]}-{self.xy1[1]}")
        print(self.xy1)

    def get_y(self):
        self.xy2 = pyautogui.position()
        self.ui.second_coord_label.setText(settings["ctrl_2nd_point"] + f": xy2 = {self.xy2[0]}-{self.xy2[1]}")

    def trans_real_time(self):
        while True:
            if self.endler != 1:
                time.sleep(1.5)
                self.text()
            else:
                break

    def pin_top(self, state):
        if state == QtCore.Qt.Checked:
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
            # self.imgworker = Translatorwin()
            self.show()
        if state != QtCore.Qt.Checked:
            self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
            self.show()

    def text(self, started_by=None):  # started_by - for future
        im = None
        if self.xy1 is None:
            im = ImageGrab.grabclipboard()
            print(im)
        if self.xy1 is not None:
            im = ImageGrab.grab(bbox=(self.xy1[0], self.xy1[1], self.xy2[0], self.xy2[1]))

        if im is None:
            print("none")
            self.error.text = "No image in copyboard!"
            self.obj.signal_incomingText.emit([self.error, self.error])

        if im is not None:
            im.save('image_to_translate.png', 'png')

            comba = self.ui.lang_in_combo.currentIndex()
            comba2 = self.ui.lang_out_combo.currentIndex()

            if comba == 0:
                string = pytesseract.image_to_string("image_to_translate.png", lang='eng')
                string = reformat_recognized_string(string)
                # text_edit.setText(string)
                if comba2 == 1:
                    try:

                        if settings["translate_by"] == 2:
                            print('translated by MyMemoryTranslator')
                            trans_string = MyMemoryTranslator(source='en-GB', target='uk-UA').translate(string)
                            self.obj.signal_incomingText.emit([string, trans_string])
                            self.notificate("Translated!", trans_string, 5, "icon.ico")


                        if settings["translate_by"] == 0:
                            print('translated by Google')
                            trans_string = GoogleTranslator(source='en', target='uk').translate(string)
                            self.obj.signal_incomingText.emit([string, trans_string])
                            self.notificate("Translated!", trans_string, 5, "icon.ico")
                        if settings["translate_by"] == 1 and deepl_tr is not None:
                            print('translated by DeepL')
                            trans_string = deepl_tr.translate_text(string, target_lang="UA")
                            self.obj.signal_incomingText.emit([string, trans_string.text])
                            self.notificate("Translated!", trans_string.text, 5, "icon.ico")
                        if deepl_tr is not None and settings["translate_by"] == 1:
                            self.error.text = "Cannot translate, because you dont set auth_key for DeepL"
                            self.obj.signal_incomingText.emit([string, self.error])
                    except Exception as e:
                        e.text = f"Translation Error: {e}"
                        self.obj.signal_incomingText.emit([e.text, e.text])
                        print(e.text)

            if comba == 1:
                string = pytesseract.image_to_string("image_to_translate.png", lang='ukr')
                string = reformat_recognized_string(string)
                # text_edit.setText(string)
                if comba2 == 0:
                    try:

                        if settings["translate_by"] == 2:
                            print('translated by MyMemoryTranslator')
                            trans_string = MyMemoryTranslator(source='uk-UA', target='en-GB').translate(string)
                            self.obj.signal_incomingText.emit([string, trans_string])
                            self.notificate("Translated!", trans_string, 5, "icon.ico")


                        if settings["translate_by"] == 0:
                            print('translated by Google')
                            trans_string = GoogleTranslator(source='uk', target='en').translate(string)                 
                            self.obj.signal_incomingText.emit([string, trans_string])
                            self.notificate("Translated!", trans_string, 5, "icon.ico")
                        if settings["translate_by"] == 1 and deepl_tr is not None:
                            print('translated by DeepL')
                            trans_string = deepl_tr.translate_text(string, target_lang="EN-US") 
                            self.obj.signal_incomingText.emit([string, trans_string.text])
                            self.notificate("Translated!", trans_string.text, 5, "icon.ico")
                        if deepl_tr is not None and settings["translate_by"] == 1:
                            self.error.text = "Cannot translate, because you dont set auth_key for DeepL"
                            self.obj.signal_incomingText.emit([string, self.error])

                    except Exception as e:
                        e.text = f"Translation Error: {e}"
                        self.obj.signal_incomingText.emit([e.text, e.text])
                        print(e.text) 


class Settings_win(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = ui_settings.Ui_Frame()
        self.ui.setupUi(self)
        self.ui.your_auth_key_label.hide()
        self.ui.your_auth_key_lineedit.hide()
        if settings['starts_traymode'] == 1:
            self.ui.starts_traymodule_check.setChecked(True)
        if settings['show_notification'] == 1:
            self.ui.show_message_check.setChecked(True)
        if settings["checking_folder"] == 0:
            self.ui.folder_path_label.hide()
            self.ui.folder_path_lineedit.hide()
        else:
            self.ui.folder_check.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.translate_by_comba.currentIndexChanged.connect(self.show_deepl_widget)

        # set setting for not changeable moments, same block for hotkeys - move down
        self.settings = settings
        self.iters = 0
        self.pages_are_created = 0



        self.check_folder = settings['checking_folder']
        self.starts_traymode = settings['starts_traymode']
        self.show_notification = settings['show_notification']
        self.selected_theme = settings['theme_now']
        self.ui.theme_name_label.setText(settings['theme_now'])

        print("path to script: ", path_to_script)
        self.path_for_style = path_to_script.replace("\\", "/")
        self.ui.theme_icon_label.setStyleSheet("border: 2px solid rgba(255, 255, 255, 230);\n"
                                               f"border-image: url({self.path_for_style}/themes/{settings['theme_now']}/icon.png);\n"
                                               "\n"
                                               "border-radius: 5px;")

        self.ui.translation_btn.clicked.connect(self.trans_page)
        self.ui.themes_btn.clicked.connect(self.themes_page)
        self.ui.controls_btn.clicked.connect(self.ctrl_page)
        self.ui.theme_author_btn.clicked.connect(lambda: webbrowser.open(
            re.search("(?P<url>https?://[^\s]+)", self.ui.theme_author_btn.styleSheet()).group("url")))
        self.ui.page_back_btn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() - 1))
        self.ui.page_next_btn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() + 1))
        self.ui.save_btn.clicked.connect(self.save_change)
        self.ui.folder_check.stateChanged.connect(self.show_check_folder_widgets)
        self.ui.starts_traymodule_check.stateChanged.connect(self.starts_traymode_func)
        self.ui.show_message_check.stateChanged.connect(self.show_notifications)

        self.ui.translate_by_comba.setCurrentIndex(self.settings["translate_by"])
        self.ui.your_auth_key_lineedit.setText(self.settings["auth_key"])
        self.ui.translate_lineedit.setText(self.settings["ctrl_translate"])
        self.ui.first_point_lineedit.setText(self.settings["ctrl_1st_point"])
        self.ui.second_point_lineedit.setText(self.settings["ctrl_2nd_point"])
        self.ui.translate_realtime_lineedit.setText(self.settings["translate_in_realtime"])
        self.ui.winmode_lineedit.setText(self.settings["ctrl_changewinmode"])
        self.ui.folder_path_lineedit.setText(self.settings["check_folder"])
        self.ui.call_traymode_lineedit.setText(self.settings["call_traymode"])

    def show_notifications(self, state):
        if state == QtCore.Qt.Checked:
            self.show_notification = 1
        if state != QtCore.Qt.Checked:
            self.show_notification = 0


    def starts_traymode_func(self, state):
        if state == QtCore.Qt.Checked:
            self.starts_traymode = 1
        if state != QtCore.Qt.Checked:
            self.starts_traymode = 0

    def show_check_folder_widgets(self, state):
        if state == QtCore.Qt.Checked:
            self.ui.folder_path_label.show()
            self.ui.folder_path_lineedit.show()
            self.check_folder = 1
        if state != QtCore.Qt.Checked:
            self.ui.folder_path_label.hide()
            self.ui.folder_path_lineedit.hide()
            self.check_folder = 0

    def foo(self):
        button = QtWidgets.QApplication.instance().sender()
        self.selected_theme = button.objectName()
        print(button.objectName())

    def load_all_themes(self):
        var_theme_frame = "theme_frame_"
        var_theme_name_label = "theme_name_label_"
        var_theme_select_btn = "theme_select_btn_"
        var_theme_icon_label = "theme_icon_label_"

        themes_available = os.listdir(f"{path_to_script}\\themes\\")
        print("Themes available: ", themes_available)
        row = 0
        column = 0

        coords_frame = [0, 10]
        page_counter = 1
        page_now = self.ui.page_themes

        if self.pages_are_created == 0:
            for folder in themes_available:
                self.iters += 1
                print("len(themes_available): ", len(themes_available))
                print("len(themes_available) - iters: ", len(themes_available) - self.iters)
                if len(themes_available) - self.iters <= 0:
                    self.pages_are_created = 1
                print("page_are_created: ", self.pages_are_created)
                print("self.iters: ", self.iters)

                themes_frame.Theme_frame(coords_frame, page_now, folder, self.path_for_style, self.foo)
                print(f"PAGE_NOW: {page_now.objectName()}")

                if column < 3:
                    column += 1
                else:
                    row += 1
                    column = 0

                if coords_frame[0] == 450 and coords_frame[1] == 210 and self.pages_are_created == 0:  # page creating
                    coords_frame = [-150, 10]
                    print("coords inside creating tab: ", coords_frame)
                    print("start creating new tab")
                    page_counter += 1
                    page_now = page_frame.create_page(page_counter, self.ui.stackedWidget)
                    print(f'PAGE_NOW OBJECT NAME: {page_now.objectName()}')
                    print("end creating new tab")

                print("coords before main coords logic: ", coords_frame)
                if coords_frame[0] == 450:
                    coords_frame[1] += 200
                    coords_frame[0] = 0
                else:
                    coords_frame[0] += 150
                print(f"coords after main coords logic:  {coords_frame}")
                # self.ui.scrollAreaWidgetContents.addWidget(locals()[f"{var_theme_frame}{folder}"])
                # self.ui.themes_gridLayout.addWidget(locals()[f"{var_theme_frame}{folder}"], row, column, 1, 1)
                # print("locals after crafting: ", locals())
                print(f"stacked widget count: {self.ui.stackedWidget.count()}")
                # locals()[]


    def back_page(self):
        return self.ui.stackedWidget.currentIndex() - 1

    def trans_page(self):
        print('cliked trans')
        self.resize(797, 596)
        self.ui.stackedWidget.setCurrentIndex(0)

    def show_deepl_widget(self, state):
        if state == 1:
            self.ui.your_auth_key_label.show()
            self.ui.your_auth_key_lineedit.show()
            self.ui.your_auth_key_lineedit.setText(self.settings["auth_key"])
            #self.ui.folder_check_label.move(self.ui.folder_check_label.x(), self.ui.folder_check_label.y()+1)
        else:
            self.ui.your_auth_key_label.hide()
            self.ui.your_auth_key_lineedit.hide()

    def themes_page(self):
        print('cliked paths')
        self.resize(1045, 596)
        self.load_all_themes()
        self.ui.stackedWidget.setCurrentIndex(2)

    def ctrl_page(self):
        self.resize(797, 596)
        print('cliked ctrl')
        self.ui.stackedWidget.setCurrentIndex(1)

    def save_change(self):
        settings = {
            "translate_by": self.ui.translate_by_comba.currentIndex(),
            "ctrl_translate": self.ui.translate_lineedit.text(),
            "ctrl_1st_point": self.ui.first_point_lineedit.text(),
            "ctrl_2nd_point": self.ui.second_point_lineedit.text(),
            "translate_in_realtime": self.ui.translate_realtime_lineedit.text(),
            "ctrl_changewinmode": self.ui.winmode_lineedit.text(),
            "auth_key": self.ui.your_auth_key_lineedit.text(),
            "theme_now": self.selected_theme,
            "checking_folder": self.check_folder,
            "check_folder": self.ui.folder_path_lineedit.text(),
            "starts_traymode": self.starts_traymode,
            "show_notification": self.show_notification,
            "call_traymode": self.ui.call_traymode_lineedit.text()
        }
        print(settings)
        my_filename = os.path.join(path_to_script, "settings.json")
        with open(my_filename, "w+") as f:
            json.dump(settings, f)
        self.close()
        self.parent.close()


app = QtWidgets.QApplication(sys.argv)
application = Translatorwin()
application.show()
app.exec()

