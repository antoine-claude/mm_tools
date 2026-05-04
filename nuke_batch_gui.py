import sys
import os
import subprocess
import tempfile
from typing import Callable, Iterable, Optional
try:
    from PyQt5 import QtWidgets, QtCore
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5"])
    from PyQt5 import QtWidgets, QtCore

#Execute as no commercial --nc
# NUKE_EXECUTABLE = r"C:\Program Files\Nuke16.0v9\Nuke16.0.exe"
NUKE_EXECUTABLE = r"C:\Program Files\Nuke16.0v8\Nuke16.0.exe"

LogCb = Callable[[str], None]
PromptCreateMissingCb = Callable[[list[str]], bool]
ProgressCb = Callable[[int, int, str, str], None]

# Dictionnaire des extensions et codecs associés (exemple)
EXTENSION_CODECS = {
    ".mov": ["h264", "prores", "png"],
    ".mp4": ["h264", "h265"],
    ".exr": [],  # Pas de codec pour EXR
}

class FrameRangeWidget(QtWidgets.QWidget):
    removed = QtCore.pyqtSignal(str)  # Signal to notify when widget is removed
    
    def __init__(self, path):
        super().__init__()
        self.path = path

        layout = QtWidgets.QHBoxLayout()
        self.label = QtWidgets.QLabel(os.path.basename(path))
        self.range_label = QtWidgets.QLabel("Frame range: (auto from Write)")
        
        # Remove button
        self.remove_btn = QtWidgets.QPushButton("✕")
        self.remove_btn.setMaximumWidth(30)
        self.remove_btn.clicked.connect(self.on_remove)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.range_label)
        layout.addWidget(self.remove_btn)

        self.setLayout(layout)
    
    def on_remove(self):
        self.removed.emit(self.path)

    def get_data(self):
        return self.path

class DropListArea(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setSpacing(5)
        self.setLayout(self.layout)
        self.widgets = {}

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            # if path.endswith('.nknc') and path not in self.widgets:
            if path.endswith('.nkind') and path not in self.widgets:
                widget = FrameRangeWidget(path)
                widget.removed.connect(self.remove_widget)
                self.layout.addWidget(widget)
                self.widgets[path] = widget
    
    def remove_widget(self, path):
        if path in self.widgets:
            widget = self.widgets[path]
            self.layout.removeWidget(widget)
            widget.deleteLater()
            del self.widgets[path]

    def get_all_entries(self):
        return [w.get_data() for w in self.widgets.values()]

class BatchRenderApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuke Batch Renderer")
        self.setFixedSize(600, 600)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("🎬 Drag and drop Nuke files below:")
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

        self.file_area = DropListArea()
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.file_area)
        scroll.setMinimumHeight(200)
        layout.addWidget(scroll)

        # Extension selection
        ext_layout = QtWidgets.QHBoxLayout()
        ext_layout.addWidget(QtWidgets.QLabel("Output extension:"))
        self.ext_combo = QtWidgets.QComboBox()
        self.ext_combo.addItems([".mov", ".mp4", ".exr"])
        ext_layout.addWidget(self.ext_combo)
        layout.addLayout(ext_layout)

        # Codec selection (updated dynamically)
        #Hide codec widget if no ext
        self.codec_row = QtWidgets.QWidget()
        codec_layout = QtWidgets.QHBoxLayout(self.codec_row)
        codec_layout.setContentsMargins(0, 0, 0, 0)
        codec_layout.addWidget(QtWidgets.QLabel("Codec:"))
        self.codec_combo = QtWidgets.QComboBox()
        codec_layout.addWidget(self.codec_combo)
        layout.addWidget(self.codec_row)

        # Update codec list when extension changes
        self.ext_combo.currentTextChanged.connect(self.update_codec_list)
        self.update_codec_list()

        # Write node input
        form_layout = QtWidgets.QFormLayout()
        self.write_node_input = QtWidgets.QLineEdit("Write6")
        form_layout.addRow("Write Node:", self.write_node_input)
        layout.addLayout(form_layout)

        #Boolean box for headless mode default True
        self.headless_checkbox = QtWidgets.QCheckBox("Run in headless mode (no GUI)")
        self.headless_checkbox.setChecked(True)
        layout.addWidget(self.headless_checkbox)

        self.run_btn = QtWidgets.QPushButton("🚀 Start Batch Render")
        self.run_btn.clicked.connect(self.start_rendering)
        layout.addWidget(self.run_btn)

        self.output_box = QtWidgets.QTextEdit()
        self.output_box.setReadOnly(True)
        layout.addWidget(self.output_box)

        self.setLayout(layout)

        #Add progress bar with actual progress percentage, current file being rendered and ccurrent frame being rendered
        

    def update_codec_list(self):
        ext = self.ext_combo.currentText()
        codecs = EXTENSION_CODECS.get(ext)
        self.codec_combo.clear()

        if codecs:
            self.codec_combo.addItems(codecs)
            self.codec_row.setVisible(True)
        else:
            self.codec_row.setVisible(False)

    def log(self, message):
        self.output_box.append(message)
        self.output_box.ensureCursorVisible()

    def build_nuke_script(self, path, write_name, ext, codec):
        return f"""
import nuke
import os

nuke.scriptOpen(r"{path}")

w = nuke.toNode("{write_name}")

if not w or not w.Class() == "Write":
    raise Exception("Write node not found or invalid: {write_name}")

start = int(w.frameRange().first())
end = int(w.frameRange().last())

file_path = w["file"].value()
base_path = os.path.splitext(file_path)[0]
output_path = base_path + "{ext}"

w["file"].setValue(output_path)
w["file_type"].setValue("{ext[1:]}")  # Remove the dot for Nuke

if "{ext}" == ".mov" and "mov64_codec" in w.knobs():
    w["mov64_codec"].setValue("{codec}")
elif "{ext}" == ".mp4" and "mov64_codec" in w.knobs():
    w["mov64_codec"].setValue("{codec}")

print(f"Rendering frames: {{start}}-{{end}}")
print("Output:", output_path)

nuke.execute(w, start, end)
"""

    def start_rendering(self):
        jobs = self.file_area.get_all_entries()
        write_name = self.write_node_input.text().strip()
        ext = self.ext_combo.currentText()
        codec = self.codec_combo.currentText() if self.codec_combo.count() > 0 else ""

        if not jobs:
            self.log("⚠️ No Nuke files added.")
            return

        for path in jobs:
            if not os.path.exists(path):
                self.log(f"❌ File not found: {path}")
                continue

            self.log(f"\n▶ Rendering: {os.path.basename(path)}")
            self.log(f"   Write Node: {write_name}")
            self.log(f"   Output extension: {ext}")
            if codec:
                self.log(f"   Codec: {codec}")

            script = self.build_nuke_script(path, write_name, ext, codec)
            
            # Write script to temporary file
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
                    tmp_file.write(script)
                    tmp_script_path = tmp_file.name
                
                # Use -f to execute the script file instead of -c
                # cmd = f'"{NUKE_EXECUTABLE}" --nc -t -f "{tmp_script_path}"'
                if self.headless_checkbox.isChecked():
                    cmd = f'"{NUKE_EXECUTABLE}" --indie -t -f "{tmp_script_path}"'
                else:
                    cmd = f'"{NUKE_EXECUTABLE}" --indie -f "{tmp_script_path}"'
                self.log(f"   Executing: {' '.join(cmd.split()[:3])}...")

                try:
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True
                    )

                    if result.stdout:
                        self.log(result.stdout)

                    if result.returncode == 0:
                        self.log("✅ Render complete")
                    else:
                        self.log("❌ Render failed")
                        if result.stderr:
                            self.log(result.stderr)

                except Exception as e:
                    self.log(f"⚠️ Exception occurred: {e}")
                
                finally:
                    # Clean up temporary file
                    if os.path.exists(tmp_script_path):
                        try:
                            os.remove(tmp_script_path)
                        except:
                            pass
                        
            except Exception as e:
                self.log(f"⚠️ Failed to create temp script: {e}")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = BatchRenderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
