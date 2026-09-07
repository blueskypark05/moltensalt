import sys
from PyQt6.QtWidgets import QApplication
from app.main_widget import MainWidget
from core.config import load_config
from app.dialogs import critical

def main():
    app = QApplication(sys.argv)

    try:
        config = load_config()
    except FileNotFoundError as e:
        critical("Setting File Error", str(e))
        return
    except ValueError as e:
        critical("Setting File Error", str(e))
        return

    window = MainWidget(config)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()