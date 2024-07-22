# widgets.py

from PySide2 import QtWidgets

class CheckBoxWidget(QtWidgets.QCheckBox):
    def __init__(self, text, parent=None):
        super(CheckBoxWidget, self).__init__(text, parent)
        self.setStyleSheet("""
            QCheckBox {
                background-color: #2b2b2b;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:checked {
                image: url(:/qt-project.org/styles/commonstyle/images/check.png);
            }
        """)
