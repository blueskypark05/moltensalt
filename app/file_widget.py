from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QFileDialog, QGroupBox, QFormLayout, QSizePolicy
from pathlib import Path
from core.config import get_source_dir
from core.add_file import AddFile
from app.dialogs import critical
import webbrowser
from os.path import normcase

class FileWidget(QDialog):
    def __init__(self, filelist, config):
        super().__init__()
        self.config = config
        self.initUI()
        self.load_init(filelist)

    def initUI(self):
        self.setWindowTitle('File Window')
        self.resize(600, 400)
        self.main_layout = QHBoxLayout(self)
        self.leftUI()
        self.rightUI()

    def leftUI(self):
        layout = QVBoxLayout()

        self.file_list_widget = QListWidget()
        self.file_list_widget.currentRowChanged.connect(self.show_file_info)

        info_group = QGroupBox("File Information")
        info_layout = QFormLayout(info_group)

        self.name_label = QLabel("")
        self.url_label = QLabel("")
        self.property_label = QLabel("")

        self.name_label.setWordWrap(True)
        self.url_label.setWordWrap(True)
        self.property_label.setWordWrap(True)
        for label in [self.name_label, self.url_label, self.property_label]:
            label.setMinimumWidth(0)
            label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

        info_layout.addRow("Name:", self.name_label)
        info_layout.addRow("URL:", self.url_label)
        info_layout.addRow("Property:", self.property_label)

        layout.addWidget(self.file_list_widget)
        layout.addWidget(info_group)

        self.main_layout.addLayout(layout)

    def rightUI(self):
        layout = QVBoxLayout()

        btn1 = QPushButton('open folder', self)
        btn1.clicked.connect(self.open_folder)
        layout.addWidget(btn1)

        btn2 = QPushButton('add file', self)
        btn2.clicked.connect(lambda: self.add_file())
        layout.addWidget(btn2)

        btn3 = QPushButton('delete file', self)
        btn3.clicked.connect(self.delete_file)
        layout.addWidget(btn3)

        btn4 = QPushButton('clear list', self)
        btn4.clicked.connect(self.clear_list)
        layout.addWidget(btn4)

        btn5 = QPushButton('open url', self)
        btn5.clicked.connect(self.open_url)
        layout.addWidget(btn5)

        btn6 = QPushButton('close', self)
        btn6.clicked.connect(self.reject)
        layout.addWidget(btn6)

        btn7 = QPushButton('save', self)
        btn7.clicked.connect(self.save_file)
        layout.addWidget(btn7)

        layout.addStretch()

        self.main_layout.addLayout(layout)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder", str(self.source_dir))

        if not folder_path:
            return
        
        for file_path in Path(folder_path).glob("*.json"):
            self.add_file(str(file_path))
        self.sort_file_list()
        self.update_file_list()

    def add_file(self, file_path=None):
        need_sort = file_path is None
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select File", str(self.source_dir), "JSON Files (*.json)")

        if not file_path:
            return

        file_path = str(Path(file_path).resolve())
        path_key = normcase(file_path)

        if any(normcase(existing_file) == path_key for existing_file in self.filelist):
            return
        
        try:
            file_info, export_data = AddFile(file_path, self.config)
            self.filelist.append(file_path)
            self.info_list.append(file_info)
            self.data_list.append(export_data)
        
        except ValueError as e:
            critical("Add File Error", str(e))
            return
        except Exception as e:
            critical("Unexpected Error", str(e))
            return

        if need_sort:
            self.sort_file_list()
            self.update_file_list()

    def delete_file(self):
        row = self.file_list_widget.currentRow()

        if 0 <= row < len(self.filelist):
            self.filelist.pop(row)
            self.info_list.pop(row)
            self.data_list.pop(row)
            self.file_list_widget.takeItem(row)
        self.show_file_info(self.file_list_widget.currentRow())

    def clear_list(self):
        self.filelist.clear()
        self.info_list.clear()
        self.data_list.clear()
        self.file_list_widget.clear()
        self.clear_file_info()

    def open_url(self):
        row = self.file_list_widget.currentRow()
        if 0 <= row < len(self.info_list):
            url = self.info_list[row][1]
            if url:
                webbrowser.open(url)

    def save_file(self):
        self.export_data = self.data_list
        self.accept()

    def update_file_list(self):
        self.file_list_widget.clear()
        for file_path in self.filelist:
            self.file_list_widget.addItem(Path(file_path).name)

    def show_file_info(self, row):
        if not (0 <= row < len(self.info_list)):
            self.clear_file_info()
            return
        if 0 <= row < len(self.info_list):
            file_info = self.info_list[row]
            self.name_label.setText(file_info[0])
            self.url_label.setText(file_info[1])
            self.property_label.setText(file_info[2])

    def clear_file_info(self):
        self.name_label.setText("")
        self.url_label.setText("")
        self.property_label.setText("")

    def get_saved_data(self):
        return self.export_data, self.filelist

    def sort_file_list(self):
        if len(self.filelist) <= 1:
            return
        zip_list = zip(self.filelist, self.info_list, self.data_list)
        sorted_zip_list = sorted(zip_list, key=lambda x: Path(x[0]).name.lower())
        self.filelist, self.info_list, self.data_list = map(list, zip(*sorted_zip_list))

    def load_init(self, filelist):
        self.source_dir = get_source_dir()
        self.info_list = []
        self.data_list = []
        self.filelist = []
        for file_path in filelist:
            self.add_file(file_path)
        self.sort_file_list()
        self.update_file_list()