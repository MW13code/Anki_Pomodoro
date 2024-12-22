# __init__.py
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QSplitter, QMessageBox
from aqt import mw
from aqt.utils import showInfo
from .tasks import TasksSidebar

def open_combined_sidebar():
    if not hasattr(mw, "pomodoro_splitter"):
        mw.original_central_widget = mw.centralWidget()
        splitter = QSplitter(mw)

        tasks_sidebar = TasksSidebar()
        splitter.addWidget(tasks_sidebar)

        splitter.addWidget(mw.original_central_widget)

        splitter.setSizes([400, 1000])

        mw.setCentralWidget(splitter)

        mw.pomodoro_splitter = splitter
        mw.pomodoro_splitter_visible = True
    else:
        splitter = mw.pomodoro_splitter
        if mw.pomodoro_splitter_visible:
            splitter.hide()
            mw.pomodoro_splitter_visible = False
        else:
            splitter.show()
            mw.pomodoro_splitter_visible = True

def init_addon():
    action = QAction("🍅", mw)
    action.triggered.connect(open_combined_sidebar)
    mw.menuBar().addAction(action)

init_addon()

