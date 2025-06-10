import os
import sys
import json
import threading
import subprocess
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import webbrowser
import platform

class BackendServer:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.frontend_started = False
        self.logs = []
        self.browser_opened = False
        self.frontend_process = None
        self.virtual_camera_thread = None
        
    def log(self, message, level='info'):
        timestamp = time.strftime('%H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level
        }
        self.logs.append(log_entry)
        print(f"[{timestamp}] [{level.upper()}] {message}")
        
        # 保持日志大小
        if len(self.logs) > 500:
            self.logs.pop(0)
    
    def start(self):
        if self.is_running:
            return False
            
        self.is_running = True
        self.log("后端服务器启动中...")
        
        # 启动前端线程
        frontend_thread = threading.Thread(target=self.start_frontend, daemon=True)
        frontend_thread.start()
        
        # 启动虚拟摄像头线程
        self.virtual_camera_thread = threading.Thread(target=self.start_virtual_camera, daemon=True)
        self.virtual_camera_thread.start()
        
        # 启动主服务线程
        self.thread = threading.Thread(target=self.run_server, daemon=True)
        self.thread.start()
        
        return True
        
    def stop(self):
        if not self.is_running:
            return
            
        self.log("后端服务器正在停止...")
        
        # 停止前端开发服务器
        if self.frontend_process and self.frontend_process.poll() is None:
            self.log("停止前端开发服务器...")
            try:
                self.frontend_process.terminate()
            except Exception as e:
                self.log(f"停止前端进程失败: {str(e)}", "error")
            self.frontend_process = None
            
        # 停止虚拟摄像头
        self.log("停止虚拟摄像头...")
        
        self.is_running = False
        self.frontend_started = False
        self.browser_opened = False
        
        self.log("后端服务器已停止")
    
    def run_server(self):
        self.log("后台服务已启动")
        
        while self.is_running:
            # 等待前端启动完成
            while not self.frontend_started and self.is_running:
                time.sleep(0.5)
            
            # 只在第一次循环时尝试打开浏览器
            if not self.browser_opened and self.frontend_started:
                try:
                    # 等待Vite完全启动
                    time.sleep(1.5)
                    
                    self.log("尝试打开浏览器...")
                    if webbrowser.open('http://localhost:3000'):
                        self.log("浏览器已成功打开")
                    else:
                        self.log("自动打开浏览器失败，请手动访问 http://localhost:3000", "warning")
                    self.browser_opened = True
                except Exception as e:
                    self.log(f"打开浏览器失败: {str(e)}", "error")
                    self.browser_opened = True
            
            # 每10秒记录一次状态
            time.sleep(10)
            if self.is_running:
                self.log("后台服务运行中...")
    
    def start_frontend(self):
        """启动前端开发服务器"""
        self.log("正在启动前端开发服务器...")
        
        try:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            frontend_dir = os.path.join(current_dir, 'frontend')
            
            self.log(f"前端目录: {frontend_dir}")
            
            # 检查前端目录是否存在
            if not os.path.exists(frontend_dir):
                self.log(f"前端目录不存在: {frontend_dir}", "error")
                return
            
            # 启动 vite 开发服务器
            command = ['npm', 'run', 'dev']
            
            # 调整命令以兼容不同平台
            if platform.system() == 'Windows':
                shell = True
            else:
                shell = False
                
            self.frontend_process = subprocess.Popen(
                command,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=shell
            )
            
            # 日志读取线程
            def log_output():
                while self.frontend_process.poll() is None:
                    line = self.frontend_process.stdout.readline()
                    if line:
                        self.log(f"[前端] {line.strip()}")
                        # 检查前端是否已启动
                        if "Local" in line or "Network" in line:
                            self.frontend_started = True
                            self.log("前端开发服务器已启动")
            
            threading.Thread(target=log_output, daemon=True).start()
            
        except Exception as e:
            self.log(f"启动前端开发服务器失败: {str(e)}", "error")
            import traceback
            self.log(traceback.format_exc(), "error")

    def start_virtual_camera(self):
        """模拟虚拟摄像头线程"""
        self.log("虚拟摄像头模块启动中...")
        time.sleep(2)
        
        if self.is_running:
            self.log("虚拟摄像头已初始化")
        
        # 模拟虚拟摄像头运行
        while self.is_running:
            time.sleep(10)
            if self.is_running:
                self.log("虚拟摄像头工作中...")

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Live2D驱动器启动器")
        self.master.geometry("900x650")
        self.master.minsize(800, 500)
        self.grid(sticky="nsew")
        
        # 设置列和行的权重
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.backend = BackendServer()
        self.create_widgets()
        self.create_status_bar()
        
        # 设置关闭窗口时的处理
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_widgets(self):
        # 控制面板框架
        control_frame = ttk.Frame(self)
        control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # 按钮组
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # 按钮
        self.start_button = ttk.Button(btn_frame, text="启动应用", command=self.start_application)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(btn_frame, text="停止应用", command=self.stop_application, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.install_button = ttk.Button(btn_frame, text="安装依赖", command=self.install_dependencies)
        self.install_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="访问GitHub", command=self.open_github).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="打开日志目录", command=self.open_log_dir).pack(side=tk.RIGHT, padx=5)
        
        # 状态提示
        self.status_label = ttk.Label(control_frame, text="就绪")
        self.status_label.pack(fill=tk.X, pady=5)
        
        # 主框架
        main_frame = ttk.PanedWindow(self, orient=tk.VERTICAL)
        main_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # 组件状态框架
        components_frame = ttk.LabelFrame(main_frame, text="组件状态")
        components_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_frame.add(components_frame)
        
        # 树状视图显示组件状态
        columns = ("component", "status", "version")
        self.tree = ttk.Treeview(components_frame, columns=columns, show="headings")
        
        self.tree.heading("component", text="组件")
        self.tree.heading("status", text="状态")
        self.tree.heading("version", text="版本")
        
        self.tree.column("component", width=150, anchor=tk.W)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("version", width=80, anchor=tk.CENTER)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 添加初始组件
        self.components = {
            "frontend": {"status": "未启动", "version": "-", "id": None},
            "backend": {"status": "未启动", "version": "-", "id": None},
            "tracking": {"status": "未启动", "version": "-", "id": None},
            "vcam": {"status": "未启动", "version": "-", "id": None}
        }
        
        for comp_id, comp_info in self.components.items():
            item_id = self.tree.insert("", "end", values=(comp_id.capitalize(), comp_info["status"], comp_info["version"]))
            comp_info["id"] = item_id
        
        # 日志框架
        log_frame = ttk.LabelFrame(main_frame, text="系统日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        main_frame.add(log_frame)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.configure(state="disabled")
        
        # 日志控制按钮
        log_controls = ttk.Frame(log_frame)
        log_controls.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(log_controls, text="清除日志", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="导出日志", command=self.export_logs).pack(side=tk.LEFT, padx=5)
        
        # 错误计数器
        self.error_count = 0
        self.error_label = ttk.Label(log_controls, text="错误: 0")
        self.error_label.pack(side=tk.RIGHT, padx=10)
    
    def create_status_bar(self):
        # 状态栏
        self.status_bar = ttk.Frame(self)
        self.status_bar.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # 系统信息
        self.system_info = ttk.Label(self.status_bar, text=f"系统: {sys.platform} | Python: {sys.version.split()[0]}")
        self.system_info.pack(side=tk.LEFT)
        
        # 状态指示灯
        self.status_indicator = tk.Canvas(self.status_bar, width=16, height=16, bd=0, highlightthickness=0)
        self.status_indicator.pack(side=tk.RIGHT, padx=10)
        self.update_status_indicator('red')
        
        # 应用状态
        self.app_status = ttk.Label(self.status_bar, text="状态: 停止")
        self.app_status.pack(side=tk.RIGHT)
    
    def update_status_indicator(self, color):
        self.status_indicator.delete("all")
        self.status_indicator.create_oval(2, 2, 14, 14, fill=color, outline=color)
    
    def log_message(self, message, level="info"):
        """添加消息到日志文本框"""
        timestamp = time.strftime('%H:%M:%S')
        
        # 更新错误计数
        if level.lower() == "error":
            self.error_count += 1
            self.error_label.config(text=f"错误: {self.error_count}")
        
        self.log_text.configure(state="normal")
        
        # 添加彩色标签
        tag = level.lower()
        self.log_text.tag_config(tag, foreground=self.get_color_for_level(level))
        
        # 添加消息
        self.log_text.insert(tk.END, f"[{timestamp}] ", tag)
        self.log_text.insert(tk.END, message + "\n", "message")
        
        self.log_text.configure(state="disabled")
        self.log_text.see(tk.END)
    
    def get_color_for_level(self, level):
        if level == "error": return "#ff6b6b"
        if level == "warning": return "#ffb648"
        return "black"
    
    def clear_logs(self):
        """清除日志文本框内容"""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state="disabled")
        self.error_count = 0
        self.error_label.config(text="错误: 0")
        self.log_message("日志已清除")
    
    def export_logs(self):
        """导出日志到文件"""
        self.log_message("导出日志功能尚未实现", "warning")
    
    def start_application(self):
        """启动应用程序"""
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.app_status.config(text="状态: 运行中")
        self.update_status_indicator('#42b983')
        self.log_message("启动应用程序...")
        
        # 更新组件状态
        self.update_component_status("frontend", "启动中...", "#ffb648")
        self.update_component_status("backend", "启动中...", "#ffb648")
        
        # 启动后端服务器
        self.backend.start()
        
        # 添加状态检查线程
        threading.Thread(target=self.monitor_status, daemon=True).start()
    
    def update_component_status(self, comp_id, status, color=None):
        if comp_id in self.components:
            values = (
                comp_id.capitalize(),
                status,
                self.components[comp_id]["version"]
            )
            self.tree.item(self.components[comp_id]["id"], values=values)
            
            if color:
                # 更新行颜色
                self.tree.tag_configure(comp_id, background=color)
                self.tree.item(self.components[comp_id]["id"], tags=(comp_id,))
    
    def monitor_status(self):
        """监控后端状态"""
        while self.backend.is_running:
            if self.backend.frontend_started:
                self.update_component_status("frontend", "运行中", "#e6ffe6")
            else:
                self.update_component_status("frontend", "启动中...", "#fff8e1")
            
            # 更新其他组件状态
            self.update_component_status("backend", "运行中", "#e6ffe6")
            self.update_component_status("tracking", "待启动", "#fffde7")
            self.update_component_status("vcam", "待启动", "#fffde7")
            
            time.sleep(0.5)
        
        # 应用停止后重置状态
        for comp_id in self.components.keys():
            self.update_component_status(comp_id, "已停止", "#ffebee")
    
    def stop_application(self):
        """停止应用程序"""
        self.log_message("停止应用程序...")
        self.backend.stop()
        
        # 更新状态
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.app_status.config(text="状态: 停止")
        self.update_status_indicator('red')
        
        # 更新组件状态
        for comp_id in self.components.keys():
            self.update_component_status(comp_id, "已停止", "#ffebee")
        
        self.log_message("应用程序已停止")
    
    def install_dependencies(self):
        """安装所需依赖"""
        self.log_message("开始安装依赖...")
        
        # 安装前端依赖
        frontend_thread = threading.Thread(target=self.install_frontend_deps, daemon=True)
        frontend_thread.start()
        
        # 安装后端依赖
        backend_thread = threading.Thread(target=self.install_backend_deps, daemon=True)
        backend_thread.start()
    
    def install_frontend_deps(self):
        """安装前端依赖"""
        self.log_message("正在安装前端依赖 (npm install)...")
        
        try:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            frontend_dir = os.path.join(current_dir, 'frontend')
            
            self.log_message(f"前端目录: {frontend_dir}")
            
            if not os.path.exists(frontend_dir):
                self.log_message(f"前端目录不存在: {frontend_dir}", "error")
                return
            
            # 运行 npm install
            self.log_message("运行: npm install")
            
            process = subprocess.Popen(
                ['npm', 'install'],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 读取输出
            for line in process.stdout:
                self.log_message(f"[npm] {line.strip()}")
            
            process.wait()
            if process.returncode == 0:
                self.log_message("前端依赖安装成功", "info")
                self.components["frontend"]["version"] = self.get_npm_version(frontend_dir)
            else:
                self.log_message(f"前端依赖安装失败, 错误代码: {process.returncode}", "error")
        except Exception as e:
            self.log_message(f"前端依赖安装失败: {e}", "error")
    
    def install_backend_deps(self):
        """安装后端依赖"""
        self.log_message("正在安装后端依赖 (pip install)...")
        
        try:
            # 获取当前脚本所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.join(current_dir, 'backend')
            
            self.log_message(f"后端目录: {backend_dir}")
            
            if not os.path.exists(backend_dir):
                self.log_message(f"后端目录不存在: {backend_dir}", "error")
                return
            
            # 运行 pip install
            self.log_message("运行: pip install -r requirements.txt")
            
            process = subprocess.Popen(
                [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # 读取输出
            for line in process.stdout:
                self.log_message(f"[pip] {line.strip()}")
                
            process.wait()
            if process.returncode == 0:
                self.log_message("后端依赖安装成功", "info")
            else:
                self.log_message(f"后端依赖安装失败, 错误代码: {process.returncode}", "error")
        except Exception as e:
            self.log_message(f"后端依赖安装失败: {e}", "error")
    
    def get_npm_version(self, frontend_dir):
        """获取npm版本信息"""
        try:
            package_json = os.path.join(frontend_dir, 'package.json')
            if not os.path.exists(package_json):
                return "-"
            
            with open(package_json, 'r') as f:
                data = json.load(f)
                return data.get('version', '-')
        except:
            return "-"
    
    def open_github(self):
        """打开GitHub项目"""
        try:
            webbrowser.open('https://github.com/508364/live2d-driver')
            self.log_message("GitHub项目页面已打开")
        except:
            self.log_message("无法打开GitHub页面", "warning")
    
    def open_log_dir(self):
        """打开日志目录"""
        self.log_message("日志目录功能尚未实现", "warning")
    
    def on_close(self):
        """处理窗口关闭事件"""
        if self.backend.is_running:
            if messagebox.askyesno("确认", "应用程序仍在运行，确定要退出吗？"):
                self.backend.stop()
                self.master.destroy()
        else:
            self.master.destroy()

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()