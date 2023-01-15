#!/usr/bin/python3

import sys
from PySide6.QtWidgets import QApplication, QMainWindow


def main():
    application = QApplication()
    main_window = MainWindow()
    main_window.show()
    status = application.exec()
    sys.exit(status)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        """Create a new instance."""
        super().__init__()
        # TODO: Implement.
        raise NotImplementedError


if __name__ == "__main__":
    main()
