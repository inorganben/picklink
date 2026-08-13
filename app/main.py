import sys
import tempfile
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from . import ai, crawler, screenshot, writer


class RecognizeWorker(QThread):
    done = Signal(dict)
    error = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            content = crawler.fetch_and_clean(self.url)
            path_tags = ai.ask_path_and_tags(content)
            summary = ai.ask_summary(content)
            self.done.emit({"content": content, "path_tags": path_tags, "summary": summary})
        except Exception as e:
            self.error.emit(str(e))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PickLink 自動收藏")
        self.resize(720, 640)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("貼上 URL")
        self.recognize_btn = QPushButton("開始識別")
        self.recognize_btn.clicked.connect(self.on_recognize)

        self.summary_edit = QTextEdit()
        self.summary_edit.setPlaceholderText("AI 總結（可直接修改）")
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("路徑，例如 Linux/發行版/Fedora")
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("標籤，逗號分隔")

        self.feedback_input = QLineEdit()
        self.feedback_input.setPlaceholderText("輸入修改意見後發送給 AI 重新改")
        self.feedback_btn = QPushButton("發送修改")
        self.feedback_btn.clicked.connect(self.on_feedback)

        self.accept_btn = QPushButton("接受並保存")
        self.accept_btn.clicked.connect(self.on_accept)

        self.status_label = QLabel("就緒")

        top = QHBoxLayout()
        top.addWidget(self.url_input, 1)
        top.addWidget(self.recognize_btn)

        fb = QHBoxLayout()
        fb.addWidget(self.feedback_input, 1)
        fb.addWidget(self.feedback_btn)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addWidget(QLabel("總結："))
        layout.addWidget(self.summary_edit)
        layout.addWidget(QLabel("路徑："))
        layout.addWidget(self.path_edit)
        layout.addWidget(QLabel("標籤："))
        layout.addWidget(self.tags_edit)
        layout.addLayout(fb)
        layout.addWidget(self.accept_btn)
        layout.addWidget(self.status_label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.content = None
        self.screenshot_path = None

    def on_recognize(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "請先貼上 URL")
            return
        self.status_label.setText("抓取與總結中…")
        self.recognize_btn.setEnabled(False)
        self.worker = RecognizeWorker(url)
        self.worker.done.connect(self.on_recognize_done)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_recognize_done(self, result):
        self.content = result["content"]
        self.summary_edit.setPlainText(result["summary"])
        self._apply_path_tags(result["path_tags"])
        self.recognize_btn.setEnabled(True)
        self.status_label.setText("識別完成，可修改或接受")

    def _apply_path_tags(self, text):
        tags = ""
        path = ""
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("標籤") or line.startswith("标签"):
                tags = line.split("：", 1)[-1].split(":", 1)[-1].strip()
            elif line.startswith("路徑") or line.startswith("路径"):
                path = line.split("：", 1)[-1].split(":", 1)[-1].strip()
        self.path_edit.setText(path)
        self.tags_edit.setText(tags)

    def on_feedback(self):
        feedback = self.feedback_input.text().strip()
        if not feedback or not self.content:
            return
        self.status_label.setText("AI 修改中…")
        self.feedback_btn.setEnabled(False)
        self.fb_worker = FeedbackWorker(self.content, feedback)
        self.fb_worker.done.connect(self.on_feedback_done)
        self.fb_worker.error.connect(self.on_error)
        self.fb_worker.start()

    def on_feedback_done(self, summary):
        self.summary_edit.setPlainText(summary)
        self.feedback_btn.setEnabled(True)
        self.feedback_input.clear()
        self.status_label.setText("已按意見修改總結")

    def on_accept(self):
        if not self.content:
            QMessageBox.warning(self, "提示", "尚未識別")
            return
        path = self.path_edit.text().strip()
        tags = self.tags_edit.text().strip()
        summary = self.summary_edit.toPlainText().strip()
        if not path or not tags or not summary:
            QMessageBox.warning(self, "提示", "總結、路徑、標籤不可為空")
            return
        self.status_label.setText("截圖與保存中…")
        self.save_worker = SaveWorker(
            self.url_input.text().strip(), summary, tags, path
        )
        self.save_worker.done.connect(self.on_save_done)
        self.save_worker.error.connect(self.on_error)
        self.save_worker.start()

    def on_save_done(self, msg):
        self.status_label.setText(msg)
        QMessageBox.information(self, "完成", msg)

    def on_error(self, err):
        self.recognize_btn.setEnabled(True)
        self.feedback_btn.setEnabled(True)
        self.status_label.setText(f"錯誤：{err}")
        QMessageBox.critical(self, "錯誤", err)


class FeedbackWorker(QThread):
    done = Signal(str)
    error = Signal(str)

    def __init__(self, content, feedback):
        super().__init__()
        self.content = content
        self.feedback = feedback

    def run(self):
        try:
            self.done.emit(ai.ask_summary(self.content, self.feedback))
        except Exception as e:
            self.error.emit(str(e))


class SaveWorker(QThread):
    done = Signal(str)
    error = Signal(str)

    def __init__(self, url, summary, tags, path):
        super().__init__()
        self.url = url
        self.summary = summary
        self.tags = tags
        self.path = path

    def run(self):
        try:
            with tempfile.TemporaryDirectory() as tmp:
                img = Path(tmp) / "shot.jpg"
                screenshot.screenshot(self.url, img)
                writer.save(self.url, self.summary, self.tags, self.path, img)
            if writer.commit(f"收藏：{self.path.split('/')[-1]}"):
                writer.push()
            self.done.emit("已保存並提交")
        except Exception as e:
            self.error.emit(str(e))


def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
