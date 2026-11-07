from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject



def create_page(page_counter, stacked_widget=None):
    page_widget = QtWidgets.QFrame()
    #page_widget.
    page_widget.setObjectName(f"page_widget_{page_counter}")
    page_back_btn = QtWidgets.QPushButton(page_widget)
    page_back_btn.setGeometry(QtCore.QRect(180, 550, 31, 23))
    page_back_btn.setStyleSheet("font-size: 12pt;\n"
                                "color: white;self.setCentralWidget(self.scroll)")
    page_back_btn.setText("<<")
    page_back_btn.setObjectName(f"page_back_btn")

    page_next_btn = QtWidgets.QPushButton(page_widget)
    page_next_btn.setGeometry(QtCore.QRect(340, 550, 31, 23))
    page_next_btn.setStyleSheet("font-size: 12pt;\n"
                                "color: white;self.setCentralWidget(self.scroll)")
    page_next_btn.setText(">>")
    page_next_btn.setObjectName(f"page_next_btn")

    page_now_btn = QtWidgets.QPushButton(page_widget)
    page_now_btn.setGeometry(QtCore.QRect(260, 550, 31, 23))
    page_now_btn.setStyleSheet("font-size: 12pt;\n"
                               "color: white;self.setCentralWidget(self.scroll)")
    page_now_btn.setText(f"{page_counter}")
    page_now_btn.setObjectName(f"page_now_btn")

    page_back_btn.clicked.connect(
        lambda: stacked_widget.setCurrentIndex(stacked_widget.currentIndex() - 1))
    page_next_btn.clicked.connect(
        lambda: stacked_widget.setCurrentIndex(stacked_widget.currentIndex() + 1))
    #self.ui.translation_btn.clicked.connect(self.trans_page)
    stacked_widget.addWidget(page_widget)
    return page_widget

# page to back & next page
# locals()[f"page_themes_back_btn_{page_counter}"].clicked.connect(
# lambda: self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() - 1))
# locals()[f"page_themes_next_btn_{page_counter}"].clicked.connect(
# lambda: self.ui.stackedWidget.setCurrentIndex(self.ui.stackedWidget.currentIndex() + 1))

# print("end creating new tab")



