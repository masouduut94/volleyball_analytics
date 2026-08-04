from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox, QGroupBox, QFormLayout,
    QListWidget, QListWidgetItem, QRadioButton, QWidget, QHBoxLayout as QHBoxLayoutWidget
)
from PySide6.QtCore import Qt, Signal
from pathlib import Path


class ModelListItem(QWidget):
    # Signal to emit when delete is requested
    delete_requested = Signal(int)
    # Signal to emit when default selection changes
    default_changed = Signal(int)

    def __init__(self, model_data, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.model_id = model_data['id']
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayoutWidget(self)
        layout.setContentsMargins(5, 2, 5, 2)

        # Radio button for default selection
        self.radio_btn = QRadioButton()
        self.radio_btn.setFixedWidth(30)
        self.radio_btn.setChecked(self.model_data.get('is_default', False))
        self.radio_btn.toggled.connect(self.on_radio_toggled)
        layout.addWidget(self.radio_btn)

        # Model name label
        self.name_label = QLabel(self.model_data['name'])
        if self.model_data.get('is_default', False):
            self.name_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.name_label)

        layout.addStretch()

        # Delete button
        delete_btn = QPushButton("✕")
        delete_btn.setFixedSize(25, 25)
        delete_btn.setStyleSheet("""
            QPushButton { 
                background-color: #ff4444; 
                color: white; 
                border-radius: 12px; 
                border: none;
            } 
            QPushButton:hover { 
                background-color: #ff0000; 
            }
        """)
        delete_btn.clicked.connect(self.on_delete_clicked)
        layout.addWidget(delete_btn)

    def on_delete_clicked(self):
        """Emit delete signal when delete button is clicked."""
        self.delete_requested.emit(self.model_id)

    def on_radio_toggled(self, checked):
        """Emit default change signal when radio button is toggled."""
        if checked:
            self.default_changed.emit(self.model_id)

    def update_default_status(self, is_default):
        """Update the UI to reflect default status."""
        self.radio_btn.blockSignals(True)
        self.radio_btn.setChecked(is_default)
        self.radio_btn.blockSignals(False)

        if is_default:
            self.name_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.name_label.setStyleSheet("")


class YoloConfigDialog(QDialog):
    def __init__(self, parent=None, db=None, callback=None):
        super().__init__(parent)

        self.db = db
        self.callback = callback  # Callback function to call when model is selected
        self.models = []
        self.selected_model_path = None
        self.selected_model_name = None

        self.setWindowTitle("Court Detection Model Configuration")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.create_ui()
        self.load_models_from_db()

    def create_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Court Detection Models")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title_label)

        # Model list
        self.model_list = QListWidget()
        layout.addWidget(self.model_list)

        # Button row
        button_layout = QHBoxLayout()

        open_btn = QPushButton("Open Model")
        open_btn.clicked.connect(self.open_model_from_disk)
        button_layout.addWidget(open_btn)

        button_layout.addStretch()

        select_btn = QPushButton("Select")
        select_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 20px; }")
        select_btn.clicked.connect(self.select_model)
        button_layout.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def load_models_from_db(self):
        """Load models from database and display them."""
        if not self.db:
            return

        # Get models from database
        self.models = self.db.get_court_models()
        self.model_list.clear()

        for model in self.models:
            item = QListWidgetItem()
            widget = ModelListItem(model, self)

            # Connect signals
            widget.delete_requested.connect(self.delete_model)
            widget.default_changed.connect(self.set_default_model)

            item.setSizeHint(widget.sizeHint())
            self.model_list.addItem(item)
            self.model_list.setItemWidget(item, widget)

    def open_model_from_disk(self):
        """Open file dialog to select a model from disk."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Court Detection Model",
            "",
            "PyTorch Model (*.pt);;All Files (*.*)"
        )

        if file_path:
            # Add model to database
            model_name = Path(file_path).stem

            # Check if model already exists
            existing = self.db.get_court_model_by_path(file_path)
            if existing:
                QMessageBox.warning(
                    self,
                    "Model Already Exists",
                    f"Model '{model_name}' already exists in the database."
                )
                return

            # Add to database
            success = self.db.add_court_model(model_name, file_path)
            if success:
                QMessageBox.information(
                    self,
                    "Model Added",
                    f"Model '{model_name}' has been added successfully."
                )
                self.load_models_from_db()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to add model to database."
                )

    def set_default_model(self, model_id):
        """Set a model as default."""
        if not self.db:
            return

        success = self.db.set_default_court_model(model_id)
        if success:
            # Reload models to update UI
            self.load_models_from_db()
            QMessageBox.information(
                self,
                "Default Model Updated",
                "Default model has been updated successfully."
            )
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Failed to update default model."
            )

    def delete_model(self, model_id):
        """Delete a model from the database."""
        if not self.db:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this model?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            success = self.db.delete_court_model(model_id)
            if success:
                self.load_models_from_db()
                QMessageBox.information(
                    self,
                    "Model Deleted",
                    "Model has been deleted successfully."
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete model."
                )

    def select_model(self):
        """Select the default model and load it."""
        # Get the default model
        default_model = self.db.get_default_court_model() if self.db else None

        if not default_model:
            QMessageBox.warning(
                self,
                "No Default Model",
                "Please select a default model first using the radio button."
            )
            return

        # Store the selected model path
        self.selected_model_path = default_model['path']
        self.selected_model_name = default_model['name']

        # Call the callback if provided
        if self.callback:
            self.callback(self.selected_model_path)

        # Accept the dialog
        self.accept()