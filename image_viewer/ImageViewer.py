import os
import tkinter as tk
from tkinter import filedialog, PhotoImage, colorchooser
from typing import List

import keyboard
from PIL import Image, ImageTk, ImageSequence
from tkinterdnd2 import DND_FILES, TkinterDnD

TRANSCOLOUR = '#FFFFFE'

class ImageViewer:
    def __init__(self, root):
        self.background_color = TRANSCOLOUR
        self.background_id = None
        self.root:TkinterDnD.Tk = root
        self.root.title("图片查看器")

        # 获取屏幕分辨率
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 设置窗口大小为屏幕分辨率的80%
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        self.root.geometry(f"{window_width}x{window_height}")

        # 将窗口居中
        position_right = int(screen_width/2 - window_width/2)
        position_down = int(screen_height/2 - window_height/2)
        self.root.geometry(f"+{position_right}+{position_down}")

        self.canvas = tk.Canvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.root.wm_attributes('-transparentcolor',TRANSCOLOUR)
        self.image_list:List[str] = []
        self.image_id: int|None = None
        self.image: PhotoImage|None = None
        self.current_image_index = 0
        self.animation:str|None = None # identifier
        self.frames: List[PhotoImage] = []
        self.zoom_factor = 1.0
        self.zoom_factor_before = self.zoom_factor
        self.zoom_coord = (window_width//2, window_height//2)
        self.image_coord = (window_width//2, window_height//2)
        self.is_dragging = False  # 标志位
        self.drag_data = {"x": 0, "y": 0, "item": None}
        # 使用keyboard模块绑定键盘事件
        keyboard.on_press_key("left", self.show_previous_image)
        keyboard.on_press_key("right", self.show_next_image)
        keyboard.on_press_key("t", self.sort_by_time)
        keyboard.on_press_key("n", self.sort_by_name)
        keyboard.on_press_key("s", self.sort_by_size)

        # 创建右键菜单
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="打开文件", command=self.open_file)
        self.context_menu.add_command(label="修改背景颜色", command=self.choose_color)
        self.context_menu.add_command(label="设置背景透明", command=self.choose_color_transparent)

        # 绑定鼠标点击事件
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<Button-3>", self.show_context_menu)

        # 绑定拖放事件
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.drop_file)

        # 绑定窗口大小改变事件
        self.root.bind("<Configure>", self.on_resize)

        # 绑定鼠标滚轮事件
        self.root.bind("<MouseWheel>", self.zoom_image)

        # 绑定拖放
        self.root.bind("<Button-2>", self.start_drag)
        self.root.bind("<B2-Motion>", self.drag)
        self.root.bind("<ButtonRelease-2>", self.end_drag)  # 绑定鼠标释放事件

    def load_images(self, folder_path:str, selected_file:str):
        if folder_path:
            # 获取文件列表
            self.image_list = [os.path.join(folder_path, file_name) for file_name in os.listdir(folder_path) if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.image_list.sort()  # 默认按名称排序
            # 标准化路径
            selected_file = os.path.normpath(selected_file)
            self.image_list = [os.path.normpath(file) for file in self.image_list]
            # 定位选择的图片文件的顺序值
            self.current_image_index = self.image_list.index(selected_file)

    def show_image(self, index:int):
        image_path = self.image_list[index]
        image = Image.open(image_path)

        # 停止当前动画
        if self.animation:
            self.root.after_cancel(self.animation)
            self.animation = None

        # 检查是否为GIF
        if image_path.lower().endswith('.gif'):
            self.play_gif(image)
        else:
            self.display_image(image)
        self.zoom()
        self.create_image()
        new_x1, new_y1 = self.image_coord
        self.canvas.coords(self.image_id, new_x1, new_y1)

    def create_image(self):
        if self.image_id:
            self.canvas.delete(self.image_id)  # 删除之前的图片

        x0 = (self.canvas.winfo_width()) // 2
        y0 = (self.canvas.winfo_height()) // 2

        self.image_id = self.canvas.create_image(x0,y0,image=self.image, anchor=tk.CENTER)

    def choose_color_transparent(self):
        self.background_color = TRANSCOLOUR
        self.canvas.itemconfig(self.background_id, fill=self.background_color, outline=self.background_color)

    def choose_color(self):
        # 打开调色板，并将选定的颜色存储在变量chosen_color
        chosen_color = colorchooser.askcolor()
        # 如果用户选择了颜色，则更新标签的背景颜色
        if chosen_color[0] != '':
            self.background_color = chosen_color[1]
            self.canvas.itemconfig(self.background_id,fill=self.background_color,outline=self.background_color)

    def display_image(self, image:Image):
        # 获取窗口的高度
        window_height = self.root.winfo_height()
        # 按比例调整图片大小
        aspect_ratio = image.width / image.height
        new_height = int(window_height * self.zoom_factor)
        new_width = int(new_height * aspect_ratio)
        resized_image = image.resize((new_width, new_height), Image.NEAREST)

        photo = ImageTk.PhotoImage(resized_image)
        self.image = photo

    def play_gif(self, image:Image):
        # 缓存调整后的帧
        self.frames = []
        window_height = self.root.winfo_height()
        aspect_ratio = image.width / image.height
        new_height = int(window_height * self.zoom_factor)
        new_width = int(new_height * aspect_ratio)
        for frame in ImageSequence.Iterator(image):
            resized_frame = frame.resize((new_width, new_height), Image.NEAREST)
            self.frames.append(ImageTk.PhotoImage(resized_frame))

        def update_frame(index):
            frame = self.frames[index]
            self.image = frame
            self.animation = self.root.after(100, update_frame, (index + 1) % len(self.frames))
        update_frame(0)

    def show_previous_image(self, event):
        print("Left arrow key pressed")  # 调试信息
        if self.image_list:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
            self.show_image(self.current_image_index)

    def show_next_image(self, event):
        print("Right arrow key pressed")  # 调试信息
        if self.image_list:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
            self.show_image(self.current_image_index)

    def sort_by_time(self, event):
        print("Sort by time")  # 调试信息
        current_image_path = self.image_list[self.current_image_index]
        self.image_list.sort(key=os.path.getmtime)
        self.current_image_index = self.image_list.index(current_image_path)
        self.show_image(self.current_image_index)

    def sort_by_name(self, event):
        print("Sort by name")  # 调试信息
        current_image_path = self.image_list[self.current_image_index]
        self.image_list.sort()
        self.current_image_index = self.image_list.index(current_image_path)
        self.show_image(self.current_image_index)

    def sort_by_size(self, event):
        print("Sort by size")  # 调试信息
        current_image_path = self.image_list[self.current_image_index]
        self.image_list.sort(key=os.path.getsize)
        self.current_image_index = self.image_list.index(current_image_path)
        self.show_image(self.current_image_index)

    def open_single_file(self,file_path:str):
        if file_path:
            folder_path = os.path.dirname(file_path)
            self.load_images(folder_path, file_path)
            if self.image_list:
                self.show_image(self.current_image_index)
                # 解除初始的鼠标点击事件绑定
                self.root.unbind("<Button-1>")
                self.root.unbind("<Button-3>")
                # 重新绑定鼠标点击事件用于切换图片和重新选择图片
                self.root.bind("<Button-1>", self.switch_image)
                self.root.bind("<Button-3>", self.show_context_menu)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        self.open_single_file(file_path)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def on_click(self, event):
        self.open_file()

    def switch_image(self, event):
        if self.image_list:
            if event.x < self.root.winfo_width() // 2:
                self.current_image_index = (self.current_image_index - 1) % len(self.image_list)
            else:
                self.current_image_index = (self.current_image_index + 1) % len(self.image_list)
            self.zoom_factor = 1.0  # 重置缩放比例
            self.zoom_factor_before = self.zoom_factor
            self.show_image(self.current_image_index)

    def drop_file(self, event):
        file_path = event.data.strip('{}')  # 去除路径中的花括号
        self.open_single_file(file_path)

    def on_resize(self, event):
        self.root.configure(width=event.width, height=event.height)
        self.background_id = self.canvas.create_rectangle(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height(),
                                     fill=self.background_color,
                                     outline=self.background_color)
        if self.image_list:
            self.show_image(self.current_image_index)

    def zoom_image(self, event):
        if self.image_list:
            if event.delta > 0:
                self.zoom_factor_before = self.zoom_factor
                self.zoom_factor *= 1.1
            else:
                self.zoom_factor_before = self.zoom_factor
                self.zoom_factor /= 1.1
            self.zoom_coord = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
            self.show_image(self.current_image_index)

    def zoom(self):
        if self.image_id:
            square_x1,square_y1,square_x2,square_y2  = self.canvas.bbox(self.image_id)
            center_x,center_y = (square_x1+square_x2)//2, (square_y1+square_y2)//2
            mouse_x, mouse_y = self.zoom_coord
            new_center_x = center_x + (center_x - mouse_x)*(self.zoom_factor-self.zoom_factor_before)
            new_center_y = center_y + (center_y - mouse_y)*(self.zoom_factor-self.zoom_factor_before)
            self.image_coord=(new_center_x, new_center_y)

    def start_drag(self, event):
        self.is_dragging = True
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
        # 获取图片的边界框坐标
        if self.image_id:
            x1, y1, x2, y2 = self.canvas.bbox(self.image_id)
            
            # 检查鼠标是否在图片边界框外
            if event.x < x1 or event.x > x2 or event.y < y1 or event.y > y2:
                # 计算平移量，将图片边缘平移至鼠标位置
                dx = 0
                dy = 0
                if event.x < x1:
                    dx = event.x - x1
                elif event.x > x2:
                    dx = event.x - x2
                if event.y < y1:
                    dy = event.y - y1
                elif event.y > y2:
                    dy = event.y - y2
                self.canvas.move(self.image_id, dx, dy)
                self.drag_data["x"] = event.x
                self.drag_data["y"] = event.y

    def drag(self, event):
        if self.is_dragging:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.image_id, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def end_drag(self, event):
        self.is_dragging = False
