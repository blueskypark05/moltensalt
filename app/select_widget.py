from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class SelectWindow(QDialog):
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Select Data")
        self.setGeometry(100, 100, 1200, 400)
        self.data = data
        self.record_items = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["item", "correlation", "unit", "temperature range", "weight"])
        self.populate_tree(self.data, self.tree_widget.invisibleRootItem())
        self.tree_widget.itemChanged.connect(self.on_item_changed)
        self.initialize_check_states()

        self.tree_widget.expandAll()
        for i in range(5):
            self.tree_widget.resizeColumnToContents(i)
        layout.addWidget(self.tree_widget)
        self.tree_widget.collapseAll()

        btn_layout = QHBoxLayout()
        expand_btn = QPushButton("Expand All")
        expand_btn.clicked.connect(self.tree_widget.expandAll)
        collapse_btn = QPushButton("Collapse All")
        collapse_btn.clicked.connect(self.tree_widget.collapseAll)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_checked_items)
        btn_layout.addStretch()
        btn_layout.addWidget(expand_btn)
        btn_layout.addWidget(collapse_btn)
        btn_layout.addWidget(close_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def populate_tree(self, data, parent_item):
        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem([str(key)])
                parent_item.addChild(item)
                self.populate_tree(value, item)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(0, Qt.CheckState.Checked)
        elif isinstance(data, list):
            for index, record in enumerate(data, start=1):
                item = QTreeWidgetItem([
                    str(index),
                    str(record.get("correlation", "")),
                    str(record.get("unit", "")),
                    str(record.get("temperature_range", "")),
                    str(record.get("weight", "")),
                ])
                parent_item.addChild(item)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                if record.get("selected", False):
                    item.setCheckState(0, Qt.CheckState.Checked)
                else:
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                self.record_items.append((record, item))

    def on_item_changed(self, item, column):
        if column != 0:
            return

        check_state = item.checkState(0)

        self.tree_widget.blockSignals(True)
        try:
            if check_state != Qt.CheckState.PartiallyChecked:
                self.check_children(item, check_state)
            self.update_parent_check_state(item.parent())
        finally:
            self.tree_widget.blockSignals(False)

    def check_children(self, item, check_state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, check_state)
            self.check_children(child, check_state)

    def update_parent_check_state(self, parent_item):
        if parent_item is None:
            return

        checked_count = 0
        partially_checked_count = 0
        child_count = parent_item.childCount()

        for i in range(child_count):
            child = parent_item.child(i)
            if child.checkState(0) == Qt.CheckState.Checked:
                checked_count += 1
            elif child.checkState(0) == Qt.CheckState.PartiallyChecked:
                partially_checked_count += 1

        if checked_count == child_count:
            parent_item.setCheckState(0, Qt.CheckState.Checked)
        elif checked_count > 0 or partially_checked_count > 0:
            parent_item.setCheckState(0, Qt.CheckState.PartiallyChecked)
        else:
            parent_item.setCheckState(0, Qt.CheckState.Unchecked)

        self.update_parent_check_state(parent_item.parent())
    
    def initialize_check_states(self):
        root = self.tree_widget.invisibleRootItem()
        self.tree_widget.blockSignals(True)
        try:
            for i in range(root.childCount()):
                self.initialize_item_check_states(root.child(i))
        finally:
            self.tree_widget.blockSignals(False)
    
    def initialize_item_check_states(self, item):
        if item.childCount() == 0:
            return item.checkState(0)

        child_states = []
        for i in range(item.childCount()):
            child_states.append(self.initialize_item_check_states(item.child(i)))

        if all(state == Qt.CheckState.Checked for state in child_states):
            item.setCheckState(0, Qt.CheckState.Checked)
            return Qt.CheckState.Checked
        elif all(state == Qt.CheckState.Unchecked for state in child_states):
            item.setCheckState(0, Qt.CheckState.Unchecked)
            return Qt.CheckState.Unchecked
        else:
            item.setCheckState(0, Qt.CheckState.PartiallyChecked)
            return Qt.CheckState.PartiallyChecked

    def save_checked_items(self):
        for data_item, tree_item in self.record_items:
            data_item["selected"] = tree_item.checkState(0) == Qt.CheckState.Checked
        self.accept()

    def get_data(self):
        return self.data