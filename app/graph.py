from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QScrollArea, QMenu, QFileDialog
from app.dialogs import critical
from pathlib import Path

class GraphCanvas(FigureCanvas):
    def wheelEvent(self, event):
        scroll_area = self.parentWidget()
        while scroll_area is not None:
            if isinstance(scroll_area, QScrollArea):
                break
            scroll_area = scroll_area.parentWidget()

        if scroll_area is None:
            super().wheelEvent(event)
            return

        scroll_bar = scroll_area.verticalScrollBar()
        scroll_amount = event.pixelDelta().y()

        if scroll_amount == 0:
            wheel_steps = event.angleDelta().y() / 120
            scroll_amount = int(wheel_steps * scroll_bar.singleStep() * 3)
        scroll_bar.setValue(scroll_bar.value() - scroll_amount)
        event.accept()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        save_action = menu.addAction("Save Graph as ...")

        selected_action = menu.exec(event.globalPos())

        if selected_action == save_action:
            self.save_graph()

    def save_graph(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(self, "Save Graph", "graph.png", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)")

        if not file_path:
            return

        save_path = Path(file_path)
        if save_path.suffix.lower() not in {".png", ".jpg", ".jpeg"}:
            suffix = ".png" if selected_filter == "PNG Files (*.png)" else ".jpg"
            save_path = save_path.with_suffix(suffix)
        try:
            self.figure.savefig(save_path, dpi=300, bbox_inches='tight')
        except Exception as e:
            critical("Error", f"Failed to save graph: {e}")


def create_graph_canvases(data, graph_type):
    export_data = []
    if graph_type == "raw data" or graph_type == "composition":
        for item in data:
            fig = Figure(figsize=(5, 4), dpi=100)
            canvas = GraphCanvas(fig)
            canvas.setMinimumHeight(400)
            ax = fig.add_subplot(111)
            ax.set_xlabel("Temperature (K)")
            ax.set_ylabel(rf"{item[-1][0]}")
            ax.set_title(rf"{item[-1][1]}")
            ax.grid(True, which='both', linestyle='--', linewidth=0.5)
            ax.set_xlim(item[-1][2][0], item[-1][2][1])
            for i in range(len(item)-1):
                ax.plot(item[i][0], item[i][1], label=rf"{item[i][2]}")
            ax.legend()
            export_data.append(canvas)
    return export_data
