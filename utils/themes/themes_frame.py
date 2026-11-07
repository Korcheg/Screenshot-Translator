from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject


class Theme_frame(QtWidgets.QFrame):
    def __init__(self, coords_frame, parent, folder, path_for_style, select_theme, *args, **kwargs):
        super(Theme_frame, self).__init__(*args, **kwargs)

        theme_frame = QtWidgets.QFrame(parent)
        theme_frame.setGeometry(
            QtCore.QRect(coords_frame[0], coords_frame[1], 131, 171))
        theme_frame.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        theme_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        theme_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        theme_frame.setObjectName(f"theme_frame")

        theme_name_label = QtWidgets.QLabel(theme_frame)
        theme_name_label.setGeometry(QtCore.QRect(0, 150, 131, 21))
        theme_name_label.setStyleSheet("color: white;\n"
                                       "border-radius: 5px;\n"
                                       "font-size: 12pt;\n"
                                       "border: 2px solid rgba(255, 255, 255, 230);\n"
                                       "border-radius: 5px;")
        theme_name_label.setObjectName(f"theme_name_label")
        theme_name_label.setText(folder)

        theme_icon_label = QtWidgets.QLabel(theme_frame)
        theme_icon_label.setGeometry(QtCore.QRect(0, 0, 131, 131))
        theme_icon_label.setStyleSheet(
            "border: 2px solid rgba(255, 255, 255, 230);\n"
            f"border-image: url({path_for_style}/themes/{folder}/icon.png);\n"
            "\n"
            "border-radius: 5px;")
        theme_icon_label.setText("")
        theme_icon_label.setObjectName(f"theme_icon_label")

        theme_select_btn = QtWidgets.QPushButton(theme_frame)
        theme_select_btn.setGeometry(QtCore.QRect(0, 0, 131, 171))
        theme_select_btn.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        theme_select_btn.setText("")
        theme_select_btn.setObjectName(f"{folder}")
        theme_select_btn.clicked.connect(select_theme)
        print(f"PARENT: {parent.objectName()}")
