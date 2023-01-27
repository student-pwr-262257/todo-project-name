#!/usr/bin/python3

# Unfortunately, using mypy with Qt doesn't work well. mypy can't see some
# objects attributes, for example, according to mypy, QPushButton doesn't have
# clicked signal attribute. Therefore, it is turned off for the entire module,
# as the errors are numerous and ignoring each such a line would be annoying.
# type: ignore

from enum import Enum, auto
from pathlib import Path
import sys
import logging
from logging import debug
from PySide6.QtCore import QObject, Signal, Slot
from rich.logging import RichHandler

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedLayout,
    QWidget,
    QComboBox,
    QFormLayout,
)

from todo_project_name.md5 import MD5
from todo_project_name.md4 import MD4


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        logging.basicConfig(level="DEBUG", handlers=[RichHandler()])
    application = QApplication()
    main_window = MainWindow()
    main_window.show()
    status = application.exec()
    sys.exit(status)


class MainWindow(QWidget):
    def __init__(self) -> None:
        """Create a new instance."""
        super().__init__()

        self.state = State(self)
        debug(f"Initial state: {self.state}")

        # The main widget layout with its data container holding widgets needed
        # for current action
        self.layout = QFormLayout(self)
        self.data_container = QStackedLayout()

        # Data containers for each action
        self.checksumLayout = QFormLayout()
        self.checksumContainer = QWidget()
        self.checksumContainer.setLayout(self.checksumLayout)

        self.keypairLayout = QFormLayout()
        self.keypairContainer = QWidget()
        self.keypairContainer.setLayout(self.keypairLayout)

        self.signLayout = QFormLayout()
        self.signContainer = QWidget()
        self.signContainer.setLayout(self.signLayout)

        self.verifyLayout = QFormLayout()
        self.verifyContainer = QWidget()
        self.verifyContainer.setLayout(self.verifyLayout)

        # Add all the containers to the main data container
        self.data_container.addWidget(self.checksumContainer)
        self.data_container.addWidget(self.keypairContainer)

        ACTION_STRINGS = [
            "Generate checksum",
            "Generate key pair",
            "Sign",
            "Verify signature",
        ]
        self.action = QComboBox()
        self.action.addItems(ACTION_STRINGS)

        # Each action change resets the state
        self.action.currentTextChanged.connect(
            lambda: self.state._reset(action=self.action.currentText())
        )
        # and the layout
        self.action.currentTextChanged.connect(
            lambda text: self.data_container.setCurrentIndex(
                ACTION_STRINGS.index(text)
            )
        )

        self.messagePath = QLabel("None")
        self.state.messagePathChanged.connect(self.messagePath.setText)
        self.checksumLayout.addRow("Message path", self.messagePath)

        self.messagePathButton = QPushButton("Change message path...")
        self.messagePathButton.clicked.connect(
            lambda: self.state._update(
                message=QFileDialog.getOpenFileName()[0]
            )
        )
        self.checksumLayout.addWidget(self.messagePathButton)

        self.algorithm = QComboBox()
        self.algorithm.addItems(
            [
                "MD4",
                "MD5",
            ]
        )
        self.algorithm.currentTextChanged.connect(
            lambda: self.state._update(algorithm=self.algorithm.currentText())
        )
        self.checksumLayout.addRow("Algorithm", self.algorithm)

        self.checksumPath = QLabel("None")
        self.state.checksumPathChanged.connect(self.checksumPath.setText)
        self.checksumLayout.addRow("Checksum path: ", self.checksumPath)
        self.checksumPathButton = QPushButton("Change checksum path...")
        self.checksumPathButton.clicked.connect(
            lambda: self.state._update(
                checksum_path=QFileDialog.getSaveFileName()[0]
            )
        )
        self.checksumLayout.addWidget(self.checksumPathButton)

        self.layout.addRow("Action", self.action)
        self.layout.addRow(self.data_container)

        self.submitButton = QPushButton("Proceed")
        self.submitButton.clicked.connect(self.state._act)
        self.layout.addWidget(self.submitButton)

        self.setLayout(self.layout)


class State(QObject):
    messagePathChanged = Signal(str)
    checksumPathChanged = Signal(str)

    def __init__(self, qt_parent) -> None:
        """Create a new instance."""
        super().__init__()
        self.qt_parent = qt_parent
        self._reset()

    def _reset(self, **fields) -> None:
        """Set default values."""
        self.action = Action.CHECKSUM
        self.algorithm = "MD4"
        self.checksum_path = None
        self.key_id = None
        self.message_path = None
        self.private_key = None
        self.public_key = None
        self.signature = None
        if fields:
            self._update(**fields)
        debug(f"The state was reset to {self}.")

    def __repr__(self):
        name = self.__class__.__name__
        return f"""{name}(
            action={self.action},
            algorithm={self.algorithm},
            checksum_path={self.checksum_path},
            key_id={self.key_id},
            message_path={self.message_path},
            private_key={self.private_key},
            public_key={self.public_key},
            signature={self.signature},
        )"""

    __str__ = __repr__

    @property
    def message_path(self):
        return self._message_path

    @message_path.setter
    def message_path(self, path: str) -> None:
        self._message_path = path
        self.messagePathChanged.emit(str(path))

    @property
    def checksum_path(self):
        return self._checkshum_path

    @checksum_path.setter
    def checksum_path(self, path):
        self._checkshum_path = path
        self.checksumPathChanged.emit(str(path))

    @Slot(dict)
    def _update(self, **fields) -> None:
        """Update the state."""
        debug(f"Before update: {self.__dict__}")
        action = fields.get("action")
        match action:
            case None:
                pass
            case "Generate checksum":
                self.action = Action.CHECKSUM
            case _:
                raise NotImplementedError("Failed to match action.")

        message = fields.get("message")
        if message:
            self.message_path = Path(message)

        checksum_path = fields.get("checksum_path")
        if checksum_path:
            self.checksum_path = Path(checksum_path)

        algorithm = fields.get("algorithm")
        if algorithm:
            self.algorithm = algorithm

        debug(f"After update: {self.__dict__}")

    def __repr__(self) -> str:
        """Representation of data."""
        return f"{self.__dict__}"

    @Slot()
    def _act(self) -> None:
        """Perform the action described by the state."""
        match self.action:
            case Action.CHECKSUM:
                if not self.message_path or not self.checksum_path:
                    QMessageBox.critical(
                        self.qt_parent,
                        "Error",
                        "Paths weren't given. Please fill them in.",
                        QMessageBox.StandardButton.Ok,
                    )
                    return

                try:
                    match self.algorithm:
                        case "MD4":
                            checksum = MD4.from_file(self.message_path)
                        case "MD5":
                            checksum = MD5.from_file(self.message_path)
                        case _:
                            raise NotImplementedError(
                                f"Invalid algorithm {self.algorithm}"
                            )

                    Path(self.checksum_path).write_text(
                        checksum.string_digest()
                    )
                except:
                    QMessageBox.critical(
                        self.qt_parent,
                        "Error",
                        "Something went wrong. Did you delete files after selecting them?",
                    )

            case Action.KEYPAIR:
                raise NotImplementedError
            case Action.SIGN:
                raise NotImplementedError
            case Action.VERIFY:
                raise NotImplementedError
            case _:
                raise NotImplementedError(
                    f"Unexpected case matched. The action was: {self.action}"
                )


class Action(Enum):
    """The end procedure of single program operation."""

    CHECKSUM = auto()
    KEYPAIR = auto()
    SIGN = auto()
    VERIFY = auto()


if __name__ == "__main__":
    main()
