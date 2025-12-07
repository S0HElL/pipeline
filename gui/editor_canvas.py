"""
Manga Translator GUI - Editor Canvas
Interactive image display and text editing canvas with properly working resizeable bounding boxes.
"""

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsPixmapItem, QWidget, QVBoxLayout,
    QGraphicsItem, QGraphicsPathItem
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QBrush, QColor, QFont,
    QPolygonF, QPainterPath
)
from PIL import Image


class ResizeHandle(QGraphicsRectItem):
    """Resize handle for bounding boxes."""
    
    def __init__(self, rect, parent=None):
        super().__init__(rect, parent)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setPen(QPen(QColor(255, 255, 255), 1))
        self.setBrush(QBrush(QColor(0, 0, 0)))
        self.setCursor(Qt.ArrowCursor)
        
        # NEW: Make handles interactable
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
    def paint(self, painter, option, widget=None):
        """Custom paint for the resize handle."""
        painter.setPen(self.pen())
        painter.setBrush(self.brush())
        painter.drawRect(self.rect())
    
    def mousePressEvent(self, event):
        """Handle mouse press - don't propagate to parent."""
        if event.button() == Qt.LeftButton:
            # The view will handle this
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move - don't propagate to parent."""
        event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release - don't propagate to parent."""
        event.accept()

class BoundingBoxItem(QGraphicsRectItem):
    """
    Resizable bounding box for text regions.
    Supports selection, movement, and resizing with handles and borders.
    """
    
    def __init__(self, rect, data, parent=None):
        super().__init__(rect, parent)
        self.data = data
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Visual properties
        self.default_pen = QPen(QColor(0, 255, 0), 2)
        self.selected_pen = QPen(QColor(255, 255, 0), 3)
        self.hover_pen = QPen(QColor(0, 255, 255), 2)
        
        self.setPen(self.default_pen)
        self.setBrush(QBrush(Qt.NoBrush))
        
        # Text alignment storage
        self.text_alignment = "Center"
        
        # Resize handles
        self.handles = []
        self.create_resize_handles()
        
        # Text preview
        self.text_item = None
        self.create_text_preview()
        
    def create_resize_handles(self):
        """Create resize handles for the bounding box."""
        handle_size = QRectF(0, 0, 20, 20)
        half_size = 10
        
        rect = self.rect()

        
        # CRITICAL FIX: Calculate positions relative to rect's TOP-LEFT corner
        # Since the rect might have non-zero x,y, we need to account for that
        local_positions = [
            QPointF(rect.x() - half_size, rect.y() - half_size),                    # Top-left
            QPointF(rect.x() + rect.width() - half_size, rect.y() - half_size),      # Top-right
            QPointF(rect.x() - half_size, rect.y() + rect.height() - half_size),     # Bottom-left
            QPointF(rect.x() + rect.width() - half_size, rect.y() + rect.height() - half_size),  # Bottom-right
            QPointF(rect.x() - half_size, rect.y() + rect.height() / 2 - half_size),             # Middle-left
            QPointF(rect.x() + rect.width() - half_size, rect.y() + rect.height() / 2 - half_size), # Middle-right
            QPointF(rect.x() + rect.width() / 2 - half_size, rect.y() - half_size),              # Top-middle
            QPointF(rect.x() + rect.width() / 2 - half_size, rect.y() + rect.height() - half_size), # Bottom-middle
        ]
        
        for i, local_pos in enumerate(local_positions):
            handle = ResizeHandle(handle_size, self)
            handle.setParentItem(self)
            handle.setPos(local_pos)
            handle.hide()

            
            scene_pos = handle.mapToScene(QPointF(0, 0))

            
            handle.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
            self.handles.append(handle)
            
    def create_text_preview(self):
        """Create text preview item for the bounding box."""
        self.text_item = QGraphicsTextItem(self.data.get('english_text', ''), self)
        self.text_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.text_item.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.text_item.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
        
        # Set text properties
        font = QFont("Arial", 12)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        
        # Position text in center of bounding box
        self.update_text_position()
        
    def update_text_position(self):
        """Update the position of the text preview."""
        if self.text_item and self.rect().isValid():
            rect = self.rect()
            text_rect = self.text_item.boundingRect()
            
            # Get alignment (default to Center if not set)
            alignment = getattr(self, 'text_alignment', 'Center')
            
            # Calculate X position based on alignment
            if alignment == "Left":
                x = rect.x() + 5  # Small padding
            elif alignment == "Right":
                x = rect.x() + rect.width() - text_rect.width() - 5
            else:  # Center (default)
                x = rect.x() + (rect.width() - text_rect.width()) / 2
            
            # Center vertically
            y = rect.y() + (rect.height() - text_rect.height()) / 2
            
            self.text_item.setPos(x, y)
            
    def update_text_content(self, text):
        """Update the text content of the preview."""
        if self.text_item:
            self.text_item.setPlainText(text)
            self.update_text_position()
            
    def update_text_style(self, font_family=None, font_size=None, alignment=None, color=None):
        """Update the text styling."""
        if self.text_item:
            font = self.text_item.font()  # Get current font first
            if font_family:
                font.setFamily(font_family)
            if font_size:
                font.setPointSize(font_size)
            self.text_item.setFont(font)
            
            if color:
                self.text_item.setDefaultTextColor(QColor(color))
                
            # Store alignment for later use in positioning
            if alignment:
                self.text_alignment = alignment
                
            self.update_text_position()
            
    def setSelected(self, selected):
        """Override setSelected to show/hide resize handles."""
        super().setSelected(selected)
        
        # Show/hide resize handles
        for handle in self.handles:
            if selected:
                handle.show()
            else:
                handle.hide()
                
    def itemChange(self, change, value):
        """Handle item changes (movement, selection, etc.)."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.setPen(self.selected_pen)
            else:
                self.setPen(self.default_pen)
                
        elif change == QGraphicsItem.ItemPositionChange:
            # Update text position when moved
            self.update_text_position()
            self.update_handle_positions()
            
        elif change == QGraphicsItem.ItemParentChange:
            # Reset handle positions when parent changes
            self.update_handle_positions()
            
        return super().itemChange(change, value)
        
    def update_handle_positions(self):
        """Update the positions of resize handles."""
        if len(self.handles) >= 8:
            rect = self.rect()
            half_size = 10
            

            
            # CRITICAL FIX: Use rect's actual x,y coordinates
            local_positions = [
                QPointF(rect.x() - half_size, rect.y() - half_size),                    # Top-left
                QPointF(rect.x() + rect.width() - half_size, rect.y() - half_size),      # Top-right
                QPointF(rect.x() - half_size, rect.y() + rect.height() - half_size),     # Bottom-left
                QPointF(rect.x() + rect.width() - half_size, rect.y() + rect.height() - half_size),  # Bottom-right
                QPointF(rect.x() - half_size, rect.y() + rect.height() / 2 - half_size),             # Middle-left
                QPointF(rect.x() + rect.width() - half_size, rect.y() + rect.height() / 2 - half_size), # Middle-right
                QPointF(rect.x() + rect.width() / 2 - half_size, rect.y() - half_size),              # Top-middle
                QPointF(rect.x() + rect.width() / 2 - half_size, rect.y() + rect.height() - half_size), # Bottom-middle
            ]
            
            for i, handle in enumerate(self.handles):
                if i < len(local_positions):
                    handle.setPos(local_positions[i])

                    scene_pos = handle.mapToScene(QPointF(0, 0))

                    handle.setRect(QRectF(0, 0, 20, 20))
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
        super().mousePressEvent(event)
        
    def hoverEnterEvent(self, event):
        """Handle hover enter events."""
        if not self.isSelected():
            self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave events."""
        if not self.isSelected():
            self.setPen(self.default_pen)
        super().hoverLeaveEvent(event)
        
    def resize_by_handle(self, handle, new_pos):
        """Resize the bounding box using a handle with proper coordinate handling."""
        mouse_scene_pos = new_pos
        mouse_local_pos = self.mapFromScene(mouse_scene_pos)
        
        rect = self.rect()
        new_rect = QRectF(rect)
        
        # Determine which handle was moved based on its ORIGINAL position
        handle_local_pos = handle.pos()
        half_size = 10
        
        # Use rect coordinates to identify corners
        tol = 2  # Tolerance for comparison
        
        # Top-left handle
        if abs(handle_local_pos.x() - (rect.x() - half_size)) < tol and abs(handle_local_pos.y() - (rect.y() - half_size)) < tol:
            new_rect.setTopLeft(mouse_local_pos)
        # Top-right handle
        elif abs(handle_local_pos.x() - (rect.x() + rect.width() - half_size)) < tol and abs(handle_local_pos.y() - (rect.y() - half_size)) < tol:
            new_rect.setTopRight(mouse_local_pos)
        # Bottom-left handle
        elif abs(handle_local_pos.x() - (rect.x() - half_size)) < tol and abs(handle_local_pos.y() - (rect.y() + rect.height() - half_size)) < tol:
            new_rect.setBottomLeft(mouse_local_pos)
        # Bottom-right handle
        elif abs(handle_local_pos.x() - (rect.x() + rect.width() - half_size)) < tol and abs(handle_local_pos.y() - (rect.y() + rect.height() - half_size)) < tol:
            new_rect.setBottomRight(mouse_local_pos)
        # Middle-left handle
        elif abs(handle_local_pos.x() - (rect.x() - half_size)) < tol:
            new_rect.setLeft(mouse_local_pos.x())
        # Middle-right handle
        elif abs(handle_local_pos.x() - (rect.x() + rect.width() - half_size)) < tol:
            new_rect.setRight(mouse_local_pos.x())
        # Top-middle handle
        elif abs(handle_local_pos.y() - (rect.y() - half_size)) < tol:
            new_rect.setTop(mouse_local_pos.y())
        # Bottom-middle handle
        elif abs(handle_local_pos.y() - (rect.y() + rect.height() - half_size)) < tol:
            new_rect.setBottom(mouse_local_pos.y())
        else:

            return
            
        # Ensure minimum size
        if new_rect.width() > 20 and new_rect.height() > 20:
            normalized_rect = new_rect.normalized()

            self.setRect(normalized_rect)
            self.update_text_position()
            self.update_handle_positions()
        else:
            print("DEBUG: Resize blocked: Min size not met.")

            
    def resize_from_border(self, edge, mouse_pos):
        """Resize from a border edge."""
        rect = self.rect()
        mouse_local = self.mapFromScene(mouse_pos)
        new_rect = QRectF(rect)
        
        # Border resize is typically more sensitive to snapping, but let's apply the logic from fixed
        if edge == 'top':
            new_rect.setTop(mouse_local.y())
        elif edge == 'bottom':
            new_rect.setBottom(mouse_local.y())
        elif edge == 'left':
            new_rect.setLeft(mouse_local.x())
        elif edge == 'right':
            new_rect.setRight(mouse_local.x())
        elif edge == 'top-left':
            new_rect.setTopLeft(mouse_local)
        elif edge == 'top-right':
            new_rect.setTopRight(mouse_local)
        elif edge == 'bottom-left':
            new_rect.setBottomLeft(mouse_local)
        elif edge == 'bottom-right':
            new_rect.setBottomRight(mouse_local)
            
        # Ensure minimum size
        if new_rect.width() > 20 and new_rect.height() > 20:
            normalized_rect = new_rect.normalized()
            self.setRect(normalized_rect)
            self.update_text_position()
            self.update_handle_positions()


class EditorCanvas(QGraphicsView):
    """
    Fixed main canvas for image display and text editing with working resize functionality.
    """
    
    # Signals
    selection_changed = Signal(object)  # Emits selected bounding box data
    color_picked = Signal(object)  # Emits picked color
    
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Image properties
        self.original_pixmap = None
        self.current_pixmap = None
        self.image_rect = QRectF()
        
        # Bounding boxes
        self.bounding_boxes = []
        self.selected_box_index = -1
        
        # View settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Text style settings
        self.current_font_family = "Arial"
        self.current_font_size = 20
        self.current_alignment = "Center"
        self.current_text_color = "#000000"
        
        # Resizing state
        self.resizing = False
        self.active_handle = None
        self.resize_edge = None
        
        # Eye dropper state
        self.eyedropper_active = False
        
        self.setup_view()
      

        
    def setup_view(self):
        """Setup the view properties."""
        # Enable antialiasing
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Set scene rect large enough to accommodate images
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        # Set viewport update mode
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        
        # Background settings
        self.setBackgroundBrush(QBrush(Qt.lightGray))
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        
    def zoom_in(self):
        """Zoom in the view."""
        factor = 1.2
        self.zoom_factor *= factor
        self.zoom_factor = min(self.max_zoom, self.zoom_factor)
        self.scale(factor, factor)
    
    def zoom_out(self):
        """Zoom out the view."""
        factor = 1.2
        self.zoom_factor /= factor
        self.zoom_factor = max(self.min_zoom, self.zoom_factor)
        self.scale(1/factor, 1/factor)
        
    def pick_color_at_position(self, scene_pos):
        """Pick color from the image at the given scene position."""
        if not self.current_pixmap:
            return
            
        # Convert scene position to image coordinates
        x = int(scene_pos.x())
        y = int(scene_pos.y())
        
        # Check if position is within image bounds
        if 0 <= x < self.current_pixmap.width() and 0 <= y < self.current_pixmap.height():
            # Get the color at the position
            image = self.current_pixmap.toImage()
            color = QColor(image.pixel(x, y))
            
            # Emit the picked color
            self.color_picked.emit(color)
        else:
            print("DEBUG: Eye dropper click outside image bounds")
    
    def reset_zoom(self):
        """Reset zoom to fit image."""
        self.fit_to_image()
    def load_image(self, image_path):
        """Load an image from file path."""
        try:
            # Load image using PIL first
            pil_image = Image.open(image_path)
            pil_image = pil_image.convert("RGB")
            
            # Convert to QImage
            qimage = QImage(
                pil_image.tobytes(), 
                pil_image.width, 
                pil_image.height, 
                pil_image.width * 3, 
                QImage.Format_RGB888
            )
            
            # Convert to QPixmap
            self.original_pixmap = QPixmap.fromImage(qimage)
            self.current_pixmap = QPixmap(self.original_pixmap)
            
            # Clear previous content
            self.scene.clear()
            self.bounding_boxes.clear()
            self.selected_box_index = -1
            
            # Add image to scene
            self.scene.addPixmap(self.current_pixmap)
            
            # Store image rect for boundary checking
            self.image_rect = QRectF(0, 0, self.current_pixmap.width(), self.current_pixmap.height())
            
            # Fit image in view
            self.fit_to_image()
            
            # Clear selection
            self.selection_changed.emit(None)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            
    def fit_to_image(self):
        """Fit the image to the current view."""
        if self.current_pixmap:
            self.fitInView(self.image_rect, Qt.KeepAspectRatio)
            self.zoom_factor = 1.0
            
    def set_inpainted_image(self, pil_image):
        """Set the inpainted image after translation."""
        try:
            # Convert PIL image to QPixmap
            qimage = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format_RGB888
            )
            self.current_pixmap = QPixmap.fromImage(qimage)
            
            # Update scene
            items = self.scene.items()
            for item in items:
                if isinstance(item, QGraphicsPixmapItem):
                    self.scene.removeItem(item)
                    
            self.scene.addPixmap(self.current_pixmap)
            
        except Exception as e:
            print(f"Error setting inpainted image: {e}")
            
    def set_translation_data(self, translated_data_list):
        """Set the translation data and create bounding boxes."""
        self.translated_data = translated_data_list
        self.create_bounding_boxes()
        
    def create_bounding_boxes(self):
        """Create interactive bounding boxes for translated text."""
        if not hasattr(self, 'translated_data'):
            return
            
        for i, data in enumerate(self.translated_data):
            group_box = data['group_box']
            # group_box is a tuple of (x1, y1, x2, y2)
            x1, y1, x2, y2 = group_box
            rect = QRectF(x1, y1, x2 - x1, y2 - y1)
            
            # Use the new BoundingBoxItem (which is the fixed ResizableBoundingBoxItem)
            box_item = BoundingBoxItem(rect, data)
            self.scene.addItem(box_item)
            self.bounding_boxes.append(box_item)
            
            # CRITICAL: Update handle positions AFTER the box is added to the scene
            # This ensures coordinate transformations work correctly
            box_item.update_handle_positions()
            
    def get_edge_at_position(self, box_item, scene_pos):
        """Determine which edge of the box is at the given scene position."""
        local_pos = box_item.mapFromScene(scene_pos)
        rect = box_item.rect()
        
        # Check if position is on the border
        tolerance = 8  # pixels
        
        on_top = abs(local_pos.y() - rect.top()) < tolerance
        on_bottom = abs(local_pos.y() - rect.bottom()) < tolerance
        on_left = abs(local_pos.x() - rect.left()) < tolerance
        on_right = abs(local_pos.x() - rect.right()) < tolerance
        
        # Determine which edge(s)
        if on_top and on_left:
            return 'top-left'
        elif on_top and on_right:
            return 'top-right'
        elif on_bottom and on_left:
            return 'bottom-left'
        elif on_bottom and on_right:
            return 'bottom-right'
        elif on_top:
            return 'top'
        elif on_bottom:
            return 'bottom'
        elif on_left:
            return 'left'
        elif on_right:
            return 'right'
        
        return None
            
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        pos = self.mapToScene(event.position().toPoint())
        
        if event.button() == Qt.LeftButton:
            # Check for eye dropper mode
            if self.eyedropper_active:
                self.pick_color_at_position(pos)
                self.eyedropper_active = False
                self.setCursor(Qt.ArrowCursor)
                event.accept()
                return
            
            # Check if we clicked on a bounding box or a handle
            items = self.scene.items(pos, Qt.IntersectsItemShape, Qt.DescendingOrder)
            
            clicked_box = None
            clicked_handle = None
            

            
            for item in items:
                if isinstance(item, ResizeHandle):
                    clicked_handle = item
                    clicked_box = item.parentItem()
                    break  # Handle takes priority
                elif isinstance(item, BoundingBoxItem):
                    if clicked_box is None:  # Only set if we haven't found a handle
                        clicked_box = item
                    
            if clicked_box:
                self.select_bounding_box(clicked_box)
                
                if clicked_handle:
                    # Start resizing with handle
                    self.resizing = True
                    self.active_handle = clicked_box
                    self.resize_edge = clicked_handle
                    event.accept()  # Don't propagate
                    return
                else:
                    # Check if clicked on border for resize
                    edge = self.get_edge_at_position(clicked_box, pos)
                    if edge:
                        # Start border resize
                        self.resizing = True
                        self.active_handle = clicked_box
                        self.resize_edge = edge
                        event.accept()
                        return
                    else:
                        # Just selection, allow normal movement
                        self.resizing = False
                        self.active_handle = None
                        self.resize_edge = None
                        
                        super().mousePressEvent(event)
                        return
            else:
                # Deselect all
                self.deselect_all()
                
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        pos = self.mapToScene(event.position().toPoint())
        
        if self.resizing and self.active_handle:
            # Handle resizing

            if isinstance(self.resize_edge, ResizeHandle):
                # Resize using handle: self.active_handle is the BoundingBoxItem
                self.active_handle.resize_by_handle(self.resize_edge, pos)
            elif isinstance(self.active_handle, BoundingBoxItem) and self.resize_edge:
                # Resize using border
                self.active_handle.resize_from_border(self.resize_edge, pos)
        else:
            # Update cursor when hovering over resize areas
            items = self.scene.items(pos, Qt.IntersectsItemShape, Qt.DescendingOrder)
            
            # Only check for the topmost item
            top_item = items if items else None
            
            if top_item and isinstance(top_item, ResizeHandle) and isinstance(top_item.parentItem(), BoundingBoxItem):
                # We are hovering over a handle, set the correct cursor based on its position
                box_item = top_item.parentItem()
                handle_pos = top_item.pos()
                rect = box_item.rect()
                
                # Check based on handle's relative position (using the larger 16x16 / half_size=8)
                half_size = 8
                is_top = handle_pos.y() == -half_size
                is_bottom = abs(handle_pos.y() - (rect.height() - half_size)) < 1
                is_left = handle_pos.x() == -half_size
                is_right = abs(handle_pos.x() - (rect.width() - half_size)) < 1
                
                if is_top and is_left or is_bottom and is_right:
                    self.setCursor(Qt.SizeFDiagCursor) # Top-left / Bottom-right
                elif is_top and is_right or is_bottom and is_left:
                    self.setCursor(Qt.SizeBDiagCursor) # Top-right / Bottom-left
                elif is_top or is_bottom:
                    self.setCursor(Qt.SizeVerCursor) # Top-middle / Bottom-middle
                elif is_left or is_right:
                    self.setCursor(Qt.SizeHorCursor) # Middle-left / Middle-right
                return
            
            # If not hovering over a handle, check for border resize cursor
            for item in items:
                if isinstance(item, BoundingBoxItem) and item.isSelected():
                    edge = self.get_edge_at_position(item, pos)
                    if edge:
                        if edge in ['top-left', 'bottom-right']:
                            self.setCursor(Qt.SizeFDiagCursor)
                        elif edge in ['top-right', 'bottom-left']:
                            self.setCursor(Qt.SizeBDiagCursor)
                        elif edge in ['top', 'bottom']:
                            self.setCursor(Qt.SizeVerCursor)
                        elif edge in ['left', 'right']:
                            self.setCursor(Qt.SizeHorCursor)
                        return
                        
            # Default cursor if not resizing or hovering over a resize area
            self.setCursor(Qt.ArrowCursor)
            
        super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        if event.button() == Qt.LeftButton:
            self.resizing = False
            self.active_handle = None
            self.resize_edge = None
            
        super().mouseReleaseEvent(event)
        
    def select_bounding_box(self, box_item):
        """Select a bounding box and emit selection change."""
        # Deselect all others
        for box in self.bounding_boxes:
            if box != box_item:
                box.setSelected(False)
                
        # Select the target box
        box_item.setSelected(True)
        self.selected_box_index = self.bounding_boxes.index(box_item)
        
        # Emit selection changed signal
        data = {
            'index': self.selected_box_index,
            'english_text': box_item.data.get('english_text', ''),
            'japanese_text': box_item.data.get('japanese_text', ''),
            'group_box': box_item.data.get('group_box', (0, 0, 0, 0))
        }
        self.selection_changed.emit(data)
        
    def deselect_all(self):
        """Deselect all bounding boxes."""
        for box in self.bounding_boxes:
            box.setSelected(False)
            
        self.selected_box_index = -1
        self.selection_changed.emit(None)
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom with Ctrl+Wheel
            angle = event.angleDelta().y()
            factor = 1.2 if angle > 0 else 1/1.2
            
            # Get cursor position before zoom
            cursor_pos = self.mapToScene(event.position().toPoint())
            
            # Zoom
            self.zoom_factor *= factor
            self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))
            
            self.scale(1/factor if angle > 0 else factor, 1/factor if angle > 0 else factor)
            
            # Keep cursor position stable
            new_cursor_pos = self.mapToScene(event.position().toPoint())
            delta = cursor_pos - new_cursor_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + int(delta.y())
            )
            
            event.accept()
        else:
            # Normal scroll
            super().wheelEvent(event)
            
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            if self.eyedropper_active:
                # Cancel eye dropper
                self.eyedropper_active = False
                self.setCursor(Qt.ArrowCursor)
                event.accept()
            else:
                # Deselect all
                self.deselect_all()
        elif event.key() == Qt.Key_Delete and self.selected_box_index >= 0:
            # Delete selected bounding box
            self.delete_selected_box()
        else:
            super().keyPressEvent(event)
            
    def delete_selected_box(self):
        """Delete the currently selected bounding box."""
        if self.selected_box_index >= 0:
            box = self.bounding_boxes[self.selected_box_index]
            self.scene.removeItem(box)
            self.bounding_boxes.pop(self.selected_box_index)
            self.selected_box_index = -1
            self.selection_changed.emit(None)
            
    def update_text_style(self):
        """Update the text style for the selected bounding box."""
        if self.selected_box_index >= 0 and self.selected_box_index < len(self.bounding_boxes):
            box = self.bounding_boxes[self.selected_box_index]
            box.update_text_style(
                font_family=self.current_font_family,
                font_size=self.current_font_size,
                alignment=self.current_alignment,
                color=self.current_text_color
            )
            
    def update_text_preview(self, index, text):
        """Update text preview for a specific bounding box."""
        if 0 <= index < len(self.bounding_boxes):
            box = self.bounding_boxes[index]
            box.update_text_content(text)
            
    def set_text_color(self, color):
        """Set the current text color."""
        self.current_text_color = color
        self.update_text_style()
        
    def get_final_image(self):
        """Get the final rendered image with all text applied."""
        if not self.current_pixmap:
            return None
            
        # Create a copy of the current image
        final_image = self.current_pixmap.toImage()
        painter = QPainter(final_image)
        
        # Render all bounding boxes with their current text
        for box in self.bounding_boxes:
            if box.text_item:
                # Get the text and position
                text = box.text_item.toPlainText()
                font = box.text_item.font()
                color = box.text_item.defaultTextColor()
                
                # Set font and color
                painter.setFont(font)
                painter.setPen(QPen(color))
                
                # Draw text at the box's text position
                rect = box.rect()
                
                # Get alignment from the box item (not from text_item)
                alignment = getattr(box, 'text_alignment', 'Center')
                text_rect = box.text_item.boundingRect()
                
                # Handle alignment
                if alignment == "Center":
                    x = rect.x() + (rect.width() - text_rect.width()) / 2
                    y = rect.y() + (rect.height() - text_rect.height()) / 2
                elif alignment == "Left":
                    x = rect.x() + 5
                    y = rect.y() + (rect.height() - text_rect.height()) / 2
                else:  # Right alignment
                    x = rect.x() + rect.width() - text_rect.width() - 5
                    y = rect.y() + (rect.height() - text_rect.height()) / 2
                    
                # Draw text with outline for better readability
                painter.setPen(QPen(Qt.white, 2))
                painter.drawText(QPointF(x, y + font.pointSize()), text)
                painter.setPen(QPen(color))
                painter.drawText(QPointF(x, y + font.pointSize()), text)
                
        painter.end()
        
        # Convert back to PIL Image
        try:
            from PIL import ImageQt
            return ImageQt.fromqimage(final_image)
        except ImportError:
            # Fallback: return QImage if ImageQt is not available
            return final_image