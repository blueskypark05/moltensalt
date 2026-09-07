from PyQt6.QtWidgets import QMessageBox


def critical(title, message, parent=None):
    QMessageBox.critical(
        parent,
        title,
        message
    )


def warning(title, message, parent=None):
    QMessageBox.warning(
        parent,
        title,
        message
    )


def information(title, message, parent=None):
    QMessageBox.information(
        parent,
        title,
        message
    )