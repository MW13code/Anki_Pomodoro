# settings_window.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QSpinBox, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import json
import os

class Settings:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.load_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.pomodoro_sessions = data.get('pomodoro_sessions', 4)
                self.session_duration = data.get('session_duration', 25 * 60)
                self.short_breaks = data.get('short_breaks', 5 * 60)
                self.long_breaks = data.get('long_breaks', 15 * 60)
                self.sessions_before_long_break = data.get('sessions_before_long_break', 4)
                self.sessions_completed = data.get('sessions_completed', 0)
                self.remaining_time = data.get('remaining_time', self.session_duration)
                self.is_timer_running = data.get('is_timer_running', False)
            except Exception:
                self.set_default_settings()
        else:
            self.set_default_settings()

    def set_default_settings(self):
        self.pomodoro_sessions = 4
        self.session_duration = 25 * 60
        self.short_breaks = 5 * 60
        self.long_breaks = 15 * 60
        self.sessions_before_long_break = 4
        self.sessions_completed = 0
        self.remaining_time = self.session_duration
        self.is_timer_running = False
        self.save_settings()

    def save_settings(self):
        data = {
            'pomodoro_sessions': self.pomodoro_sessions,
            'session_duration': self.session_duration,
            'short_breaks': self.short_breaks,
            'long_breaks': self.long_breaks,
            'sessions_before_long_break': self.sessions_before_long_break,
            'sessions_completed': self.sessions_completed,
            'remaining_time': self.remaining_time,
            'is_timer_running': self.is_timer_running
        }
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

class SettingsWindow(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Ustawienia Minutnika Pomodoro")
        self.setModal(True)
        self.setFixedSize(300, 300)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        pomodoro_layout = QHBoxLayout()
        pomodoro_label = QLabel("Liczba serii Pomodoro:")
        self.pomodoro_spin = QSpinBox()
        self.pomodoro_spin.setRange(1, 100)
        self.pomodoro_spin.setValue(self.settings.pomodoro_sessions)
        pomodoro_layout.addWidget(pomodoro_label)
        pomodoro_layout.addWidget(self.pomodoro_spin)
        layout.addLayout(pomodoro_layout)

        session_layout = QHBoxLayout()
        session_label = QLabel("Czas trwania sesji (min):")
        self.session_spin = QSpinBox()
        self.session_spin.setRange(1, 240)
        self.session_spin.setValue(self.settings.session_duration // 60)
        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_spin)
        layout.addLayout(session_layout)

        short_break_layout = QHBoxLayout()
        short_break_label = QLabel("Czas krótkiej przerwy (min):")
        self.short_break_spin = QSpinBox()
        self.short_break_spin.setRange(1, 120)
        self.short_break_spin.setValue(self.settings.short_breaks // 60)
        short_break_layout.addWidget(short_break_label)
        short_break_layout.addWidget(self.short_break_spin)
        layout.addLayout(short_break_layout)

        long_break_layout = QHBoxLayout()
        long_break_label = QLabel("Czas długiej przerwy (min):")
        self.long_break_spin = QSpinBox()
        self.long_break_spin.setRange(1, 300)
        self.long_break_spin.setValue(self.settings.long_breaks // 60)
        long_break_layout.addWidget(long_break_label)
        long_break_layout.addWidget(self.long_break_spin)
        layout.addLayout(long_break_layout)

        sessions_before_layout = QHBoxLayout()
        sessions_before_label = QLabel("Sesji przed długą przerwą:")
        self.sessions_before_spin = QSpinBox()
        self.sessions_before_spin.setRange(1, 100)
        self.sessions_before_spin.setValue(self.settings.sessions_before_long_break)
        sessions_before_layout.addWidget(sessions_before_label)
        sessions_before_layout.addWidget(self.sessions_before_spin)
        layout.addLayout(sessions_before_layout)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Zapisz")
        save_button.clicked.connect(self.save_settings)
        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_settings(self):
        self.settings.pomodoro_sessions = self.pomodoro_spin.value()
        self.settings.session_duration = self.session_spin.value() * 60
        self.settings.short_breaks = self.short_break_spin.value() * 60
        self.settings.long_breaks = self.long_break_spin.value() * 60
        self.settings.sessions_before_long_break = self.sessions_before_spin.value()
        self.settings.save_settings()
        QMessageBox.information(self, "Ustawienia", "Ustawienia zostały zapisane.")
        self.accept()

