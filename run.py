import os
import sys
import json
import threading
import subprocess
import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, font
import webbrowser
import platform
import logging
import socket
import requests
import re
import traceback
from functools import partial

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger()

class BackendManager:
    """后端服务管理器，处理所有子进程和服务"""
    
    def __init__(self):
        self.is_running = False
        self.logs = []
        self.port = None
        self.services = {
            "frontend": {"status": "stopped", "process": None},
            "backend": {"status": "stopped", "process": None},
            "vcam": {"status": "stopped", "process": None},
            "tracking": {"status": "stopped", "process": None}
        }
        self.threads = {}
        self.find_available_port()
    
    def log(self, message, level='info'):
        """记录日志，带有时间戳和日志级别"""
        timestamp = time.strftime('%H:%M:%S')
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'level': level
        }
        self.logs.append(log_entry)
        log_level = getattr(logging, level.upper(), logging.INFO)
        logger.log(log_level, message)
        if len(self.logs) > 1000:
            self.logs.pop(0)
    
    def find_available_port(self, start=3000, max_attempts=20):
        """查找可用端口，默认尝试20个端口"""
        self.log("Searching for available port...", "debug")
        self.port = start
        attempts = 0
        
        while attempts < max_attempts:
            if self.is_port_available(self.port):
                self.log(f"Port {self.port} is available", "info")
                return self.port
            self.log(f"Port {self.port} is occupied, trying next...", "warning")
            self.port += 1
            attempts += 1
        
        # Fallback to start port if no port found
        self.port = start
        self.log(f"Could not find available port, using {self.port}", "error")
        return self.port
    
    def is_port_available(self, port):
        """检查端口是否可用"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex(('127.0.0.1', port))
                return result != 0
        except Exception as e:
            self.log(f"Port check failed: {e}", "error")
            return False
    
    def start_service(self, service_name, target):
        """启动服务线程"""
        if self.services[service_name]["status"] != "stopped":
            self.log(f"{service_name.capitalize()} is already running", "warning")
            return False
        
        self.services[service_name]["status"] = "starting"
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        self.threads[service_name] = thread
        return True
    
    def stop_service(self, service_name):
        """停止服务"""
        if service_name not in self.services or not self.services[service_name]["process"]:
            return
        
        process = self.services[service_name]["process"]
        self.log(f"Stopping {service_name} service...", "info")
        
        try:
            if platform.system() == 'Windows':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)])
            else:
                process.terminate()
                
            # Wait for process to terminate
            process.wait(timeout=3)
            self.services[service_name]["status"] = "stopped"
            self.services[service_name]["process"] = None
            self.log(f"{service_name.capitalize()} service stopped", "info")
        except Exception as e:
            self.log(f"Failed to stop {service_name}: {e}", "error")
    
    def start_all(self):
        """启动所有服务"""
        if self.is_running:
            self.log("Services are already running", "warning")
            return False
        
        self.is_running = True
        self.log("Starting all services...", "info")
        
        # Start backend services
        self.start_service("backend", self.run_backend_service)
        self.start_service("frontend", self.run_frontend_service)
        self.start_service("vcam", self.run_virtual_camera)
        self.start_service("tracking", self.run_facial_tracking)
        
        # Start browser thread after 5 seconds
        threading.Timer(5, self.open_browser).start()
        
        return True
    
    def stop_all(self):
        """停止所有服务"""
        if not self.is_running:
            self.log("Services are not running", "warning")
            return
        
        self.log("Stopping all services...", "info")
        self.is_running = False
        
        # Stop services in reverse order
        for service in ["tracking", "vcam", "frontend", "backend"]:
            self.stop_service(service)
        
        # Join threads
        for service, thread in self.threads.items():
            if thread.is_alive():
                thread.join(timeout=2.0)
                if thread.is_alive():
                    self.log(f"Thread for {service} did not stop gracefully", "warning")
        
        self.threads.clear()
        self.log("All services stopped", "info")
    
    def run_backend_service(self):
        """运行后端服务（模拟）"""
        try:
            self.services["backend"]["status"] = "running"
            self.log("Backend service started", "info")
            
            while self.is_running and self.services["backend"]["status"] == "running":
                self.log("Backend processing requests...", "debug")
                time.sleep(10)
            
            self.services["backend"]["status"] = "stopped"
        except Exception as e:
            self.log(f"Backend service error: {e}", "error")
            self.services["backend"]["status"] = "error"
    
    def run_frontend_service(self):
        """运行前端服务"""
        try:
            frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
            
            # On Windows create a batch file
            if platform.system() == 'Windows':
                script_path = os.path.join(frontend_dir, 'run_vite.bat')
                with open(script_path, 'w') as f:
                    f.write('@echo off\n')
                    f.write('chcp 65001\n')
                    f.write(f'npx vite --port {self.port}\n')
            else:  # Linux/macOS
                script_path = os.path.join(frontend_dir, 'run_vite.sh')
                with open(script_path, 'w') as f:
                    f.write('#!/bin/bash\n')
                    f.write('export LANG=en_US.UTF-8\n')
                    f.write(f'npx vite --port {self.port}\n')
                os.chmod(script_path, 0o755)
            
            self.log(f"Starting frontend service on port {self.port}...", "info")
            process = subprocess.Popen(
                [script_path],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            
            self.services["frontend"]["process"] = process
            self.services["frontend"]["status"] = "running"
            
            # Monitor frontend output
            for line in iter(process.stdout.readline, ''):
                if not self.is_running:
                    break
                
                cleaned_line = line.strip()
                self.log(f"[Frontend] {cleaned_line}", "info")
                
                if "Local:" in cleaned_line or "ready in" in cleaned_line:
                    # Update port from output
                    port_match = re.search(r':(\d+)', cleaned_line)
                    if port_match and port_match.group(1) != str(self.port):
                        self.port = int(port_match.group(1))
                        self.log(f"Updated frontend port to {self.port}", "info")
            
            process.stdout.close()
            process.wait()
            
            if self.is_running:
                self.log("Frontend service exited unexpectedly", "error")
                self.services["frontend"]["status"] = "error"
            else:
                self.log("Frontend service stopped", "info")
                self.services["frontend"]["status"] = "stopped"
                
        except Exception as e:
            self.log(f"Frontend service error: {str(e)}{traceback.format_exc()}", "error")
            self.services["frontend"]["status"] = "error"
    
    def run_virtual_camera(self):
        """运行虚拟摄像头服务（模拟）"""
        try:
            self.log("Starting virtual camera service...", "info")
            self.services["vcam"]["status"] = "running"
            
            # Simulate virtual camera running
            while self.is_running and self.services["vcam"]["status"] == "running":
                self.log("Virtual camera active", "debug")
                time.sleep(8)
                
            self.services["vcam"]["status"] = "stopped"
            self.log("Virtual camera service stopped", "info")
        except Exception as e:
            self.log(f"Virtual camera error: {e}", "error")
            self.services["vcam"]["status"] = "error"
    
    def run_facial_tracking(self):
        """运行面部追踪服务（模拟）"""
        try:
            self.log("Starting facial tracking service...", "info")
            self.services["tracking"]["status"] = "running"
            
            # Simulate facial tracking
            while self.is_running and self.services["tracking"]["status"] == "running":
                self.log("Tracking facial features", "debug")
                time.sleep(5)
                
            self.services["tracking"]["status"] = "stopped"
            self.log("Facial tracking service stopped", "info")
        except Exception as e:
            self.log(f"Facial tracking error: {e}", "error")
            self.services["tracking"]["status"] = "error"
    
    def open_browser(self):
        """在浏览器中打开应用"""
        if not self.is_running:
            return
            
        try:
            if not self.services["frontend"]["status"] == "running":
                self.log("Frontend not ready, delaying browser launch", "warning")
                threading.Timer(2, self.open_browser).start()
                return
            
            url = f"http://localhost:{self.port}"
            self.log(f"Attempting to open browser: {url}", "info")
            
            if webbrowser.open(url):
                self.log("Browser opened successfully", "info")
            elif platform.system() == 'Windows':
                os.system(f'start {url}')
                self.log("Launched browser via system command", "info")
            else:
                self.log("Automatic browser launch failed, please open manually", "warning")
        except Exception as e:
            self.log(f"Failed to open browser: {e}", "error")


class ModernUI(tk.Tk):
    """现代化的GUI界面"""
    
    def __init__(self):
        super().__init__()
        
        self.title("Live2D 驱动器启动器")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # 初始化错误计数器
        self.error_count = 0
        
        # Configure application icon
        self.setup_icon()
        
        # Configure style
        self.setup_styles()
        
        # Initialize backend manager
        self.backend = BackendManager()
        
        # Build UI components
        self.create_layout()
        
        # Handle window close event
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup periodic updates
        self.after(1000, self.update_ui)
    
    def setup_icon(self):
        """尝试设置应用图标"""
        icon_path = None
        try:
            if platform.system() == "Windows":
                icon_path = 'icon.ico' if os.path.exists('icon.ico') else None
                if icon_path:
                    self.iconbitmap(icon_path)
            elif platform.system() == "Darwin":
                icon_path = 'icon.icns' if os.path.exists('icon.icns') else None
                if icon_path:
                    img = tk.PhotoImage(file=icon_path)
                    self.tk.call('wm', 'iconphoto', self._w, img)
        except Exception:
            pass
    
    def setup_styles(self):
        """设置UI样式和主题"""
        # Set window background color
        self.configure(bg="#f5f5f5")
        
        # Configure styles
        self.style = ttk.Style()
        
        # Attempt to use a modern theme
        available_themes = self.style.theme_names()
        preferred_themes = ['vista', 'aqua', 'clam', 'alt', 'default', 'classic']
        
        for theme in preferred_themes:
            if theme in available_themes:
                self.style.theme_use(theme)
                break
        
        # Custom style settings
        self.style.configure('TFrame', background="#f5f5f5")
        self.style.configure('Header.TLabel', background="#4a76a8", foreground="white", font=("Segoe UI", 12, "bold"))
        self.style.configure('Status.TFrame', background="#e0e0e0")
        self.style.configure('Primary.TButton', background="#4a9", foreground="white", font=("Segoe UI", 10, "bold"))
        self.style.configure('Danger.TButton', background="#e74c3c", foreground="white")
        
        # Map button colors
        self.style.map('Primary.TButton',
                      background=[('pressed', '#3a8'), ('active', '#5bb')])
        self.style.map('Danger.TButton',
                      background=[('pressed', '#d62c1a'), ('active', '#f25')])
        
        # Custom status colors for components
        self.status_colors = {
            "stopped": "#f8f9fa",     # Very light gray
            "starting": "#fff3cd",    # Light yellow
            "running": "#d4edda",    # Light green
            "error": "#f8d7da"        # Light red
        }
    
    def create_layout(self):
        """创建UI布局"""
        # 状态栏放在最前面
        self.status_bar = ttk.Frame(self, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 确保error_label在使用前已初始化
        self.error_label = ttk.Label(self.status_bar, text="错误: 0")
        self.error_label.pack(side=tk.RIGHT, padx=10)
        
        # 主容器
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header panel
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Live2D 驱动器控制面板", 
                 style="Header.TLabel", padding=10).pack(fill=tk.X)
        
        # Control panel
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Service buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="启动应用", 
                                    command=self.start_application, style="Primary.TButton")
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止应用", 
                                  command=self.stop_application, style="Danger.TButton", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.install_btn = ttk.Button(btn_frame, text="安装依赖",
                                     command=self.install_dependencies)
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        # Port info and refresh button
        port_frame = ttk.Frame(control_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="当前端口:").pack(side=tk.LEFT)
        self.port_label = ttk.Label(port_frame, text=f"{self.backend.port}")
        self.port_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(port_frame, text="刷新端口", 
                  command=self.refresh_port).pack(side=tk.LEFT)
        
        # Create status panels using notebook for tabbed interface
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Service status tab
        self.service_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.service_tab, text="服务状态")
        self.setup_service_status_tab()
        
        # Logs tab
        self.logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_tab, text="系统日志")
        self.setup_logs_tab()
        
        # System info tab
        self.system_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.system_tab, text="系统信息")
        self.setup_system_info_tab()
    
    def setup_service_status_tab(self):
        """设置服务状态标签页"""
        # Create table for service status
        columns = ("Service", "Status", "Action")
        self.service_tree = ttk.Treeview(self.service_tab, columns=columns, show="headings")
        
        # Configure columns
        for col in columns:
            self.service_tree.heading(col, text=col)
            self.service_tree.column(col, width=100, anchor=tk.CENTER)
        
        # Add services to the table
        services = [
            ("前端服务", "已停止", "启动"),
            ("后端服务", "已停止", "启动"),
            ("虚拟摄像头", "已停止", "启动"),
            ("面部追踪", "已停止", "启动")
        ]
        
        for i, service in enumerate(services):
            self.service_tree.insert("", "end", values=service, iid=f"service_{i}")
        
        self.service_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add action buttons to header
        header_frame = ttk.Frame(self.service_tab)
        header_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(header_frame, text="服务状态监控", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        
        self.start_all_btn = ttk.Button(header_frame, text="启动所有服务", 
                                       command=self.start_application, width=15)
        self.start_all_btn.pack(side=tk.RIGHT, padx=5)
        
        self.stop_all_btn = ttk.Button(header_frame, text="停止所有服务", 
                                      command=self.stop_application, state=tk.DISABLED, width=15)
        self.stop_all_btn.pack(side=tk.RIGHT, padx=5)
        
        # Add button to view service details
        ttk.Button(self.service_tab, text="查看服务详情", 
                 command=self.show_service_details).pack(pady=5)
    
    def setup_logs_tab(self):
        """设置日志标签页"""
        # Log level filter
        filter_frame = ttk.Frame(self.logs_tab)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="日志级别:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_level = tk.StringVar(value="info")
        log_levels = [("全部", "all"), ("调试", "debug"), ("信息", "info"), 
                     ("警告", "warning"), ("错误", "error")]
        
        for text, level in log_levels:
            rb = ttk.Radiobutton(filter_frame, text=text, value=level, 
                                variable=self.log_level, 
                                command=self.update_log_view)
            rb.pack(side=tk.LEFT, padx=5)
        
        # Log controls
        ctrl_frame = ttk.Frame(self.logs_tab)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(ctrl_frame, text="清除日志", 
                  command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="导出日志", 
                  command=self.export_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl_frame, text="打开日志目录", 
                  command=self.open_log_dir).pack(side=tk.RIGHT, padx=5)
        
        # Log display area
        log_frame = ttk.Frame(self.logs_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 确保log_text在访问前已初始化
        self.log_text = scrolledtext.ScrolledText(
            log_frame, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)
        
        # Configure log text colors
        self.log_text.tag_config('debug', foreground='#666666')
        self.log_text.tag_config('info', foreground='#000000')
        self.log_text.tag_config('warning', foreground='#b95e00')
        self.log_text.tag_config('error', foreground='#e60000')
        
        # 不要在初始化时调用update_log_view - 它会在update_ui中调用
        
    def setup_system_info_tab(self):
        """设置系统信息标签页"""
        # System info in grid layout
        info_frame = ttk.Frame(self.system_tab)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # System information
        sys_info = [
            ("操作系统:", platform.platform()),
            ("Python 版本:", sys.version.split()[0]),
            ("系统架构:", platform.architecture()[0]),
            ("CPU:", platform.processor() or "Unknown"),
            ("工作目录:", os.getcwd()),
            ("日志目录:", os.path.join(os.getcwd(), "logs"))
        ]
        
        # Display system information
        for i, (label, value) in enumerate(sys_info):
            ttk.Label(info_frame, text=label, font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky=tk.W, padx=10, pady=5)
            ttk.Label(info_frame, text=value).grid(
                row=i, column=1, sticky=tk.W, padx=10, pady=5)
        
        # Buttons for system actions
        btn_frame = ttk.Frame(self.system_tab)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="打开 GitHub 项目", 
                  command=self.open_github).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="检查更新", 
                  command=self.check_for_updates).pack(side=tk.LEFT, padx=10)
    
    def update_ui(self):
        """定期更新UI状态"""
        # 确保所有UI元素已初始化
        if not hasattr(self, 'error_label') or not hasattr(self, 'start_btn'):
            self.after(1000, self.update_ui)  # 延迟后再尝试
            return
            
        if self.backend.is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            if hasattr(self, 'start_all_btn'):
                self.start_all_btn.config(state=tk.DISABLED)
                self.stop_all_btn.config(state=tk.NORMAL)
            self.status_label.config(text="应用中...")
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            if hasattr(self, 'start_all_btn'):
                self.start_all_btn.config(state=tk.NORMAL)
                self.stop_all_btn.config(state=tk.DISABLED)
            self.status_label.config(text="就绪")
        
        # Update service statuses
        if hasattr(self, 'service_tree'):
            services = ["frontend", "backend", "vcam", "tracking"]
            for i, service in enumerate(services):
                status = self.backend.services[service]["status"].capitalize()
                background = self.status_colors.get(self.backend.services[service]["status"], "#ffffff")
                
                # Update tree view
                self.service_tree.item(f"service_{i}", values=(
                    self.service_tree.item(f"service_{i}", 'values')[0],
                    status,
                    "停止" if self.backend.services[service]["status"] == "running" else "启动"
                ))
                
                # Update row background color
                self.service_tree.tag_configure(f"row_{i}", background=background)
                self.service_tree.item(f"service_{i}", tags=(f"row_{i}",))
        
        # Update port info
        if hasattr(self, 'port_label'):
            self.port_label.config(text=str(self.backend.port))
        
        # Update logs
        self.update_log_view()
        
        # Schedule next update
        self.after(1000, self.update_ui)
    
    def update_log_view(self):
        """根据当前筛选级别更新日志视图"""
        if not hasattr(self, 'log_text') or not hasattr(self, 'error_label'):
            return  # 如果未初始化则返回
            
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        
        level_filter = self.log_level.get()
        current_errors = 0
        
        for entry in self.backend.logs:
            if level_filter != "all" and entry['level'] != level_filter:
                continue
                
            if entry['level'] == 'error':
                current_errors += 1
                
            self.log_text.insert(
                tk.END, 
                f"[{entry['timestamp']}] {entry['message']}\n", 
                entry['level']
            )
        
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.error_count = current_errors
        self.error_label.config(text=f"错误: {self.error_count}")
    
    def start_application(self):
        """启动整个应用程序"""
        if not hasattr(self, 'status_label'):
            return  # 防止在UI初始化完成前调用
            
        self.status_label.config(text="正在启动服务...")
        
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "启动应用程序中...\n", 'info')
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        threading.Thread(target=self._start_services, daemon=True).start()
    
    def _start_services(self):
        """在后台线程中启动服务"""
        try:
            if not self.backend.start_all():
                if hasattr(self, 'log_text'):
                    self.log_text.config(state=tk.NORMAL)
                    self.log_text.insert(tk.END, "服务已启动或启动失败\n", 'warning')
                    self.log_text.config(state=tk.DISABLED)
        except Exception as e:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"启动错误: {e}\n", 'error')
                self.log_text.config(state=tk.DISABLED)
    
    def stop_application(self):
        """停止整个应用程序"""
        if not hasattr(self, 'status_label'):
            return  # 防止在UI初始化完成前调用
            
        self.status_label.config(text="正在停止服务...")
        
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "停止应用程序中...\n", 'info')
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
        
        threading.Thread(target=self.backend.stop_all, daemon=True).start()
    
    def refresh_port(self):
        """刷新端口设置"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"刷新端口中...\n", 'info')
            self.log_text.config(state=tk.DISABLED)
            
        self.backend.find_available_port()
        
        if hasattr(self, 'port_label'):
            self.port_label.config(text=str(self.backend.port))
            
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"端口已刷新: {self.backend.port}\n", 'info')
            self.log_text.config(state=tk.DISABLED)
    
    def install_dependencies(self):
        """安装依赖项"""
        # 仅当log_text已初始化时才显示消息
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "开始安装依赖...\n", 'info')
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def clear_logs(self):
        """清除日志显示"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    def export_logs(self):
        """导出日志到文件"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "导出日志到文件...\n", 'info')
            self.log_text.config(state=tk.DISABLED)
    
    def open_log_dir(self):
        """打开日志目录"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "打开日志目录...\n", 'info')
            self.log_text.config(state=tk.DISABLED)
    
    def open_github(self):
        """打开GitHub项目页面"""
        try:
            webbrowser.open('https://github.com/508364/live2d-driver')
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, "GitHub项目页面已打开\n", 'info')
                self.log_text.config(state=tk.DISABLED)
        except Exception as e:
            if hasattr(self, 'log_text'):
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"无法打开GitHub: {e}\n", 'error')
                self.log_text.config(state=tk.DISABLED)
    
    def check_for_updates(self):
        """检查更新"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, "正在检查更新...\n", 'info')
            self.log_text.config(state=tk.DISABLED)
    
    def show_service_details(self):
        """显示服务详情对话框"""
        if hasattr(self, 'service_tree'):
            selected_item = self.service_tree.focus()
            if selected_item:
                service_name = self.service_tree.item(selected_item, 'values')[0]
                messagebox.showinfo("服务详情", f"{service_name}的详细信息将显示在这里")
    
    def on_closing(self):
        """窗口关闭时的处理"""
        if self.backend.is_running:
            if not messagebox.askyesno(
                "确认关闭", 
                "应用程序仍在运行中。确定要退出吗？",
                icon='warning'
            ):
                return
        
        self.destroy()


if __name__ == "__main__":
    app = ModernUI()
    app.mainloop()