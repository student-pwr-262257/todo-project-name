#!/usr/bin/python3

# Unfortunately, using mypy with Qt doesn't work well. mypy can't see some
# objects attributes, for example, according to mypy, QPushButton doesn't have
# clicked signal attribute. Therefore, it is turned off for the entire module,
# as the errors are numerous and ignoring each such a line would be annoying.
# type: ignore

from copy import copy
from enum import Enum, auto
from pathlib import Path
import sys
import logging
from logging import debug
from PySide6.QtCore import QObject, Qt, Signal, Slot
from rich.logging import RichHandler

from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QStackedLayout,
    QWidget,
    QComboBox,
    QFormLayout,
)
from todo_project_name import rsa

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
    def _prepare_containers_and_layouts(self):
        # The main layout of the application window
        self.layout = QFormLayout(self)
        # Container for widgets relating to current action
        self.data_container = QStackedLayout()

        # Data containers for each action
        self.checksumContainer = QWidget()
        self.checksumLayout = QFormLayout()
        self.checksumContainer.setLayout(self.checksumLayout)

        self.keypairContainer = QWidget()
        self.keypairLayout = QFormLayout()
        self.keypairContainer.setLayout(self.keypairLayout)

        self.signContainer = QWidget()
        self.signLayout = QFormLayout()
        self.signContainer.setLayout(self.signLayout)

        self.verifyContainer = QWidget()
        self.verifyLayout = QFormLayout()
        self.verifyContainer.setLayout(self.verifyLayout)

        # Add all the containers to the main data container (stack)
        self.data_container.addWidget(self.checksumContainer)
        self.data_container.addWidget(self.keypairContainer)
        self.data_container.addWidget(self.signContainer)
        self.data_container.addWidget(self.verifyContainer)

    def _set_layout_with_widgets(self, layout) -> None:
        """Set layout with widgets.

        Warning. It reparents widgets.
        """
        match layout:
            case self.checksumLayout:
                self.checksumLayout.addRow(
                    "Message path", self.checksumLayout.messagePath
                )
                self.checksumLayout.addWidget(
                    self.checksumLayout.messagePathButton
                )
                self.checksumLayout.addRow(
                    "Algorithm", self.checksumLayout.algorithm
                )
                self.checksumLayout.addRow(
                    "Checksum path: ", self.checksumLayout.checksumPath
                )
                self.checksumLayout.addWidget(
                    self.checksumLayout.checksumPathButton
                )

            case self.keypairLayout:
                self.keypairLayout.addRow(
                    "Keypair save path:", self.keypairLayout.keypairPath
                )
                self.keypairLayout.addWidget(self.keypairLayout.keypairButton)
                self.keypairLayout.addRow(
                    "Base name of generated keys",
                    self.keypairLayout.keypairBasename,
                )
                self.keypairLayout.addRow(
                    "Key pair id", self.keypairLayout.keypairId
                )

            case self.signLayout:
                self.signLayout.addRow(
                    "Message path", self.signLayout.messagePath
                )
                self.signLayout.addWidget(self.signLayout.messagePathButton)
                self.signLayout.addRow("Key ID", self.signLayout.keyId)
                self.signLayout.addWidget(self.signLayout.keyPathButton)
                self.signLayout.addRow(
                    "Signature path", self.signLayout.signaturePath
                )
                self.signLayout.addWidget(self.signLayout.signaturePathButton)

            case self.verifyLayout:
                self.verifyLayout.addRow(
                    "Public key ID", self.verifyLayout.keyId
                )
                self.verifyLayout.addWidget(self.verifyLayout.keyPathButton)
                self.verifyLayout.addRow(
                    "Message to verify", self.verifyLayout.messagePath
                )
                self.verifyLayout.addWidget(
                    self.verifyLayout.messagePathButton
                )
                self.verifyLayout.addRow(
                    "Signature path", self.verifyLayout.signaturePath
                )
                self.verifyLayout.addWidget(
                    self.verifyLayout.signaturePathButton
                )

            case _:
                raise ValueError(f"Unrecognized layout {layout}")

    def __init__(self) -> None:
        """Create a new instance."""
        super().__init__()

        self.state = State(self)
        debug(f"Initial state: {self.state}")

        self._prepare_containers_and_layouts()

        self.ACTION_STRINGS = [
            "Generate checksum",
            "Generate key pair",
            "Sign",
            "Verify",
        ]
        self.action_layout_map = dict(
            zip(
                self.ACTION_STRINGS,
                [
                    self.checksumLayout,
                    self.keypairLayout,
                    self.signLayout,
                    self.verifyLayout,
                ],
            )
        )
        self.action = QComboBox()
        self.action.addItems(self.ACTION_STRINGS)

        # Each action change resets the state
        self.action.currentTextChanged.connect(
            lambda: self.state._reset(action=self.action.currentText())
        )
        # and the layout
        self.action.currentTextChanged.connect(
            lambda text: self.data_container.setCurrentIndex(
                self.ACTION_STRINGS.index(text)
            )
        )

        self.checksumLayout.messagePath = QLabel("None")
        self.state.messagePathChanged.connect(
            self.checksumLayout.messagePath.setText
        )
        self.checksumLayout.messagePathButton = QPushButton(
            "Change message path..."
        )
        self.checksumLayout.messagePathButton.clicked.connect(
            lambda: self.state._update(
                message=QFileDialog.getOpenFileName()[0]
            )
        )
        self.checksumLayout.algorithm = QComboBox()
        self.checksumLayout.algorithm.addItems(
            [
                "MD4",
                "MD5",
            ]
        )
        self.checksumLayout.algorithm.currentTextChanged.connect(
            lambda: self.state._update(
                algorithm=self.checksumLayout.algorithm.currentText()
            )
        )
        self.checksumLayout.checksumPath = QLabel("None")
        self.state.checksumPathChanged.connect(
            self.checksumLayout.checksumPath.setText
        )
        self.checksumLayout.checksumPathButton = QPushButton(
            "Change checksum path..."
        )
        self.checksumLayout.checksumPathButton.clicked.connect(
            lambda: self.state._update(
                checksum_path=QFileDialog.getSaveFileName(
                    dir=f"{self.state.message_path}-{self.state.algorithm}-checksum.txt"
                )[0]
            )
        )

        self.keypairLayout.keypairPath = QLabel("None")
        self.state.keypairPathChanged.connect(
            self.keypairLayout.keypairPath.setText
        )
        self.keypairLayout.keypairButton = QPushButton(
            "Change keypair save location…"
        )
        self.keypairLayout.keypairButton.clicked.connect(
            lambda: self.state._update(
                keypair_path=QFileDialog.getExistingDirectory()
            )
        )
        self.keypairLayout.keypairBasename = QLineEdit("key")
        self.keypairLayout.keypairBasename.textChanged.connect(
            lambda text: self.state._update(keypair_basename=text)
        )

        self.keypairLayout.keypairId = QLineEdit("")
        self.keypairLayout.keypairId.textChanged.connect(
            lambda text: self.state._update(key_id=text)
        )

        self.signLayout.messagePath = QLabel("None")
        self.state.messagePathChanged.connect(
            self.signLayout.messagePath.setText
        )
        self.signLayout.messagePathButton = QPushButton(
            "Change message path..."
        )
        self.signLayout.messagePathButton.clicked.connect(
            lambda: self.state._update(
                message=QFileDialog.getOpenFileName()[0]
            )
        )
        self.signLayout.keyId = QLabel("None")
        self.state.keyIdChanged.connect(self.signLayout.keyId.setText)
        self.signLayout.keyPathButton = QPushButton("Change the key…")
        self.signLayout.keyPathButton.clicked.connect(
            lambda: self.state._update(
                key_path=QFileDialog.getOpenFileName()[0]
            )
        )

        self.signLayout.signaturePath = QLabel("None")
        self.state.signaturePathChanged.connect(
            self.signLayout.signaturePath.setText
        )
        self.signLayout.signaturePathButton = QPushButton(
            "Change signature path…"
        )
        self.signLayout.signaturePathButton.clicked.connect(
            lambda text: self.state._update(
                signature_path=QFileDialog.getOpenFileName()[0]
                if self.state.action == Action.VERIFY
                else QFileDialog.getSaveFileName(
                    dir=f"{self.state.message_path}-signature.txt"
                )[0]
            )
        )

        self.verifyLayout.keyId = QLabel("None")
        self.state.keyIdChanged.connect(self.verifyLayout.keyId.setText)
        self.verifyLayout.keyPathButton = QPushButton("Change the key…")
        self.verifyLayout.keyPathButton.clicked.connect(
            lambda: self.state._update(
                key_path=QFileDialog.getOpenFileName()[0]
            )
        )
        self.verifyLayout.messagePath = QLabel("None")
        self.state.messagePathChanged.connect(
            self.verifyLayout.messagePath.setText
        )
        self.verifyLayout.messagePathButton = QPushButton(
            "Change message path..."
        )
        self.verifyLayout.messagePathButton.clicked.connect(
            lambda: self.state._update(
                message=QFileDialog.getOpenFileName()[0]
            )
        )
        self.verifyLayout.signaturePath = QLabel("None")
        self.state.signaturePathChanged.connect(
            self.verifyLayout.signaturePath.setText
        )
        self.verifyLayout.signaturePathButton = QPushButton(
            "Change signature path…"
        )
        self.verifyLayout.signaturePathButton.clicked.connect(
            lambda text: self.state._update(
                signature_path=QFileDialog.getOpenFileName()[0]
                if self.state.action == Action.VERIFY
                else QFileDialog.getSaveFileName()[0]
            )
        )
        for layout in (
            self.checksumLayout,
            self.signLayout,
            self.keypairLayout,
            self.verifyLayout,
        ):
            self._set_layout_with_widgets(layout)

        self.helpButton = QPushButton("Help")

        def show_help() -> None:
            """Show help to the user in the form of a popup."""
            box = QMessageBox(parent=self)
            box.setWindowTitle("Help")
            box.setTextFormat(Qt.RichText)
            box.setText(
                """Click the folded menu labeled “Action” and choose the
                appropriate procedure. Then, fill all the required
                information. The application lets you generate a checksum of
                some file using multiple hashing algorithms. Also, it enables
                you to generate RSA key pairs. You can then use them to create
                a signature of a file with some message. Lastly, you can verify
                such signatures obtained from others, if you have their public
                key and signature."""
            )
            box.show()

        self.helpButton.clicked.connect(show_help)

        self.layout.addRow("Action", self.action)
        self.layout.addRow(self.data_container)

        self.submitButton = QPushButton("Proceed")
        self.submitButton.clicked.connect(self.state._act)
        self.layout.addWidget(self.helpButton)
        self.layout.addWidget(self.submitButton)

        self.setLayout(self.layout)


class State(QObject):
    messagePathChanged = Signal(str)
    checksumPathChanged = Signal(str)
    keypairPathChanged = Signal(str)
    keyIdChanged = Signal(str)
    signaturePathChanged = Signal(str)

    def __init__(self, qt_parent) -> None:
        """Create a new instance."""
        super().__init__()
        self.qt_parent = qt_parent
        self._reset()

    def _reset(self, **fields) -> None:
        """Set default values."""
        self.action = Action.CHECKSUM
        self.algorithm = "MD4"
        self.keypair_basename = "key"
        self.checksum_path = None
        self._key_id = None
        self.keypair_path = None
        self.message_path = None
        self._key_path = None
        self._signature_path = None
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
            keypair_basename={self.keypair_basename},
            keypair_path={self.keypair_path},
            message_path={self.message_path},
            key_path={self.key_path},
            signature_path={self.signature_path},
        )"""

    __str__ = __repr__

    def __copy__(self):
        """Return a copy of the object."""
        dummy = QWidget()
        state = self.__class__(dummy)
        state.action = copy(self.action)
        state.algorithm = copy(self.algorithm)
        state.keypair_basename = copy(self.keypair_basename)
        state.checksum_path = copy(self.checksum_path)
        state._key_id = copy(self.key_id)
        state.keypair_path = copy(self.keypair_path)
        state.message_path = copy(self.message_path)
        state._key_path = copy(self.key_path)
        state._signature_path = copy(self.signature_path)
        return state

    @property
    def signature_path(self):
        return self._signature_path

    @signature_path.setter
    def signature_path(self, path):
        self._signature_path = path
        self.signaturePathChanged.emit(path)

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
    def checksum_path(self, path: str):
        self._checkshum_path = path
        self.checksumPathChanged.emit(str(path))

    @property
    def keypair_path(self):
        return self._keypair_path

    @keypair_path.setter
    def keypair_path(self, path: str):
        self._keypair_path = path
        self.keypairPathChanged.emit(path)

    @property
    def key_id(self):
        return self._key_id

    @key_id.setter
    def key_id(self, text):
        self._key_id = text
        self.keyIdChanged.emit(text)

    @property
    def key_path(self):
        return self._key_path

    @key_path.setter
    def key_path(self, path):
        key = rsa.read_key(Path(path), rsa.RSAKeyPrivate)
        self._key_path = path
        self.key_id = key.id

    @Slot(dict)
    def _update(self, **fields) -> None:
        """Update the state."""
        debug(f"Before update: {self}")
        action = fields.get("action")
        match action:
            case None:
                pass
            case "Generate checksum":
                self.action = Action.CHECKSUM
            case "Generate key pair":
                self.action = Action.KEYPAIR
            case "Sign":
                self.action = Action.SIGN
            case "Verify":
                self.action = Action.VERIFY
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

        keypair_path = fields.get("keypair_path")
        if keypair_path:
            self.keypair_path = keypair_path

        keypair_basename = fields.get("keypair_basename")
        if keypair_basename:
            self.keypair_basename = keypair_basename

        key_path = fields.get("key_path")
        if key_path:
            self.key_path = key_path

        key_id = fields.get("key_id")
        if key_id:
            self.key_id = key_id

        signature_path = fields.get("signature_path")
        if signature_path:
            self.signature_path = signature_path

        debug(f"After update: {self}")

    def __repr__(self) -> str:
        """Representation of data."""
        return f"{self.__dict__}"

    @Slot()
    def _act(self) -> None:
        """Perform the action described by the state."""

        def inform_about_error(text: str):
            """Inform about an error using dialog."""
            QMessageBox.critical(
                self.qt_parent,
                "Error",
                text,
                QMessageBox.StandardButton.Ok,
            )

        match self.action:
            case Action.CHECKSUM:
                if not self.message_path or not self.checksum_path:
                    inform_about_error(
                        "Paths weren't given. Please fill them in."
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
                    QMessageBox.information(
                        self.qt_parent,
                        "Ok",
                        "Everything went well.",
                        QMessageBox.StandardButton.Ok,
                    )
                except:
                    inform_about_error(
                        "Something went wrong. Did you delete files after selecting them?",
                    )

            case Action.KEYPAIR:
                if not self.keypair_path or not self.keypair_basename:
                    inform_about_error(
                        "Keypair path or basename weren't given. Please fill it in.",
                    )
                    return
                try:
                    key_pair = rsa.rsa_key_gen(128)
                    key_pair.private.id = self.key_id
                    key_pair.public.id = self.key_id
                    rsa.save_key(
                        key_pair.private,
                        Path(self.keypair_path)
                        / (self.keypair_basename + ".private"),
                    )
                    rsa.save_key(
                        key_pair.public,
                        Path(self.keypair_path)
                        / (self.keypair_basename + ".public"),
                    )
                    QMessageBox.information(
                        self.qt_parent,
                        "Ok",
                        "Everything went well.",
                        QMessageBox.StandardButton.Ok,
                    )
                except:
                    inform_about_error(
                        "Something went wrong. Have you generated keys with such a basename and path already?",
                    )

            case Action.SIGN:
                if not self.key_path or not self.message_path:
                    inform_about_error(
                        "Paths weren't given. Please fill them in.",
                    )
                    return
                try:
                    message = Path(self.message_path).read_text("utf8")
                    key = rsa.read_key(Path(self.key_path), rsa.RSAKeyPrivate)
                    signature = rsa.rsa_sign(message, key)
                    Path(self.signature_path).write_text(
                        signature, encoding="utf8"
                    )
                    QMessageBox.information(
                        self.qt_parent,
                        "Ok",
                        "Everything went well.",
                        QMessageBox.StandardButton.Ok,
                    )
                except:
                    inform_about_error(
                        "Failed to write signature. Do you have write access?"
                    )

            case Action.VERIFY:
                if not (
                    self.key_path and self.message_path and self.signature_path
                ):
                    inform_about_error("Please, fill in all the fields.")
                try:
                    message = Path(self.message_path).read_text("utf8")
                    key = rsa.read_key(Path(self.key_path), rsa.RSAKeyPublic)
                    signature = Path(self.signature_path).read_text("utf8")
                    is_correct = rsa.rsa_verify(message, signature, key)
                    if is_correct:
                        QMessageBox.information(
                            self.qt_parent,
                            "Correct",
                            "Given signature is correct.",
                            QMessageBox.StandardButton.Ok,
                        )
                    else:
                        QMessageBox.information(
                            self.qt_parent,
                            "Incorrect",
                            "Given signature is incorrect.",
                            QMessageBox.StandardButton.Ok,
                        )

                except:
                    inform_about_error(
                        "Something went wrong. Are the files still there?"
                    )
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
