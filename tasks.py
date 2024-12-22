# tasks.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QWidget, QMessageBox
)
from .tasks_up import HtmlWidgetUp
from .tasks_down import HtmlWidgetDown
from .settings_window import Settings, SettingsWindow
from PyQt6.QtCore import pyqtSignal, pyqtSlot
import os

class TasksSidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        addon_dir = os.path.dirname(__file__)
        settings_file = os.path.join(addon_dir, 'settings.json')
        self.settings = Settings(settings_file)

        self.settings_window = SettingsWindow(self.settings, self)

        self.widget_up = HtmlWidgetUp(self.settings)
        self.layout().addWidget(self.widget_up)

        self.widget_down = HtmlWidgetDown()
        self.layout().addWidget(self.widget_down)

        self.widget_down.task_completed.connect(self.handle_task_completed)
        self.widget_up.timer_finished.connect(self.handle_timer_finished)

    @pyqtSlot()
    def handle_task_completed(self):
        self.settings.sessions_completed += 1
        self.settings.save_settings()

        if self.settings.sessions_completed % self.settings.sessions_before_long_break == 0:
            self.settings.remaining_time = self.settings.long_breaks
            self.settings.session_duration = self.settings.long_breaks
            self.widget_up.progress_bar.setMaximum(self.settings.long_breaks)
            self.widget_up.progress_bar.setValue(0)
            self.widget_up.update_time_label()
            QMessageBox.information(self, "Przerwa", "Czas na długą przerwę!")
        else:
            self.settings.remaining_time = self.settings.short_breaks
            self.settings.session_duration = self.settings.short_breaks
            self.widget_up.progress_bar.setMaximum(self.settings.short_breaks)
            self.widget_up.progress_bar.setValue(0)
            self.widget_up.update_time_label()
            QMessageBox.information(self, "Przerwa", "Czas na krótką przerwę!")
        
        self.widget_up.start_timer()

    @pyqtSlot()
    def handle_timer_finished(self):
        QMessageBox.information(self, "Minutnik", "Czas minął!")

