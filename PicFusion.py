import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import webbrowser
import requests
import os
from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('tkinterdnd2')

CURRENT_VERSION = "2.0.0"
VERSION_INFO_URL = "https://tv.suyinvip.top/version_info.json"

def concatenate_images(image_paths, direction='horizontal', background_color='white'):
    images = [Image.open(image_path).convert("RGBA") for image_path in image_paths]
    widths, heights = zip(*(img.size for img in images))

    if direction == 'horizontal':
        max_height = max(heights)
        scaled_images = [img.resize((int(img.width * max_height / img.height), max_height), Image.Resampling.LANCZOS) for img in images]
        total_width = sum(img.width for img in scaled_images)
        new_image_size = (total_width, max_height)
    else:
        max_width = max(widths)
        scaled_images = [img.resize((max_width, int(img.height * max_width / img.width)), Image.Resampling.LANCZOS) for img in images]
        total_height = sum(img.height for img in scaled_images)
        new_image_size = (max_width, total_height)

    if background_color == 'transparent':
        new_image = Image.new('RGBA', new_image_size, (0, 0, 0, 0))
    else:
        new_image = Image.new('RGBA', new_image_size, background_color)

    offset = 0
    for img in scaled_images:
        if direction == 'horizontal':
            new_image.paste(img, (offset, 0), img)
            offset += img.width
        else:
            new_image.paste(img, (0, offset), img)
            offset += img.height

    return new_image

def select_images():
    filepaths = filedialog.askopenfilenames(filetypes=[("图像文件", "*.jpg *.jpeg *.png *.bmp *.gif")])
    if filepaths:
        update_image_list(filepaths)

def update_image_list(filepaths):
    global selected_images
    selected_images.extend(filepaths)
    refresh_image_list()
    update_preview()

def clear_images():
    global selected_images
    selected_images = []
    refresh_image_list()
    update_preview()

def remove_image(index):
    global selected_images
    del selected_images[index]
    refresh_image_list()
    update_preview()

def move_image_up(index):
    if index > 0:
        selected_images[index], selected_images[index-1] = selected_images[index-1], selected_images[index]
        refresh_image_list()
        update_preview()

def move_image_down(index):
    if index < len(selected_images) - 1:
        selected_images[index], selected_images[index+1] = selected_images[index+1], selected_images[index]
        refresh_image_list()
        update_preview()

def generate_image():
    if not selected_images:
        messagebox.showwarning("警告", "未选择任何图像！")
        return

    direction = 'horizontal' if direction_var.get() == 1 else 'vertical'
    background_color = color_var.get()

    def run_generation():
        try:
            result_image = concatenate_images(selected_images, direction, background_color)
            output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")])
            if output_path:
                result_image.save(output_path)
                messagebox.showinfo("成功", f"图像已保存到 {output_path}")
        except Exception as e:
            messagebox.showerror("错误", f"生成图像失败：{e}")

    threading.Thread(target=run_generation).start()

def update_preview():
    if not selected_images:
        preview_label.config(image='')
        return

    direction = 'horizontal' if direction_var.get() == 1 else 'vertical'
    background_color = color_var.get()
    result_image = concatenate_images(selected_images, direction, background_color)
    result_image.thumbnail((300, 300), Image.Resampling.LANCZOS)
    preview_image = ImageTk.PhotoImage(result_image)
    preview_label.config(image=preview_image)
    preview_label.image = preview_image

def refresh_image_list():
    for widget in image_frame.winfo_children():
        widget.destroy()

    for index, image_path in enumerate(selected_images):
        image_name = image_path.split('/')[-1]
        label = tk.Label(image_frame, text=image_name)
        label.grid(row=index, column=0, padx=5, pady=5)
        up_button = tk.Button(image_frame, text="上移", command=lambda idx=index: move_image_up(idx))
        up_button.grid(row=index, column=1, padx=5, pady=5)
        down_button = tk.Button(image_frame, text="下移", command=lambda idx=index: move_image_down(idx))
        down_button.grid(row=index, column=2, padx=5, pady=5)
        remove_button = tk.Button(image_frame, text="删除", command=lambda idx=index: remove_image(idx))
        remove_button.grid(row=index, column=3, padx=5, pady=5)

def open_browser():
    webbrowser.open("https://www.123pan.com/s/gTp9-diIr.html")

def drop(event):
    files = app.tk.splitlist(event.data)
    update_image_list(files)

def check_for_updates():
    def run_check():
        try:
            response = requests.get(VERSION_INFO_URL)
            if response.status_code == 200:
                version_info = response.json()
                latest_version = version_info['version']
                download_url = version_info['download_url']
                if latest_version > CURRENT_VERSION:
                    if messagebox.askyesno("更新", f"检测到新版本 {latest_version}，是否下载更新？"):
                        webbrowser.open(download_url)
                else:
                    messagebox.showinfo("更新", "当前已是最新版本。")
            else:
                messagebox.showerror("错误", "无法检查更新。")
        except requests.ConnectionError:
            messagebox.showerror("错误", "网络连接失败。请检查网络连接后重试。")
        except Exception as e:
            messagebox.showerror("错误", f"检查更新失败：{e}")

    threading.Thread(target=run_check).start()

app = TkinterDnD.Tk()
app.title("图像拼接工具吾爱苏音v2.0 ")

selected_images = []

tk.Label(app, text="选定的图像：", font=("Arial", 12)).grid(row=0, column=0, sticky='w', padx=10, pady=5)

image_frame = tk.Frame(app)
image_frame.grid(row=1, column=0, columnspan=4, padx=10, pady=5)

tk.Button(app, text="浏览", command=select_images).grid(row=2, column=0, padx=5, pady=5)
tk.Button(app, text="清空", command=clear_images).grid(row=2, column=1, padx=5, pady=5)

direction_var = tk.IntVar(value=1)
tk.Label(app, text="方向：", font=("Arial", 12)).grid(row=3, column=0, sticky='w', padx=10, pady=5)
tk.Radiobutton(app, text="水平", variable=direction_var, value=1).grid(row=3, column=1, sticky='w', padx=5, pady=5)
tk.Radiobutton(app, text="垂直", variable=direction_var, value=2).grid(row=3, column=2, sticky='w', padx=5, pady=5)

tk.Label(app, text="背景颜色：", font=("Arial", 12)).grid(row=4, column=0, sticky='w', padx=10, pady=5)
color_var = tk.StringVar(value='white')
tk.Radiobutton(app, text="白色", variable=color_var, value='white').grid(row=4, column=1, sticky='w', padx=5, pady=5)
tk.Radiobutton(app, text="黑色", variable=color_var, value='black').grid(row=4, column=2, sticky='w', padx=5, pady=5)
tk.Radiobutton(app, text="透明", variable=color_var, value='transparent').grid(row=4, column=3, sticky='w', padx=5, pady=5)

tk.Button(app, text="生成图像", command=generate_image, font=("Arial", 12)).grid(row=5, column=0, columnspan=4, padx=10, pady=10)

tk.Label(app, text="预览：", font=("Arial", 12)).grid(row=6, column=0, sticky='w', padx=10, pady=5)
preview_label = tk.Label(app)
preview_label.grid(row=7, column=0, columnspan=4, padx=10, pady=5)

link_label = tk.Label(app, text="软件下载", fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
link_label.grid(row=8, column=2, sticky='se', padx=10, pady=10)
link_label.bind("<Button-1>", lambda e: open_browser())

tk.Button(app, text="检查更新", command=check_for_updates, font=("Arial", 10)).grid(row=8, column=0, padx=5, pady=5)

app.drop_target_register(DND_FILES)
app.dnd_bind('<<Drop>>', drop)

app.mainloop()
