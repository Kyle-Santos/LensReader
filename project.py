from PIL import Image
from PyQt6 import QtGui
from PyQt6.QtCore import QCoreApplication, QEvent, QObject, Qt
from PyQt6.QtGui import QImage, QPixmap, QPixmap, QPainter
from PyQt6.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QMainWindow, QPushButton, QTextEdit, QVBoxLayout,
                             QWidget)
from pytesseract import image_to_string


class ImageProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Processor")

        self.file_path = None
        self.image = None
        self.photo = None  # Keep a reference to the PhotoImage object

        # GUI Components
        self.label = QLabel("Image Processing Snippet:", self)
        self.label.move(10, 10)

        self.text_area = QTextEdit(self)
        self.text_area.setGeometry(10, 40, 400, 100)
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("background-color: white; color: black;")

        self.browse_button = QPushButton("Browse Image", self)
        self.browse_button.setGeometry(10, 150, 120, 30)
        self.browse_button.clicked.connect(self.browse_image)

        self.process_button = QPushButton("Process Image", self)
        self.process_button.setGeometry(150, 150, 120, 30)
        self.process_button.clicked.connect(self.process_image)

        self.screenshot_button = QPushButton("Take Screenshot", self)
        self.screenshot_button.setGeometry(290, 150, 120, 30)
        self.screenshot_button.clicked.connect(self.start_screenshot)

        self.screenshot_button = QPushButton("Load Screenshot", self)
        self.screenshot_button.setGeometry(150, 180, 120, 30)
        self.screenshot_button.clicked.connect(self.load_screenshot)

        self.image_label = QLabel(self)
        self.image_label.setGeometry(10, 200, 400, 200)

        # Create an instance of the ScreenshotTool
        self.screenshot_tool = self.ScreenshotTool()


    def browse_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", "Images (*.png *.jpg *.bmp)")
        if file_path:
            self.file_path = file_path
            self.image = QPixmap(file_path)
            self.display_image()

    def display_image(self):
        self.image_label.setPixmap(resize_image(self.image, 400))

    def process_image(self):
        qimage = self.image.toImage()
        grayscale_image = convert_grayscale(qimage)

        smoothed_image = noise_reduction(grayscale_image)

        # Convert QImage to PIL Image
        pil_image = Image.fromqpixmap(smoothed_image)

        # config
        config = (
            '--psm 6 '
            '--oem 3 '
        )

        # Use Tesseract OCR to extract text from the image
        text_content = image_to_string(pil_image, config=config)
        self.text_area.setPlainText(text_content)

    def start_screenshot(self):
        self.screenshot_tool.show()
        self.screenshot_tool.button_window.show()

    def load_screenshot(self):
        self.image = self.screenshot_tool.getImage()
        self.display_image()


    class ScreenshotTool(QMainWindow):
        def __init__(self) -> None:
            super().__init__()

            # Class Instance Variables.
            self.mouse_relative_position_x = 0
            self.mouse_relative_position_y = 0
            self.button_window_height = 50
            self.region_x_pos = 0
            self.region_y_pos = 0
            self.region_width = 0
            self.region_height = 0
            self.image = None

            # Set the flags and attributes for this window.
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

            # Create an instance of the ButtonWindow
            self.button_window = self.ButtonWindow()
            #self.button_window.setParent(self)

            # Create an instance of the class ButtonWindow.
            # self.button_window = ButtonWindow()

            # When the button close is clicked, then close this window.
            self.button_window.button_close.clicked.connect(self.closeTool)

            # When the button save is clicked, then call method get_screen_region.
            self.button_window.button_capture.clicked.connect(self.getScreenshot)

            # Used to save the mouse different states, e.g. 0 is when the mouse left button is released.
            # "1" is when the mouse left button is pressed, and the window position is:
            # pos.x() > self.width() - 5 and pos.y() > self.height() - 5
            self.mouse_mode = 0

            # Create the stylesheet to make the window transparent.
            # If we want the property to apply only to one specific Widget , we can give it a name
            # using setObjectName() and use an ID Selector to refer to it.
            widget_stylesheet = "QWidget#central_widget {" \
                                "border-color: rgba(255, 0, 0, 255);" \
                                "border-left-color: rgba(255, 0, 0, 255);" \
                                "border-right-color: rgba(255, 0, 0, 255);" \
                                "border-bottom-color: rgba(255, 0, 0, 255);" \
                                "border-style: dashed;" \
                                "border-top-width: 4px;" \
                                "border-left-width: 4px;" \
                                "border-right-width: 4px;" \
                                "border-bottom-width: 4px;" \
                                "border-radius: 4px;" \
                                "background-color: rgba(255, 255, 255, 50);" \
                                "}"

            # Create the central widget.
            self.central_widget = QWidget(self)
            self.central_widget.setStyleSheet(widget_stylesheet)
            self.central_widget.setMouseTracking(True)
            self.central_widget.installEventFilter(self)
            self.central_widget.setObjectName("central_widget")

            # Set the central widget for the main window.
            self.setCentralWidget(self.central_widget)

            # Define the initial geometry for the window.
            screen_width = QApplication.primaryScreen().size().width()
            screen_height = QApplication.primaryScreen().size().height()
            self.setGeometry(int(screen_width / 2) - int(self.geometry().width() / 2),  # x position
                            int(screen_height / 2) - int(self.geometry().height() / 2),  # y position
                            400,  # width
                            300)  # height

            # set windows minimum size.
            self.setMinimumSize(300, 100)

        def closeTool(self):
            self.button_window.hide()
            self.hide()

        def getScreenshot(self):
            # Save a copy of the selected region X, Y, Width and Height.
            self.region_x_pos = self.x()
            self.region_y_pos = self.y()
            self.region_width = self.width()
            self.region_height = self.height()

            # Get a screenshot of the region area selected by the user.
            # Capture the screen region using QPixmap
            screen = QtGui.QGuiApplication.primaryScreen()

            screenshot = screen.grabWindow(0, self.region_x_pos, self.region_y_pos, 
                                            self.region_width, self.region_height)


            # Trim the screenshot to remove the border
            # Set the image to screenshot 
            self.image = screenshot.copy(10, 10, screenshot.width() - 20, screenshot.height() - 20)

            self.button_window.hide()
            self.hide()

        def getImage(self):
            return self.image

        # Overwrite the method mousePressEvent for class QMainWindow.
        def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
            if event.button() == Qt.MouseButton.LeftButton:
                # Get the cursor position relative to the widget that receives the mouse event.
                self.mouse_relative_position_x = event.pos().x()
                self.mouse_relative_position_y = event.pos().y()
                # The mouse event is handled by this widget.
                event.accept()
            else:
                # The mouse event is not handle by this widget.
                event.ignore()

        # Overwrite the method mouseReleaseEvent for class QMainWindow.
        def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
            if event.button() == Qt.MouseButton.LeftButton:
                # Change the mouse cursor to be the standard arrow cursor.
                QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
                # Set mouse mode to 0, meaning that none of the buttons are pressed.
                self.mouse_mode = 0
                # The mouse event is handled by this widget.
                event.accept()
            else:
                # The mouse event is not handle by this widget.
                event.ignore()

        # Override the method resizeEvent for class MainWindow.
        def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
            """
            This method will be called every time the main window is resized.
            It is used to resize the button window to match the width of the
            main window.
            :param event: Resize event object.
            :return: Nothing.
            """
            # Set geometry for the button window whenever the main window change its size.
            self.button_window.setGeometry(self.x(),  # x position
                                        self.y() + self.height(),  # y position
                                        self.width(),  # width
                                        self.button_window_height)  # height
            # Pass the event to the main window.
            QMainWindow.resizeEvent(self, event)

        # Override method eventFilter for class MainWindow.
        def eventFilter(self, watched: QObject, event: QEvent) -> bool:

            # If the mouse moved.
            if event.type() == QEvent.Type.MouseMove:
                # Get mouse relative position respect the window.
                pos = event.pos()

                # Ensure buttons are visible
                self.button_window.button_capture.setVisible(True)
                self.button_window.button_close.setVisible(True)

                # To bring the button window to the front.
                self.button_window.show()
                # self.button_window.activateWindow()
                QApplication.setActiveWindow(self.button_window)
                self.button_window.raise_()

                # If none of buttons were pressed, then change the mouse cursor
                # when the mouse reach the edge of the window to let the user know
                # that the window can be resized.
                if event.buttons() == Qt.MouseButton.NoButton:
                    # Change the mouse cursor when pointer reach the bottom-right corner.
                    if pos.x() > self.width() - 5 and pos.y() > self.height() - 5:
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)
                    # Change the mouse cursor when pointer reach the top-left corner.
                    elif pos.x() < 5 and pos.y() < 5:
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)
                    # Change the mouse cursor when pointer reach the top-right corner.
                    elif pos.x() > self.width() - 5 and pos.y() < 5:
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeBDiagCursor)
                    # Change the mouse cursor when pointer reach the bottom-left corner.
                    elif pos.x() < 5 and pos.y() > self.height() - 5:
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeBDiagCursor)
                    # Change the mouse cursor when pointer reach the left and right border.
                    elif pos.x() > self.width() - 5 or pos.x() < 5:
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeHorCursor)
                    # Change the mouse cursor when pointer reach the top and bottom border.
                    elif pos.y() > self.height() - 5 or pos.y() < 5:
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeVerCursor)
                    # Change the mouse cursor to the standard arrow cursor.
                    else:
                        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

                # If the left button was pressed, then change the mouse cursor
                # when it reaches the edge of the window and also adjust the geometry
                # of the window.
                if event.buttons() & Qt.MouseButton.LeftButton:

                    # When the mouse is in the bottom-right corner.
                    # If the X mouse position is greater than the window width - 10,
                    # and if the Y mouse position is greater than the window height - 10,
                    # then adjust window geometry.
                    if pos.x() > self.width() - 10 and pos.y() > self.height() - 10 \
                            and (self.mouse_mode == 0 or self.mouse_mode == 1):
                        self.mouse_mode = 1
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)
                        self.setGeometry(self.x(), self.y(), pos.x(), pos.y())

                    # When the mouse is in the top-left corner.
                    # If the X mouse position is less than 10,
                    # and if the Y mouse position is less than 10,
                    # then adjust window geometry.
                    elif pos.x() < 10 and pos.y() < 10 \
                            and (self.mouse_mode == 0 or self.mouse_mode == 2):
                        self.mouse_mode = 2
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeFDiagCursor)
                        self.setGeometry(self.x() + pos.x(), self.y() + pos.y(),
                                        self.width() - pos.x(), self.height() - pos.y())

                    # When the mouse is in the top-right corner.
                    # If the X mouse position is greater than the window width - 10,
                    # and if the Y mouse position is less than 10,
                    # then adjust window geometry.
                    elif pos.x() > self.width() - 10 and pos.y() < 10 \
                            and (self.mouse_mode == 0 or self.mouse_mode == 3):
                        self.mouse_mode = 3
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeBDiagCursor)
                        self.setGeometry(self.x(), self.y() + pos.y(),
                                        pos.x(), self.height() - pos.y())

                    # When the mouse is in the bottom-left corner.
                    # If the X mouse position is less than 10,
                    # and if the Y mouse position is greater than height - 10,
                    # then adjust window geometry.
                    elif pos.x() < 10 and pos.y() > self.height() - 10 \
                            and (self.mouse_mode == 0 or self.mouse_mode == 4):
                        self.mouse_mode = 4
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeBDiagCursor)
                        self.setGeometry(self.x() + pos.x(), self.y(),
                                        self.width() - pos.x(), pos.y())

                    # When the mouse is on the window right border.
                    # If the X mouse position is greater than the window width - 5,
                    # then adjust window geometry.
                    elif pos.x() > self.width() - 5 and 0 < pos.y() < self.height() \
                            and (self.mouse_mode == 0 or self.mouse_mode == 5):
                        self.mouse_mode = 5
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeHorCursor)
                        self.setGeometry(self.x(), self.y(), pos.x(), self.height())

                    # When the mouse is on the window left border.
                    # If the X mouse position is less than 5,
                    # then adjust window geometry.
                    elif pos.x() < 5 and 0 < pos.y() < self.height() \
                            and (self.mouse_mode == 0 or self.mouse_mode == 6):
                        self.mouse_mode = 6
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeHorCursor)
                        if self.width() - pos.x() > self.minimumWidth():
                            self.setGeometry(self.x() + pos.x(), self.y(), self.width() - pos.x(), self.height())

                    # When the mouse is on the window bottom border.
                    # If the Y mouse position is greater than the window height,
                    # then adjust window geometry.
                    elif pos.y() > self.height() - 5 and 0 < pos.x() < self.width() \
                            and (self.mouse_mode == 0 or self.mouse_mode == 7):
                        self.mouse_mode = 7
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeVerCursor)
                        self.setGeometry(self.x(), self.y(), self.width(), pos.y())

                    # When the mouse is on the window top border.
                    # If the Y mouse position is less than 5,
                    # then adjust window geometry.
                    elif pos.y() < 5 and 0 < pos.x() < self.width() \
                            and (self.mouse_mode == 0 or self.mouse_mode == 8):
                        self.mouse_mode = 8
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeVerCursor)
                        if self.height() - pos.y() > self.minimumHeight():
                            self.setGeometry(self.x(), self.y() + pos.y(), self.width(), self.height() - pos.y())

                    # If the X mouse position is greater than 10 and less than window width
                    # and the Y mouse position is greater than 10 and less than window height.
                    # Then move window to a new position.
                    elif 10 < pos.x() < self.width() - 10 and 10 < pos.y() < self.height() - 10 \
                            and (self.mouse_mode == 0 or self.mouse_mode == 9):
                        self.mouse_mode = 9
                        # Change the mouse cursor to cursor used for elements that are used to
                        # resize top-level windows in any direction.
                        QApplication.setOverrideCursor(Qt.CursorShape.SizeAllCursor)
                        # Move the widget when the mouse is dragged.
                        self.move(int(event.globalPosition().x()) - self.mouse_relative_position_x,
                                int(event.globalPosition().y()) - self.mouse_relative_position_y)
                        # Set geometry for the button_window.
                        self.button_window.setGeometry(self.x(),  # x position
                                                    self.y() + self.height(),  # y position
                                                    self.width(),  # width
                                                    self.button_window_height)  # height
                    else:
                        # Change the mouse cursor to be the standard arrow cursor.
                        QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)

            elif event.type() == QEvent.Type.Show:
                # Set geometry for the button_window.
                self.button_window.setGeometry(self.x(),  # x position
                                            self.y() + self.height(),  # y position
                                            self.width(),  # width
                                            self.button_window_height)  # height
                # Show the window.
                self.button_window.show()

            else:
                # return super(MainWindow, self).eventFilter(watched, event)
                return False

            # This function does not cause an immediate repaint; instead it schedules a paint
            # event for processing when Qt returns to the main event loop. This permits Qt to
            # optimize for more speed and less flicker than a call to repaint() does.
            self.central_widget.update()
            # Processes all pending events for the calling thread according to the specified
            # flags until there are no more events to process.
            QCoreApplication.processEvents()

            return True


        class ButtonWindow(QWidget):
            def __init__(self) -> None:
                super().__init__()

                # Set the flags and attributes for this window.
                self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
                self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

                # Create the stylesheet to make the window transparent.
                widget_stylesheet = "QWidget#button_window {" \
                                    "background-color: rgba(255, 255, 255, 100);" \
                                    "}"

                button_stylesheet = "QPushButton {" \
                                    "color: rgb(255, 255, 255);" \
                                    "font: 75 10pt FreeSans;" \
                                    "background-color: rgba(6, 104, 249, 255);" \
                                    "border-top-color: rgba(151, 222, 247, 255);" \
                                    "border-left-color: rgba(151, 222, 247, 255);" \
                                    "border-right-color: rgba(4, 57, 135, 255);" \
                                    "border-bottom-color: rgba(4, 57, 135,255);" \
                                    "border-style: inset;" \
                                    "border-top-width: 2px;" \
                                    "border-left-width: 2px;" \
                                    "border-right-width: 3px;" \
                                    "border-bottom-width: 3px;" \
                                    "border-radius: 5px;" \
                                    "}"

                # Create a button to capture the screen.
                self.button_capture = QPushButton("Capture")
                self.button_capture.setFixedSize(85, 30)
                # self.button_capture.setMouseTracking(True)
                # self.button_capture.installEventFilter(self)
                self.button_capture.setStyleSheet(button_stylesheet)

                # Create a button to close the application.
                self.button_close = QPushButton("Close")
                self.button_close.setFixedSize(85, 30)
                # self.button_close.setMouseTracking(True)
                # self.button_close.installEventFilter(self)
                self.button_close.setStyleSheet(button_stylesheet)

                # Create a horizontal layout with the buttons.
                horizontal_layout = QHBoxLayout()
                horizontal_layout.addStretch(1)
                horizontal_layout.addWidget(self.button_capture)
                horizontal_layout.addStretch(1)
                horizontal_layout.addWidget(self.button_close)
                horizontal_layout.addStretch(1)

                # Create a vertical layout with the horizontal layout.
                vert_layout = QVBoxLayout()
                vert_layout.addStretch(1)
                vert_layout.addLayout(horizontal_layout)
                vert_layout.addStretch(1)

                # Set the widget layout.
                self.setLayout(vert_layout)
                self.setStyleSheet(widget_stylesheet)
                self.setObjectName("button_window")

            # Override method eventFilter for class QWidget.
            def eventFilter(self, watched: QObject, event: QEvent) -> bool:
                # If the mouse moved.
                if event.type() == QEvent.Type.MouseMove:
                    QApplication.setOverrideCursor(Qt.ArrowCursor)
                    return True
                else:
                    return False

def noise_reduction(image):
    # Create a QImage for storing the smoothed image
    smoothed_image = QImage(image.size(), QImage.Format.Format_ARGB32)
    smoothed_image.fill(0)  # Fill with transparent background

    # Create a QPainter to perform drawing operations
    painter = QPainter()
    painter.begin(smoothed_image)
    
    # Set rendering hints for smoothing
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)

    # Draw the input image onto the smoothed image
    painter.drawImage(smoothed_image.rect(), image)

    # End painting
    painter.end()

    return smoothed_image

def resize_image(image, desired_size):
    return image.scaledToWidth(desired_size)

def convert_grayscale(image):
    grayscale_image = image.convertToFormat(QImage.Format.Format_Grayscale8)

    return grayscale_image

def main():
    app = QApplication([])
    window = ImageProcessorApp()
    window.setGeometry(100, 100, 420, 370)
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
