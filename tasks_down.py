# tasks_down.py
import os
import json
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QMenu,
    QInputDialog
)
from PyQt6.QtCore import pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QKeySequence

class AddTaskLineEdit(QLineEdit):
    """Subclass QLineEdit to handle Ctrl+Enter for adding tasks."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.parent_widget.add_task_from_input()
        else:
            super().keyPressEvent(event)


class HtmlWidgetDown(QWidget):
    # Sygnał emitowany, gdy zadanie zostanie zaznaczone lub odznaczone
    task_completed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())

        # Ścieżka do pliku z zadaniami
        self.tasks_file = os.path.join(os.path.dirname(__file__), 'tasks.json')

        # Tytuł
        title_label = QLabel("Lista Zadań")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.layout().addWidget(title_label)

        # Pole do dodawania nowych zadań z obsługą Ctrl+Enter
        add_layout = QHBoxLayout()
        self.task_input = AddTaskLineEdit(self)
        self.task_input.setPlaceholderText("Wpisz nowe zadanie...")
        add_layout.addWidget(self.task_input)

        self.add_button = QPushButton("Dodaj")
        self.add_button.clicked.connect(self.add_task_from_input)
        add_layout.addWidget(self.add_button)

        self.layout().addLayout(add_layout)

        # Lista zadań z możliwością drag and drop
        self.task_list = QListWidget()
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.open_context_menu)
        self.task_list.itemDoubleClicked.connect(self.edit_task)

        # Konfiguracja drag and drop
        self.task_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.task_list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.task_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.task_list.setDragEnabled(True)
        self.task_list.setAcceptDrops(True)
        self.task_list.setDropIndicatorShown(True)

        # Podłącz sygnał do zapisywania zadań po zmianie kolejności
        self.task_list.model().rowsMoved.connect(self.save_tasks)

        self.layout().addWidget(self.task_list)

        # Przycisk do usuwania zaznaczonych zadań
        delete_layout = QHBoxLayout()
        self.delete_button = QPushButton("Usuń zaznaczone")
        self.delete_button.clicked.connect(self.delete_selected_tasks)
        delete_layout.addWidget(self.delete_button)
        self.layout().addLayout(delete_layout)

        # Wczytaj zadania z pliku
        self.load_tasks()

    def load_tasks(self):
        """Ładuje zadania z pliku JSON."""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        tasks = []
                    else:
                        tasks = json.loads(content)
                for task in tasks:
                    self.add_task(task['name'], task['completed'], task.get('affected', False))
            except json.JSONDecodeError as e:
                QMessageBox.warning(self, "Błąd", f"Nieprawidłowy format JSON w pliku zadań: {e}")
                # Inicjalizacja pustej listy zadań
                self.save_tasks()
            except Exception as e:
                QMessageBox.warning(self, "Błąd", f"Nie można załadować zadań: {e}")

    def save_tasks(self):
        """Zapisuje bieżące zadania do pliku JSON."""
        tasks = []
        for index in range(self.task_list.count()):
            item = self.task_list.item(index)
            checkbox = self.task_list.itemWidget(item)
            tasks.append({
                'name': checkbox.text(),
                'completed': checkbox.isChecked(),
                'affected': getattr(checkbox, 'affected', False)  # Śledzenie, czy zadanie już wpłynęło na minutnik
            })
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Błąd", f"Nie można zapisać zadań: {e}")

    def add_task_from_input(self):
        """Dodaje zadanie z pola tekstowego."""
        task_name = self.task_input.text().strip()
        if task_name:
            # Sprawdzenie, czy zadanie już istnieje
            for index in range(self.task_list.count()):
                item = self.task_list.item(index)
                checkbox = self.task_list.itemWidget(item)
                if checkbox.text().lower() == task_name.lower():
                    QMessageBox.information(self, "Informacja", "To zadanie już istnieje.")
                    return
            self.add_task(task_name)
            self.task_input.clear()
            self.save_tasks()
        else:
            QMessageBox.information(self, "Informacja", "Proszę wpisać nazwę zadania.")

    def add_task(self, task_name, completed=False, affected=False):
        """Dodaje zadanie do listy."""
        item = QListWidgetItem()
        checkbox = QCheckBox(task_name)
        checkbox.setChecked(completed)
        checkbox.affected = affected  # Dodanie atrybutu śledzącego wpływ na minutnik
        checkbox.stateChanged.connect(self.on_task_state_changed)
        self.task_list.addItem(item)
        self.task_list.setItemWidget(item, checkbox)
        if completed:
            checkbox.setStyleSheet("text-decoration: line-through; color: gray;")
        else:
            checkbox.setStyleSheet("")

    def on_task_state_changed(self, state):
        """Reaguje na zmianę stanu checkboxa."""
        checkbox = self.sender()
        if state == Qt.CheckState.Checked.value:
            if not getattr(checkbox, 'affected', False):
                self.task_completed.emit()
                checkbox.affected = True  # Oznaczenie, że zadanie wpłynęło na minutnik
                checkbox.setStyleSheet("text-decoration: line-through; color: gray;")
                self.save_tasks()
        else:
            # Opcjonalnie: Możesz zdezaktywować wpływ na minutnik, jeśli zadanie jest odznaczone
            # Jeśli chcesz, aby odznaczenie mogło ponownie wpływać, ustaw 'affected' na False
            # checkbox.affected = False
            # self.save_tasks()
            pass
            checkbox.setStyleSheet("")
            self.save_tasks()

    def open_context_menu(self, position: QPoint):
        """Otwiera menu kontekstowe."""
        menu = QMenu()
        edit_action = menu.addAction("Edytuj")
        delete_action = menu.addAction("Usuń")
        action = menu.exec(self.task_list.viewport().mapToGlobal(position))
        if action == edit_action:
            item = self.task_list.itemAt(position)
            if item:
                self.edit_task(item)
        elif action == delete_action:
            self.delete_task_at_position(position)

    def edit_task(self, item: QListWidgetItem):
        """Pozwala na edycję nazwy zadania."""
        checkbox = self.task_list.itemWidget(item)
        new_name, ok = QInputDialog.getText(self, "Edytuj Zadanie", "Nowa nazwa zadania:", text=checkbox.text())
        if ok and new_name.strip():
            # Sprawdzenie, czy zadanie już istnieje
            for index in range(self.task_list.count()):
                existing_item = self.task_list.item(index)
                existing_checkbox = self.task_list.itemWidget(existing_item)
                if existing_checkbox.text().lower() == new_name.strip().lower() and existing_checkbox != checkbox:
                    QMessageBox.information(self, "Informacja", "To zadanie już istnieje.")
                    return
            checkbox.setText(new_name.strip())
            self.save_tasks()

    def delete_task_at_position(self, position: QPoint):
        """Usuwa zadanie znajdujące się w danym położeniu."""
        item = self.task_list.itemAt(position)
        if item:
            row = self.task_list.row(item)
            self.task_list.takeItem(row)
            self.save_tasks()

    def delete_selected_tasks(self):
        """Usuwa wszystkie zaznaczone zadania."""
        items_to_delete = []
        for index in range(self.task_list.count()):
            item = self.task_list.item(index)
            checkbox = self.task_list.itemWidget(item)
            if checkbox.isChecked():
                items_to_delete.append(item)
        if not items_to_delete:
            QMessageBox.information(self, "Informacja", "Nie wybrano żadnych zadań do usunięcia.")
            return
        for item in items_to_delete:
            row = self.task_list.row(item)
            self.task_list.takeItem(row)
        self.save_tasks()

