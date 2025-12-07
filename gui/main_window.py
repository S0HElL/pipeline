"""
Manga Translator GUI - Main Window
Main application window for the manga translation GUI with fixed font loading, UI layout, and text style updates.
"""

import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QProgressBar,
    QTextEdit, QSpinBox, QComboBox, QColorDialog, QDockWidget,
    QToolBar, QStatusBar, QMenuBar, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QPixmap, QAction, QIcon, QFontDatabase

# Import our custom modules with proper path handling
def import_gui_modules():
    """Import GUI modules with proper path handling"""
    try:
        # First try direct imports
        from editor_canvas import EditorCanvas
        from translation_worker import TranslationWorker
        return EditorCanvas, TranslationWorker
    except ImportError:
        # Handle case when running from the main directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Add paths to sys.path
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        try:
            from editor_canvas import EditorCanvas
            from translation_worker import TranslationWorker
            return EditorCanvas, TranslationWorker
        except ImportError:
            # Final fallback - create placeholder classes for testing
            print("Warning: Could not import GUI modules. Creating placeholder classes.")
            
            class EditorCanvas(QWidget):
                def __init__(self):
                    super().__init__()
                    self.setMinimumSize(800, 600)
                    label = QLabel("Editor Canvas (Import Failed)")
                    layout = QVBoxLayout()
                    layout.addWidget(label)
                    self.setLayout(layout)
                
                def load_image(self, path): pass
                def update_text_style(self): pass
                def set_inpainted_image(self, img): pass
                def set_translation_data(self, data): pass
                def update_text_preview(self, index, text): pass
                def set_text_color(self, color): pass
                def get_final_image(self): return None
            
            class TranslationWorker(QThread):
                finished = Signal(object, object)
                error = Signal(str)
                progress = Signal(str)
                
                def __init__(self, image_path):
                    super().__init__()
                    self.image_path = image_path
                    
                def run(self):
                    self.progress.emit("Translation worker not available.")
                    self.error.emit("GUI modules failed to import.")
            
            return EditorCanvas, TranslationWorker

# Import the modules
EditorCanvas, TranslationWorker = import_gui_modules()


class MainWindow(QMainWindow):
    """
    Main application window for the Manga Translator GUI.
    
    This window provides:
    - Image upload and display
    - Translation pipeline execution
    - Text editing and typesetting controls
    - Final image saving
    Fixed issues:
    - Proper font loading from ../fonts directory
    - Fixed UI layout to prevent overlap
    - Proper text style update mechanism
    - Resizable bounding boxes (via EditorCanvas)
    """
    
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.translation_worker = None
        self.translated_data = []
        
        # Undo/Redo stacks
        self.undo_stack = []
        self.redo_stack = []
        
        self._updating_text = False
        
        self.init_ui()
        self.setup_connections()
        
        
    def init_ui(self):
        """Initialize the user interface components."""
        self.setWindowTitle("Manga Translator - GUI Editor")
        self.setMinimumSize(1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create editor canvas (main image display area)
        self.canvas = EditorCanvas()
        self.canvas.setMinimumSize(800, 600)
        main_layout.addWidget(self.canvas)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create status bar
        self.create_status_bar()
        
        # Create dock widgets for text editing and typesetting (these handle file operations too)
        self.create_dock_widgets()
        
    def save_state(self):
        """Save current state for undo."""
        if self.translated_data:
            # Deep copy the current state
            import copy
            state = copy.deepcopy(self.translated_data)
            self.undo_stack.append(state)
            self.redo_stack.clear()  # Clear redo stack when new action is performed
        
    def undo(self):
        """Undo the last action."""
        if self.undo_stack:
            # Save current state to redo stack
            import copy
            self.redo_stack.append(copy.deepcopy(self.translated_data))
            
            # Restore previous state
            self.translated_data = self.undo_stack.pop()
            
            # Update canvas
            try:
                self.canvas.set_translation_data(self.translated_data)
            except Exception as e:
                print(f"Error during undo: {e}")
                
    def redo(self):
        """Redo the last undone action."""
        if self.redo_stack:
            # Save current state to undo stack
            import copy
            self.undo_stack.append(copy.deepcopy(self.translated_data))
            
            # Restore redo state
            self.translated_data = self.redo_stack.pop()
            
            # Update canvas
            try:
                self.canvas.set_translation_data(self.translated_data)
            except Exception as e:
                print(f"Error during redo: {e}")

    def zoom_in(self):
        """Zoom in the canvas."""
        try:
            self.canvas.zoom_in()
            zoom_pct = int(self.canvas.zoom_factor * 100)
            self.zoom_label.setText(f"Zoom: {zoom_pct}%")
        except AttributeError:
            pass
            
    def zoom_out(self):
        """Zoom out the canvas."""
        try:
            self.canvas.zoom_out()
            zoom_pct = int(self.canvas.zoom_factor * 100)
            self.zoom_label.setText(f"Zoom: {zoom_pct}%")
        except AttributeError:
            pass
            
    def zoom_fit(self):
        """Fit image to window."""
        try:
            self.canvas.reset_zoom()
            self.zoom_label.setText("Zoom: 100%")
        except AttributeError:
            pass
        
    def activate_eyedropper(self):
        """Activate the eye dropper tool."""
        try:
            self.canvas.setCursor(Qt.CrossCursor)
            self.canvas.eyedropper_active = True
            self.status_bar.showMessage("Click on the image to pick a color. Press ESC to cancel.")
        except AttributeError:
            pass

    def on_color_picked(self, color):
        """Handle color picked from eye dropper."""
        if color and color.isValid():
            self.canvas.current_text_color = color.name()
            self.canvas.update_text_style()
            self.status_bar.showMessage(f"Color picked: {color.name()}")
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open Image...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.upload_image)
        file_menu.addAction(open_action)
        
        save_action = QAction('Save Image...', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_final_image)
        save_action.setEnabled(False)
        file_menu.addAction(save_action)
        self.save_action = save_action
        
        file_menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('Edit')
        
        # Undo/Redo actions - NOW CONNECTED
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        self.undo_action = undo_action
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        self.redo_action = redo_action
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Zoom actions - NOW CONNECTED
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setShortcut('Ctrl++')
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setShortcut('Ctrl+-')
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction('Fit to Window', self)
        zoom_fit_action.triggered.connect(self.zoom_fit)
        view_menu.addAction(zoom_fit_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = self.addToolBar('Main')
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # File operations
        open_action = QAction('Open', self)
        open_action.setToolTip('Open Image (Ctrl+O)')
        open_action.triggered.connect(self.upload_image)
        toolbar.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setToolTip('Save Final Image (Ctrl+S)')
        save_action.triggered.connect(self.save_final_image)
        save_action.setEnabled(False)
        toolbar.addAction(save_action)
        self.save_toolbar_action = save_action
        
        toolbar.addSeparator()
        
        # Translation
        translate_action = QAction('Translate', self)
        translate_action.setToolTip('Run Translation Pipeline')
        translate_action.triggered.connect(self.start_translation)
        translate_action.setEnabled(False)
        toolbar.addAction(translate_action)
        self.translate_toolbar_action = translate_action
        
        toolbar.addSeparator()
        
        # View controls - NOW CONNECTED
        zoom_in_action = QAction('Zoom In', self)
        zoom_in_action.setToolTip('Zoom In (Ctrl++)')
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction('Zoom Out', self)
        zoom_out_action.setToolTip('Zoom Out (Ctrl+-)')
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        zoom_fit_action = QAction('Fit to Window', self)
        zoom_fit_action.setToolTip('Fit Image to Window')
        zoom_fit_action.triggered.connect(self.zoom_fit)
        toolbar.addAction(zoom_fit_action)
        
    def create_status_bar(self):
        """Create the application status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Add permanent widgets to status bar
        self.coord_label = QLabel("Coords: -")
        self.coord_label.setMinimumWidth(120)
        self.status_bar.addPermanentWidget(self.coord_label)
        
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setMinimumWidth(80)
        self.status_bar.addPermanentWidget(self.zoom_label)
        
    def create_dock_widgets(self):
        """Create dock widgets for file operations, text editing and typesetting."""
        
        # File operations dock (replaces the old control panel)
        file_dock = QDockWidget("File Operations", self)
        file_dock.setAllowedAreas(Qt.RightDockWidgetArea)
        
        file_widget = QWidget()
        file_layout = QVBoxLayout(file_widget)
        
        self.upload_btn = QPushButton("Upload Image")
        self.upload_btn.setMinimumHeight(40)
        
        self.tl_btn = QPushButton("Translate (TL)")
        self.tl_btn.setMinimumHeight(40)
        self.tl_btn.setEnabled(False)  # Enabled after image upload
        
        self.save_btn = QPushButton("Save Final Image")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setEnabled(False)  # Enabled after translation
        
        # Progress section
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.status_label = QLabel("Ready")
        
        file_layout.addWidget(self.upload_btn)
        file_layout.addWidget(self.tl_btn)
        file_layout.addWidget(self.save_btn)
        file_layout.addWidget(self.progress_bar)
        file_layout.addWidget(self.status_label)
        file_layout.addStretch()
        
        file_dock.setWidget(file_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, file_dock)
        self.file_dock = file_dock
        
        # Text editing dock
        self.text_edit_dock = QDockWidget("Text Editor", self)
        self.text_edit_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        text_edit_widget = QWidget()
        text_edit_layout = QVBoxLayout(text_edit_widget)
        
        self.text_edit_label = QLabel("Select a text region to edit:")
        self.text_edit = QTextEdit()
        self.text_edit.setMaximumHeight(150)
        self.text_edit.setPlaceholderText("Translated text will appear here...")
        
        text_edit_layout.addWidget(self.text_edit_label)
        text_edit_layout.addWidget(self.text_edit)
        text_edit_layout.addStretch()
        
        self.text_edit_dock.setWidget(text_edit_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.text_edit_dock)
        self.text_edit_dock.hide()
        
        # Typesetting controls dock
        self.typesetting_dock = QDockWidget("Typesetting", self)
        self.typesetting_dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        
        typesetting_widget = QWidget()
        typesetting_layout = QVBoxLayout(typesetting_widget)
        
        # Font family
        font_label = QLabel("Font Family:")
        self.font_combo = QComboBox()
        self.populate_font_combo()
        
        # Font size
        size_label = QLabel("Font Size:")
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.font_size_spin.setValue(20)
        
        # Text color
        color_label = QLabel("Text Color:")
        color_layout = QHBoxLayout()
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_text_color)

        self.eyedropper_btn = QPushButton("Eye Dropper")
        self.eyedropper_btn.clicked.connect(self.activate_eyedropper)
        self.eyedropper_btn.setToolTip("Pick color from image")

        color_layout.addWidget(self.color_btn)
        color_layout.addWidget(self.eyedropper_btn)
                
        # Alignment
        align_label = QLabel("Text Alignment:")
        self.align_combo = QComboBox()
        self.align_combo.addItems(["Left", "Center", "Right"])
        
        typesetting_layout.addWidget(font_label)
        typesetting_layout.addWidget(self.font_combo)
        typesetting_layout.addWidget(size_label)
        typesetting_layout.addWidget(self.font_size_spin)
        typesetting_layout.addWidget(color_label)
        typesetting_layout.addLayout(color_layout)  # Changed from addWidget to addLayout
        typesetting_layout.addWidget(align_label)
        typesetting_layout.addWidget(self.align_combo)
        typesetting_layout.addStretch()
        
        self.typesetting_dock.setWidget(typesetting_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.typesetting_dock)
        self.typesetting_dock.hide()
        
        # Tabify docks for better organization
        self.tabifyDockWidget(file_dock, self.text_edit_dock)
        self.tabifyDockWidget(file_dock, self.typesetting_dock)
        
        # Connect typesetting controls to canvas
        self.font_combo.currentTextChanged.connect(self.on_font_changed)
        self.font_size_spin.valueChanged.connect(self.on_font_size_changed)
        self.align_combo.currentTextChanged.connect(self.on_alignment_changed)
        
    def populate_font_combo(self):
        """Populate the font combo box with available fonts."""
        # Fix font path to look in parent directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        font_dir = os.path.join(current_dir, "..", "fonts")
        
        loaded_fonts = []
        if os.path.exists(font_dir):
            # Load and register custom fonts
            for filename in os.listdir(font_dir):
                if filename.lower().endswith(('.ttf', '.otf')):
                    font_path = os.path.join(font_dir, filename)
                    file_base_name = os.path.splitext(filename)
                    
                    try:
                        # Load font using QFontDatabase
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            # Use the actual font family name
                            font_families = QFontDatabase.applicationFontFamilies(font_id)
                            if font_families:
                                font_family_str = font_families[0] # Get the first family name as a string
                                self.font_combo.addItem(font_family_str)
                                loaded_fonts.append(font_family_str)
                            else:
                                file_name_str = file_base_name[0] # Get the base name as a string
                                self.font_combo.addItem(file_name_str)
                                loaded_fonts.append(file_name_str)
                        else:
                            file_name_str = file_base_name[0] # Get the base name as a string
                            self.font_combo.addItem(file_name_str)
                            loaded_fonts.append(file_name_str)
                    except Exception as e:
                        print(f"Failed to load font {filename}: {e}")
                        file_name_str = file_base_name[0] # Get the base name as a string
                        self.font_combo.addItem(file_name_str)
                        loaded_fonts.append(file_name_str)
        
        # Add some default fonts
        default_fonts = ["Arial", "Times New Roman", "Helvetica", "Comic Sans MS"]
        for font in default_fonts:
            if font not in loaded_fonts:  # Avoid duplicates
                self.font_combo.addItem(font)
                
    def setup_connections(self):
        """Connect UI signals to slots."""
        # File operations
        self.upload_btn.clicked.connect(self.upload_image)
        self.tl_btn.clicked.connect(self.start_translation)
        self.save_btn.clicked.connect(self.save_final_image)
        
        # Canvas selection changed
        try:
            if hasattr(self.canvas, 'selection_changed'):
                self.canvas.selection_changed.connect(self.on_selection_changed)
            if hasattr(self.canvas, 'color_picked'):
                self.canvas.color_picked.connect(self.on_color_picked)
        except AttributeError:
            pass
        
        # Text editing connections
        self.text_edit.textChanged.connect(self.on_text_edited)
        
    def on_font_changed(self, font_family):
        """Handle font family changes."""
        self.canvas.current_font_family = font_family
        self.canvas.update_text_style()
        
    def on_font_size_changed(self, font_size):
        """Handle font size changes."""
        self.canvas.current_font_size = font_size
        self.canvas.update_text_style()
        
    def on_alignment_changed(self, alignment):
        """Handle alignment changes."""
        self.canvas.current_alignment = alignment
        self.canvas.update_text_style()
        
    def upload_image(self):
        """Open file dialog to upload an image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Manga Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff);;All Files (*)"
        )
        
        if file_path:
            self.current_image_path = file_path
            try:
                self.canvas.load_image(file_path)
            except Exception as e:
                QMessageBox.warning(self, "Warning", f"Could not load image: {str(e)}")
                return
            
            # Update UI state
            self.tl_btn.setEnabled(True)
            self.translate_toolbar_action.setEnabled(True)
            self.save_btn.setEnabled(False)
            self.save_action.setEnabled(False)
            self.save_toolbar_action.setEnabled(False)
            
            self.status_bar.showMessage(f"Loaded: {file_path}")
            
    def start_translation(self):
        """Start the translation pipeline in a background thread."""
        if not self.current_image_path:
            QMessageBox.warning(self, "Warning", "Please upload an image first.")
            return
            
        # Disable translation button during processing
        self.tl_btn.setEnabled(False)
        self.translate_toolbar_action.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.showMessage("Starting translation...")
        
        # Create and start worker thread
        try:
            self.translation_worker = TranslationWorker(self.current_image_path)
            self.translation_worker.finished.connect(self.on_translation_finished)
            self.translation_worker.error.connect(self.on_translation_error)
            self.translation_worker.progress.connect(self.on_translation_progress)
            
            self.translation_worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start translation worker: {str(e)}")
            self.tl_btn.setEnabled(True)
            self.translate_toolbar_action.setEnabled(True)
            self.progress_bar.setVisible(False)
            
    def on_translation_finished(self, inpainted_image, translated_data):
        """Handle translation completion."""
        self.progress_bar.setVisible(False)
        self.tl_btn.setEnabled(True)
        self.translate_toolbar_action.setEnabled(True)
        
        self.translated_data = translated_data
        
        # Update canvas with results
        try:
            if inpainted_image:
                self.canvas.set_inpainted_image(inpainted_image)
            self.canvas.set_translation_data(translated_data)
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Could not update canvas: {str(e)}")
        
        # Enable save button
        self.save_btn.setEnabled(True)
        self.save_action.setEnabled(True)
        self.save_toolbar_action.setEnabled(True)
        
        if translated_data:
            self.status_bar.showMessage(f"Translation completed. Found {len(translated_data)} text regions.")
        else:
            self.status_bar.showMessage("Translation completed. No text regions detected.")
        
    def on_translation_error(self, error_message):
        """Handle translation errors."""
        self.progress_bar.setVisible(False)
        self.tl_btn.setEnabled(True)
        self.translate_toolbar_action.setEnabled(True)
        
        QMessageBox.critical(self, "Translation Error", f"Translation failed:\n{error_message}")
        self.status_bar.showMessage("Translation failed.")
        
    def on_translation_progress(self, message):
        """Update progress during translation."""
        self.status_bar.showMessage(message)
        
    def save_final_image(self):
        """Save the final translated image."""
        if not self.translated_data:
            QMessageBox.warning(self, "Warning", "No translated data to save.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Translated Image",
            "",
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )
        
        if file_path:
            try:
                final_image = self.canvas.get_final_image()
                if final_image:
                    final_image.save(file_path)
                    self.status_bar.showMessage(f"Saved: {file_path}")
                    QMessageBox.information(self, "Success", "Image saved successfully!")
                else:
                    QMessageBox.warning(self, "Warning", "Could not generate final image.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save image:\n{str(e)}")
                
    def on_selection_changed(self, selected_data):
        """Handle selection changes in the canvas."""
        if selected_data:
            # Show text editing dock
            self.text_edit_dock.show()
            self.typesetting_dock.show()
            
            # Block signals to prevent triggering on_text_edited
            self._updating_text = True
            
            # Update text editor
            self.text_edit.setText(selected_data.get('english_text', ''))
            
            # Unblock signals
            self._updating_text = False
            
            # Store the current selection index for text editing
            self._current_selection_index = selected_data.get('index', -1)
        else:
            # Hide text editing dock
            self.text_edit_dock.hide()
            self.typesetting_dock.hide()
            self._current_selection_index = None
            
    def on_text_edited(self):
        """Handle text editing in the text editor."""
        # Don't process if we're programmatically updating the text
        if self._updating_text:
            return
            
        if hasattr(self, '_current_selection_index') and self._current_selection_index is not None:
            # Save state for undo before making changes
            self.save_state()
            
            # Update the translation data
            new_text = self.text_edit.toPlainText()
            if 0 <= self._current_selection_index < len(self.translated_data):
                self.translated_data[self._current_selection_index]['english_text'] = new_text
                
                # Update canvas preview
                try:
                    self.canvas.update_text_preview(self._current_selection_index, new_text)
                except AttributeError:
                    pass
                
    def choose_text_color(self):
        """Choose text color for the current selection."""
        color = QColorDialog.getColor()
        if color.isValid():
            try:
                self.canvas.current_text_color = color.name()
                self.canvas.update_text_style()
            except AttributeError:
                # Canvas doesn't have set_text_color method yet
                pass
            
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Manga Translator",
            "Manga Translator GUI\n\n"
            "A tool for translating manga/comic images using OCR and AI.\n"
            "Features interactive text editing and typesetting controls.\n\n"
            "Fixed Issues:\n"
            "- Proper font loading from ../fonts directory\n"
            "- Fixed UI layout to prevent overlap\n"
            "- Proper text style update mechanism\n"
            "- Resizable bounding boxes\n\n"
            "Built with PySide6"
        )
        
    def closeEvent(self, event):
        """Handle application close."""
        # Stop any running translation worker
        if self.translation_worker and hasattr(self.translation_worker, 'isRunning') and self.translation_worker.isRunning():
            self.translation_worker.terminate()
            self.translation_worker.wait()
            
        event.accept()


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Manga Translator")
    app.setApplicationVersion("1.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()