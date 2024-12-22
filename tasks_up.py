# tasks_up.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout,
    QProgressBar, QMessageBox, QToolButton
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QIcon
import os
import json

class HtmlWidgetUp(QWidget):
    timer_finished = pyqtSignal()

    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setLayout(QVBoxLayout())

        header_layout = QHBoxLayout()

        title_label = QLabel("Minutnik Pomodoro")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)

        self.settings_button = QToolButton()
        self.settings_button.setIcon(QIcon.fromTheme("configure"))
        self.settings_button.setToolTip("Ustawienia Minutnika")
        self.settings_button.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_button)

        self.layout().addLayout(header_layout)

        self.time_label = QLabel(self.format_time(self.settings.remaining_time))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("font-size: 48px;")
        self.layout().addWidget(self.time_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(self.settings.session_duration)
        self.progress_bar.setValue(self.settings.session_duration - self.settings.remaining_time)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 20px;
            }
        """)
        self.layout().addWidget(self.progress_bar)

        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        button_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        button_layout.addWidget(self.pause_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setEnabled(self.settings.remaining_time != self.settings.session_duration)
        button_layout.addWidget(self.reset_button)

        self.layout().addLayout(button_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        if self.settings.is_timer_running:
            self.timer.start(1000)
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.reset_button.setEnabled(True)

    def open_settings(self):
        self.settings_window = self.parent().parent().settings_window
        self.settings_window.show()

    def start_timer(self):
        self.timer.start(1000)
        self.settings.is_timer_running = True
        self.settings.save_settings()
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.reset_button.setEnabled(True)

    def pause_timer(self):
        self.timer.stop()
        self.settings.is_timer_running = False
        self.settings.save_settings()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)

    def reset_timer(self):
        self.timer.stop()
        self.settings.remaining_time = self.settings.session_duration
        self.settings.is_timer_running = False
        self.settings.save_settings()
        self.update_time_label()
        self.progress_bar.setMaximum(self.settings.session_duration)
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.reset_button.setEnabled(False)

    def update_timer(self):
        if self.settings.remaining_time > 0:
            self.settings.remaining_time -= 1
            self.settings.save_settings()
            self.update_time_label()
            self.progress_bar.setValue(self.settings.session_duration - self.settings.remaining_time)
        else:
            self.timer.stop()
            self.settings.is_timer_running = False
            self.settings.save_settings()
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            self.reset_button.setEnabled(True)
            self.time_label.setText("Czas minął!")
            self.timer_finished.emit()

    def update_time_label(self):
        self.time_label.setText(self.format_time(self.settings.remaining_time))

    def format_time(self, seconds):
        minutes = seconds // 60
        sec = seconds % 60
        return f"{minutes:02d}:{sec:02d}"

