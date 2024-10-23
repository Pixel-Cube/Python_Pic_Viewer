import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QFileDialog, QDesktopWidget, QMenu, QColorDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图片查看器")
        
        # 获取屏幕尺寸并设置窗口大小为屏幕的80%
        screen = QDesktopWidget().screenGeometry()
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)
        self.setGeometry(0, 0, width, height)
        self.center()
        
        # 设置标签用于显示图片
        self.label = QLabel("拖入图片以查看", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)
        
        self.setAcceptDrops(True)
        self.image_loaded = False
    
    def center(self):
        # 将窗口居中
        screen = QDesktopWidget().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(screen.center())
        self.move(frame.topLeft())
    
    def dragEnterEvent(self, event):
        # 处理拖入事件
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        # 处理放下事件
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                self.load_image(file_path)
    
    def load_image(self, file_path):
        # 加载并显示图片
        pixmap = QPixmap(file_path)
        self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.image_loaded = True

    def contextMenuEvent(self, event):
        # 右键菜单事件
        context_menu = QMenu(self)
        open_action = context_menu.addAction("打开文件")
        change_bg_action = context_menu.addAction("修改背景颜色")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == open_action:
            self.open_file_dialog()
        elif action == change_bg_action:
            self.change_background_color()

    def mousePressEvent(self, event):
        # 鼠标点击事件
        if event.button() == Qt.LeftButton and not self.image_loaded:
            self.open_file_dialog()

    def open_file_dialog(self):
        # 打开文件对话框
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "打开图片文件", "", "图片文件 (*.png *.xpm *.jpg *.bmp *.gif)", options=options)
        if file_path:
            self.load_image(file_path)

    def change_background_color(self):
        # 修改背景颜色
        color = QColorDialog.getColor()
        if color.isValid():
            self.label.setStyleSheet(f"background-color: {color.name()};")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())