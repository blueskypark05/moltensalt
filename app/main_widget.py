from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QLabel, QLineEdit, QComboBox, QDialog
from PyQt6.QtCore import Qt
from app.file_widget import FileWidget
from core.make_tree import make_tree
from app.dialogs import critical
from app.select_widget import SelectWindow
from core.data_calculation import calculate_raw_data
from app.graph import create_graph_canvases

class MainWidget(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.initsystem()
        self.initUI()

    def initsystem(self):
        self.filelist = []
        self.data = {}
        return


    def initUI(self):
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 800, 600)
        self.main_layout = QVBoxLayout()
        self.topUI()
        self.downUI()
        self.setLayout(self.main_layout)

    def topUI(self):
        layout = QHBoxLayout()

        btn1 = QPushButton('file', self)
        btn1.clicked.connect(self.open_file_dialog)
        layout.addWidget(btn1)

        layout.addStretch()

        btn2 = QPushButton('select', self)
        btn2.clicked.connect(self.select_item)
        layout.addWidget(btn2)

        self.select_combobox = QComboBox(self)
        self.select_combobox.addItems(['raw data'])
        layout.addWidget(self.select_combobox)

        btn3 = QPushButton('run', self)
        btn3.clicked.connect(self.run_action)
        layout.addWidget(btn3)

        btn4 = QPushButton('export', self)
        btn4.clicked.connect(self.export_data)
        layout.addWidget(btn4)

        self.main_layout.addLayout(layout)

    def downUI(self):
        downlayout = QVBoxLayout()

        temperature_layout = QHBoxLayout()

        temperature_label = QLabel("Temperature Range(K):")
        temperature_layout.addWidget(temperature_label)
        self.mintemperature_input = QLineEdit()
        self.mintemperature_input.setPlaceholderText("Min Temperature")
        temperature_layout.addWidget(self.mintemperature_input)
        temperature_layout.addWidget(QLabel("to"))
        self.maxtemperature_input = QLineEdit()
        self.maxtemperature_input.setPlaceholderText("Max Temperature")
        temperature_layout.addWidget(self.maxtemperature_input)
        temperature_layout.addStretch()

        downlayout.addLayout(temperature_layout)

        self.graph_scroll_area = QScrollArea()
        self.graph_scroll_area.setWidgetResizable(True)

        self.graph_container = QWidget()
        self.graph_layout = QVBoxLayout(self.graph_container)

        self.empty_label = QLabel("Graph will be displayed here")
        self.empty_label.setMinimumHeight(400)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.graph_layout.addWidget(self.empty_label)
        self.graph_layout.addStretch()

        self.graph_canvas = []

        self.graph_scroll_area.setWidget(self.graph_container)
        downlayout.addWidget(self.graph_scroll_area)
        self.main_layout.addLayout(downlayout)

    def open_file_dialog(self):
        file_dialog = FileWidget(self.filelist, self.config)
        file_dialog.show()
        if file_dialog.exec() == QDialog.DialogCode.Accepted:
            data, filelist = file_dialog.get_saved_data()
            try:
                tree = make_tree(data, self.config, filelist)
            except ValueError as e:
                critical("Data Processing Error", str(e), self)
                return
            self.data = tree
            self.filelist = filelist

    def select_item(self):
        select_dialog = SelectWindow(self.data)
        if select_dialog.exec() == QDialog.DialogCode.Accepted:
            self.data = select_dialog.get_data()

    def run_action(self):
        try:
            min_temp = float(self.mintemperature_input.text())
            max_temp = float(self.maxtemperature_input.text())
        except ValueError:
            critical("Input Error", "Please enter valid numeric values for temperature range.", self)
            return
        if min_temp >= max_temp:
            critical("Input Error", "Minimum temperature must be less than maximum temperature.", self)
            return
        if self.select_combobox.currentText() == "raw data":
            try:
                graph_data = calculate_raw_data(self.data, min_temp, max_temp, self.config)
                graph_canvases = create_graph_canvases(graph_data, "raw data")
            except ValueError as e:
                critical("Data Processing Error", str(e), self)
                return
            self.display_graph_canvases(graph_canvases)
        return

    def display_graph_canvases(self, graph_canvases):
        self.clear_graphs()

        if not graph_canvases:
            if self.empty_label is None:
                self.empty_label = QLabel("Graph will be displayed here")
                self.empty_label.setMinimumHeight(400)
                self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.graph_layout.insertWidget(self.graph_layout.count() - 1, self.empty_label,)
            return

        if self.empty_label is not None:
            self.graph_layout.removeWidget(self.empty_label)
            self.empty_label.deleteLater()
            self.empty_label = None

        for canvas in graph_canvases:
            self.graph_layout.insertWidget(self.graph_layout.count() - 1, canvas,)
            self.graph_canvas.append(canvas)
    def export_data(self):
        return

    def making_export_data(self, step = 0.01):
        return

    def clear_graphs(self):
        for canvas in self.graph_canvas:
            self.graph_layout.removeWidget(canvas)
            canvas.deleteLater()

        self.graph_canvas.clear()