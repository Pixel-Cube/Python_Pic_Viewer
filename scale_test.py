import tkinter as tk

class ZoomSquareApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=600, height=600, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        
        self.square = self.canvas.create_rectangle(250, 250, 350, 350, fill='blue')
        self.zoom_scale_factor = 1.3  # 缩放因子
        self.move_smooth_factor = 0.8  # 移动平滑系数
        self.zoom_smooth_factor = 0.3  # 缩放平滑系数
        self.move_delay = 20  # 移动延迟时间（毫秒）
        self.zoom_delay = 20  # 缩放延迟时间（毫秒）
        self.target_coords = None
        self.is_dragging = False  # 标志位
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-2>", self.start_drag)
        self.canvas.bind("<B2-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-2>", self.end_drag)  # 绑定鼠标释放事件

        self.drag_data = {"x": 0, "y": 0, "item": None}

    def zoom(self, event):
        mouse_x, mouse_y = event.x, event.y
        bbox = self.canvas.bbox(self.square)
        square_x1, square_y1, square_x2, square_y2 = bbox

        scale = self.zoom_scale_factor if event.delta > 0 else 1 / self.zoom_scale_factor

        new_width = (square_x2 - square_x1) * scale
        new_height = (square_y2 - square_y1) * scale

        new_x1 = mouse_x - (mouse_x - square_x1) * scale
        new_y1 = mouse_y - (mouse_y - square_y1) * scale
        new_x2 = new_x1 + new_width
        new_y2 = new_y1 + new_height

        # 如果鼠标在方块外，则将方块边缘平移至鼠标位置
        if not (square_x1 <= mouse_x <= square_x2 and square_y1 <= mouse_y <= square_y2):
            if mouse_x < square_x1:
                new_x1 = mouse_x
                new_x2 = new_x1 + new_width
            elif mouse_x > square_x2:
                new_x2 = mouse_x
                new_x1 = new_x2 - new_width
            if mouse_y < square_y1:
                new_y1 = mouse_y
                new_y2 = new_y1 + new_height
            elif mouse_y > square_y2:
                new_y2 = mouse_y
                new_y1 = new_y2 - new_height

        self.target_coords = (new_x1, new_y1, new_x2, new_y2)
        self.smooth_zoom()

    def smooth_zoom(self):
        if self.target_coords:
            current_coords = self.canvas.coords(self.square)
            new_coords = [
                current_coords[i] + (self.target_coords[i] - current_coords[i]) * self.zoom_smooth_factor
                for i in range(4)
            ]
            self.canvas.coords(self.square, *new_coords)
            if all(abs(new_coords[i] - self.target_coords[i]) < 1 for i in range(4)):
                self.canvas.coords(self.square, *self.target_coords)
                self.target_coords = None
            else:
                self.root.after(self.zoom_delay, self.smooth_zoom)

    def start_drag(self, event):
        self.is_dragging = True
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

        # 如果鼠标在方块外，则将方块边缘平移至鼠标位置
        bbox = self.canvas.bbox(self.square)
        square_x1, square_y1, square_x2, square_y2 = bbox
        mouse_x, mouse_y = event.x, event.y

        new_x1, new_y1, new_x2, new_y2 = square_x1, square_y1, square_x2, square_y2

        if not (square_x1 <= mouse_x <= square_x2 and square_y1 <= mouse_y <= square_y2):
            if mouse_x < square_x1:
                new_x1 = mouse_x
                new_x2 = new_x1 + (square_x2 - square_x1)
            elif mouse_x > square_x2:
                new_x2 = mouse_x
                new_x1 = new_x2 - (square_x2 - square_x1)
            if mouse_y < square_y1:
                new_y1 = mouse_y
                new_y2 = new_y1 + (square_y2 - square_y1)
            elif mouse_y > square_y2:
                new_y2 = mouse_y
                new_y1 = new_y2 - (square_y2 - square_y1)

            self.canvas.coords(self.square, new_x1, new_y1, new_x2, new_y2)

    def drag(self, event):
        if self.is_dragging:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.square, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def end_drag(self, event):
        self.is_dragging = False

if __name__ == "__main__":
    root = tk.Tk()
    app = ZoomSquareApp(root)
    root.mainloop()