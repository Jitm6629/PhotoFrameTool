import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw, ImageFont
import piexif
import os

class PhotoFrameTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoFrameTool - 批量照片加白边工具")
        self.root.geometry("1100x750")

        # 变量存储
        self.img_path_list = []
        self.output_dir = ""
        self.main_img = None

        # 白边边距变量
        self.top_margin = tk.IntVar(value=100)
        self.bottom_margin = tk.IntVar(value=540)
        self.left_margin = tk.IntVar(value=100)
        self.right_margin = tk.IntVar(value=100)

        # 摄影参数变量
        self.camera = tk.StringVar()
        self.lens = tk.StringVar()
        self.aperture = tk.StringVar()
        self.shutter = tk.StringVar()
        self.iso = tk.StringVar()
        self.focal = tk.StringVar()

        self.build_ui()

    def build_ui(self):
        # 主左右分栏
        left_frame = tk.Frame(self.root, width=700)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        right_frame = tk.Frame(self.root, width=360)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # ========== 左侧区域：文件导入+边距设置+预览 ==========
        file_frame = tk.LabelFrame(left_frame, text="文件操作")
        file_frame.pack(fill=tk.X, pady=5)
        tk.Button(file_frame, text="批量导入照片", command=self.load_images).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(file_frame, text="选择输出文件夹", command=self.select_output).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(file_frame, text="一键批量生成", command=self.batch_export).grid(row=0, column=2, padx=5, pady=5)

        # 四边白边设置
        margin_frame = tk.LabelFrame(left_frame, text="四边独立白边设置(像素)")
        margin_frame.pack(fill=tk.X, pady=5)
        tk.Label(margin_frame, text="上边距").grid(row=0, column=0)
        tk.Entry(margin_frame, textvariable=self.top_margin, width=8).grid(row=0, column=1, padx=3)
        tk.Label(margin_frame, text="下边距").grid(row=0, column=2)
        tk.Entry(margin_frame, textvariable=self.bottom_margin, width=8).grid(row=0, column=3, padx=3)
        tk.Label(margin_frame, text="左边距").grid(row=1, column=0)
        tk.Entry(margin_frame, textvariable=self.left_margin, width=8).grid(row=1, column=1, padx=3)
        tk.Label(margin_frame, text="右边距").grid(row=1, column=2)
        tk.Entry(margin_frame, textvariable=self.right_margin, width=8).grid(row=1, column=3, padx=3)

        # 文件列表
        list_frame = tk.LabelFrame(left_frame, text="已导入照片列表")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.file_listbox = tk.Listbox(list_frame)
        scroll = ttk.Scrollbar(list_frame, command=self.file_listbox.yview)
        self.file_listbox.configure(yscrollcommand=scroll.set)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.bind("<<ListboxSelect>>", self.on_select_img)

        # ========== 右侧区域：摄影参数面板 ==========
        param_frame = tk.LabelFrame(right_frame, text="拍摄参数(自动读取EXIF/手动修改)")
        param_frame.pack(fill=tk.X, pady=5)
        tk.Label(param_frame, text="相机型号").grid(row=0, column=0, sticky="w")
        tk.Entry(param_frame, textvariable=self.camera, width=22).grid(row=0, column=1, padx=3, pady=2)
        tk.Label(param_frame, text="镜头").grid(row=1, column=0, sticky="w")
        tk.Entry(param_frame, textvariable=self.lens, width=22).grid(row=1, column=1, padx=3, pady=2)
        tk.Label(param_frame, text="光圈").grid(row=2, column=0, sticky="w")
        tk.Entry(param_frame, textvariable=self.aperture, width=22).grid(row=2, column=1, padx=3, pady=2)
        tk.Label(param_frame, text="快门").grid(row=3, column=0, sticky="w")
        tk.Entry(param_frame, textvariable=self.shutter, width=22).grid(row=3, column=1, padx=3, pady=2)
        tk.Label(param_frame, text="ISO").grid(row=4, column=0, sticky="w")
        tk.Entry(param_frame, textvariable=self.iso, width=22).grid(row=4, column=1, padx=3, pady=2)
        tk.Label(param_frame, text="焦距").grid(row=5, column=0, sticky="w")
        tk.Entry(param_frame, textvariable=self.focal, width=22).grid(row=5, column=1, padx=3, pady=2)
        tk.Button(param_frame, text="重新读取EXIF参数", command=self.read_exif).grid(row=6, column=0, columnspan=2, pady=5)

    def load_images(self):
        paths = filedialog.askopenfilenames(
            title="选择照片",
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png;*.tiff")]
        )
        if not paths:
            return
        self.img_path_list.extend(paths)
        self.refresh_listbox()

    def refresh_listbox(self):
        self.file_listbox.delete(0, tk.END)
        for p in self.img_path_list:
            self.file_listbox.insert(tk.END, os.path.basename(p))

    def select_output(self):
        self.output_dir = filedialog.askdirectory(title="选择导出文件夹")

    def on_select_img(self, event):
        idx = self.file_listbox.curselection()
        if not idx:
            return
        sel_path = self.img_path_list[idx[0]]
        self.main_img = Image.open(sel_path)
        self.read_exif(sel_path)

    def read_exif(self, img_path=None):
        if img_path is None:
            idx = self.file_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选中一张图片")
                return
            img_path = self.img_path_list[idx[0]]
        try:
            exif_data = piexif.load(img_path)
            # 相机信息
            if piexif.ImageIFD.Model in exif_data["0th"]:
                self.camera.set(exif_data["0th"][piexif.ImageIFD.Model].decode("utf-8"))
            # 镜头、光圈、快门、ISO、焦距
            exif_exif = exif_data["Exif"]
            # ISO
            if piexif.ExifIFD.ISOSpeedRatings in exif_exif:
                self.iso.set(str(exif_exif[piexif.ExifIFD.ISOSpeedRatings]))
            # 快门
            if piexif.ExifIFD.ExposureTime in exif_exif:
                num, den = exif_exif[piexif.ExifIFD.ExposureTime]
                if num < den:
                    self.shutter.set(f"1/{den//num}s")
                else:
                    self.shutter.set(f"{num/den:.1f}s")
            # 光圈
            if piexif.ExifIFD.FNumber in exif_exif:
                f_num, f_den = exif_exif[piexif.ExifIFD.FNumber]
                self.aperture.set(f"f/{f_num/f_den:.1f}")
            # 焦距
            if piexif.ExifIFD.FocalLength in exif_exif:
                f_len, f_den = exif_exif[piexif.ExifIFD.FocalLength]
                self.focal.set(f"{f_len/f_den:.0f}mm")
            # 镜头型号
            if piexif.ExifIFD.LensModel in exif_exif:
                self.lens.set(exif_exif[piexif.ExifIFD.LensModel].decode("utf-8"))
        except Exception as e:
            messagebox.showerror("EXIF读取失败", f"无拍摄参数或读取出错：{str(e)}")

    def generate_frame_image(self, img_path):
        # 读取原图
        ori_img = Image.open(img_path).convert("RGB")
        w, h = ori_img.size
        # 读取四边边距
        t = self.top_margin.get()
        b = self.bottom_margin.get()
        l = self.left_margin.get()
        r = self.right_margin.get()
        # 画布总尺寸
        new_w = w + l + r
        new_h = h + t + b
        # 白色画布
        canvas = Image.new("RGB", (new_w, new_h), "white")
        canvas.paste(ori_img, (l, t))

        draw = ImageDraw.Draw(canvas)
        # 字体兼容
        try:
            font = ImageFont.truetype("msyh.ttc", 84)
            small_font = ImageFont.truetype("msyh.ttc", 84)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()

        # 底部区域统一基准Y坐标：图片底部往下30像素开始排版
        bottom_base_y = t + h + 30
        bottom_area_height = b - 40  # 底部边框可用高度
        

        # ====================== 左侧：相机LOGO占位区域 ======================
        logo_x = l + 40
        logo_w, logo_h = 158*3, 35*3
        logo_y = bottom_base_y + (bottom_area_height - logo_h) // 2
        # 绘制占位框（后期替换成真实LOGO图片）
        # 加载LOGO示例（自行替换图片路径）
        try:
            logo_img = Image.open("./logo/canon.png").convert("RGBA")
            logo_img = logo_img.resize((logo_w, logo_h))
            canvas.paste(logo_img, (logo_x, logo_y), mask=logo_img)
        except Exception:
            # 图片不存在时自动回退显示占位框
            draw.rectangle([logo_x, logo_y, logo_x + logo_w, logo_y + logo_h], outline="#888888", width=2)
            draw.text((logo_x + 35, logo_y + 30), "LOGO占位", font=small_font, fill="#666666")

        # ====================== 右侧：拍摄参数贴右边缘 ======================
        # 拼接指定格式参数文本
        param_text = f"{self.shutter.get()}  ISO {self.iso.get()}  {self.aperture.get()}  {self.camera.get()}"
        # 文字贴右边界，距离右边留白40像素
        text_w = draw.textlength(param_text, font=font)
        param_x = new_w - r - 40 - text_w
        param_y = bottom_base_y + (bottom_area_height // 2 - 13)  # 垂直居中
        draw.text((param_x, param_y), param_text, font=font, fill="#222222")

        return canvas

    def batch_export(self):
        if not self.img_path_list:
            messagebox.showwarning("提示", "请先导入照片")
            return
        if not self.output_dir:
            messagebox.showwarning("提示", "请先选择输出文件夹")
            return
        success = 0
        for path in self.img_path_list:
            try:
                # 读取当前图片EXIF更新参数
                self.read_exif(path)
                out_img = self.generate_frame_image(path)
                filename = os.path.splitext(os.path.basename(path))[0] + "_带边框.jpg"
                save_path = os.path.join(self.output_dir, filename)
                out_img.save(save_path, quality=95)
                success += 1
            except Exception as err:
                print(f"处理失败 {path}: {err}")
        messagebox.showinfo("导出完成", f"成功处理 {success}/{len(self.img_path_list)} 张图片")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoFrameTool(root)
    root.mainloop()