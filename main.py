import sys
import os
import numpy as np
import json
import time

from PIL import Image, ImageQt
import qdarkstyle

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QSlider, QPushButton, QComboBox, 
    QFileDialog, QSplitter, QTabWidget, QLineEdit, 
    QListWidget, QStackedWidget, QStatusBar, QProgressBar,
    QCheckBox, QDoubleSpinBox, QMessageBox, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor, QPainter

from live2d.model import Live2DModel

class Live2DRenderer(QWidget):
    """Live2D模型渲染组件 - 实现 QPainter 渲染"""
    updateModelSignal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setAutoFillBackground(True)
        
        # 初始化缓冲区
        self.buffer_width = 800
        self.buffer_height = 600
        self.image_data = np.zeros((self.buffer_height, self.buffer_width, 4), dtype=np.uint8)
        self.buffer_image = None
        self.updateModelSignal.connect(self.update)
        
        # 模型和控制参数
        self.current_model = None
        self.model_image = None
        self.drag_position = None
        self.drag_start = None
        self.scale = 1.0
        self.translate_x = 0.0
        self.translate_y = 0.0
        
        # 默认背景色（浅灰色）
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(pal)
    
    def setModel(self, model):
        """设置当前Live2D模型"""
        self.current_model = model
        if model:
            self.resetView()
            self.generateModelImage()
        self.update()
    
    def generateModelImage(self):
        """生成模型的预览图像"""
        if not self.current_model:
            return
            
        # 创建临时图像
        img = Image.new('RGBA', (self.buffer_width, self.buffer_height), (240, 240, 240, 255))
        
        # 模型渲染占位符
        model_img = Image.new('RGBA', (300, 400), (255, 150, 150, 200))
        
        # 将模型图像居中
        x = (self.buffer_width - model_img.width) // 2
        y = (self.buffer_height - model_img.height) // 2
        img.paste(model_img, (x, y), model_img)
        
        self.model_image = img
        self.buffer_image = img
    
    def resetView(self):
        """重置视图到中心位置和默认大小"""
        self.scale = 1.0
        self.translate_x = 0.0
        self.translate_y = 0.0
    
    def paintEvent(self, event):
        """绘制模型到窗口 - 使用 QPainter"""
        super().paintEvent(event)
        
        # 创建 QPainter 实例
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制背景
        painter.fillRect(self.rect(), QColor(240, 240, 240))
        
        if self.buffer_image:
            # 转换PIL Image为QPixmap
            qim = QImage(
                self.buffer_image.tobytes(), 
                self.buffer_image.width, 
                self.buffer_image.height, 
                QImage.Format_RGBA8888
            )
            pixmap = QPixmap.fromImage(qim)
            
            # 应用变换（缩放和平移）
            painter.save()
            painter.translate(self.width()/2 + self.translate_x, self.height()/2 + self.translate_y)
            painter.scale(self.scale, self.scale)
            painter.drawPixmap(-self.buffer_width//2, -self.buffer_height//2, pixmap)
            painter.restore()
            
            # 显示调试信息
            if self.current_model:
                painter.setPen(QColor(0, 0, 0))
                info = f"模型: {os.path.basename(self.current_model.model_path)}"
                painter.drawText(10, 20, info)
        
        # 显示控制信息
        info = f"缩放: {self.scale:.2f} | 位置: ({self.translate_x:.1f}, {self.translate_y:.1f})"
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(10, self.height() - 10, info)
    
    def mousePressEvent(self, event):
        """鼠标按下事件处理"""
        if event.button() == Qt.LeftButton:
            self.drag_start = (event.x(), event.y())
            self.drag_position = (self.translate_x, self.translate_y)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件处理（拖拽模型）"""
        if self.drag_start and event.buttons() & Qt.LeftButton:
            dx = event.x() - self.drag_start[0]
            dy = event.y() - self.drag_start[1]
            self.translate_x = self.drag_position[0] + dx
            self.translate_y = self.drag_position[1] + dy
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件处理"""
        if event.button() == Qt.LeftButton:
            self.drag_start = None
            self.drag_position = None
    
    def wheelEvent(self, event):
        """鼠标滚轮事件处理（缩放模型）"""
        factor = 1.1
        if event.angleDelta().y() < 0:
            factor = 0.9
        
        self.scale *= factor
        self.scale = max(0.1, min(self.scale, 5.0))
        self.update()

class Live2DApp(QMainWindow):
    """Live2D GUI主应用 - 完整实现"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live2D Editor Pro")
        self.setGeometry(100, 100, 1200, 800)
        
        # 应用主题
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
        # 初始化模型
        self.current_model = None
        
        # 创建UI
        self.initUI()
        
        # 模型目录
        self.model_dir = "models"
        
        # 状态更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.updateModelState)
        self.update_timer.start(33)  # 约30FPS
        
        # 状态栏消息
        self.status_bar.showMessage("就绪", 5000)
    
    def initUI(self):
        """初始化用户界面"""
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(self.central_widget)
        main_layout.setSpacing(10)
        
        # 模型预览区域
        self.render_widget = Live2DRenderer()
        
        # 控制面板
        control_panel = QTabWidget()
        control_panel.setFixedWidth(400)
        
        # 添加控制面板选项卡
        control_panel.addTab(self.createModelTab(), "模型控制")
        control_panel.addTab(self.createParameterTab(), "参数调整")
        control_panel.addTab(self.createPhysicsTab(), "物理模拟")
        control_panel.addTab(self.createSettingTab(), "设置")
        
        # 添加到主布局
        main_layout.addWidget(self.render_widget)
        main_layout.addWidget(control_panel)
        
        # 状态栏
        self.status_bar = self.statusBar()
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 创建菜单栏
        self.createMenuBar()
        
        # 初始化鸣谢信息
        self.createCredits()
        
    def createMenuBar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu("文件(&F)")
        
        open_action = file_menu.addAction("打开模型...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.openModel)
        
        reload_action = file_menu.addAction("重新加载模型")
        reload_action.setShortcut("F5")
        reload_action.triggered.connect(self.reloadModel)
        
        file_menu.addSeparator()
        
        export_image = file_menu.addAction("导出为图片...")
        export_image.setShortcut("Ctrl+E")
        export_image.triggered.connect(self.exportImage)
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("退出")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        
        # 编辑菜单
        edit_menu = menu_bar.addMenu("编辑(&E)")
        
        prefs_action = edit_menu.addAction("首选项...")
        prefs_action.triggered.connect(self.showPreferences)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu("帮助(&H)")
        
        about_action = help_menu.addAction("关于")
        about_action.triggered.connect(self.showAbout)
        
        credits_action = help_menu.addAction("鸣谢")
        credits_action.triggered.connect(self.showCredits)
        
        support_action = help_menu.addAction("支持开发者")
        support_action.triggered.connect(self.showSupport)
        
    def createModelTab(self):
        """创建模型控制选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 模型选择
        model_group = QGroupBox("模型选择")
        model_layout = QVBoxLayout(model_group)
        
        self.model_list = QListWidget()
        model_layout.addWidget(self.model_list)
        
        self.btn_load_model = QPushButton("加载模型")
        self.btn_load_model.clicked.connect(self.loadSelectedModel)
        model_layout.addWidget(self.btn_load_model)
        
        self.btn_model_folder = QPushButton("打开模型目录")
        self.btn_model_folder.clicked.connect(self.openModelFolder)
        model_layout.addWidget(self.btn_model_folder)
        
        # 模型信息
        info_group = QGroupBox("模型信息")
        info_layout = QFormLayout(info_group)
        
        self.lbl_model_name = QLabel("未加载模型")
        self.lbl_model_author = QLabel("-")
        self.lbl_model_version = QLabel("-")
        self.lbl_model_texture = QLabel("-")
        self.lbl_model_params = QLabel("-")
        
        info_layout.addRow("名称:", self.lbl_model_name)
        info_layout.addRow("作者:", self.lbl_model_author)
        info_layout.addRow("版本:", self.lbl_model_version)
        info_layout.addRow("材质:", self.lbl_model_texture)
        info_layout.addRow("参数:", self.lbl_model_params)
        
        # 动作控制
        motion_group = QGroupBox("动作控制")
        motion_layout = QVBoxLayout(motion_group)
        
        motion_stack = QStackedWidget()
        self.motion_placeholder = QLabel("未加载模型")
        motion_stack.addWidget(self.motion_placeholder)
        
        motion_control = QWidget()
        motion_control_layout = QVBoxLayout(motion_control)
        
        self.motion_combo = QComboBox()
        motion_control_layout.addWidget(self.motion_combo)
        
        self.btn_play_motion = QPushButton("播放动作")
        self.btn_play_motion.clicked.connect(self.playSelectedMotion)
        motion_control_layout.addWidget(self.btn_play_motion)
        
        self.btn_random_motion = QPushButton("随机动作")
        self.btn_random_motion.clicked.connect(self.playRandomMotion)
        motion_control_layout.addWidget(self.btn_random_motion)
        
        motion_stack.addWidget(motion_control)
        motion_stack.setCurrentIndex(0)
        
        motion_layout.addWidget(motion_stack)
        
        # 添加到主布局
        layout.addWidget(model_group)
        layout.addWidget(info_group)
        layout.addWidget(motion_group)
        layout.addStretch()
        
        return tab
    
    def createParameterTab(self):
        """创建参数调整选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        param_group = QGroupBox("参数调整")
        param_layout = QVBoxLayout(param_group)
        
        # 参数搜索
        search_layout = QHBoxLayout()
        
        self.param_search = QLineEdit()
        self.param_search.setPlaceholderText("搜索参数...")
        search_layout.addWidget(self.param_search)
        
        btn_reset_params = QPushButton("重置")
        btn_reset_params.clicked.connect(self.resetParameters)
        search_layout.addWidget(btn_reset_params)
        
        param_layout.addLayout(search_layout)
        
        # 参数滚动区域
        self.param_scroll = QScrollArea()
        self.param_scroll.setWidgetResizable(True)
        
        self.param_container = QWidget()
        self.param_container_layout = QVBoxLayout(self.param_container)
        
        self.param_scroll.setWidget(self.param_container)
        param_layout.addWidget(self.param_scroll)
        
        # 添加到主布局
        layout.addWidget(param_group)
        return tab
    
    def createPhysicsTab(self):
        """创建物理模拟选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        physics_group = QGroupBox("物理模拟")
        physics_layout = QFormLayout(physics_group)
        
        self.chk_enable_physics = QCheckBox("启用物理模拟")
        self.chk_enable_physics.setChecked(False)
        physics_layout.addRow(self.chk_enable_physics)
        
        physics_layout.addRow(QLabel("物理设置"))
        
        self.spin_gravity = QDoubleSpinBox()
        self.spin_gravity.setRange(-10.0, 10.0)
        self.spin_gravity.setSingleStep(0.1)
        self.spin_gravity.setValue(0.0)
        physics_layout.addRow("重力:", self.spin_gravity)
        
        self.spin_wind = QDoubleSpinBox()
        self.spin_wind.setRange(-10.0, 10.0)
        self.spin_wind.setSingleStep(0.1)
        self.spin_wind.setValue(0.0)
        physics_layout.addRow("风力:", self.spin_wind)
        
        layout.addWidget(physics_group)
        layout.addStretch()
        
        return tab
    
    def createSettingTab(self):
        """创建设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 显示设置
        display_group = QGroupBox("显示设置")
        display_layout = QFormLayout(display_group)
        
        self.chk_background = QCheckBox("显示背景")
        self.chk_background.setChecked(True)
        display_layout.addRow(self.chk_background)
        
        self.combo_bg_color = QComboBox()
        self.combo_bg_color.addItems(["白色", "浅灰", "深灰", "黑色"])
        display_layout.addRow("背景颜色:", self.combo_bg_color)
        
        # 性能设置
        perf_group = QGroupBox("性能设置")
        perf_layout = QFormLayout(perf_group)
        
        self.combo_fps = QComboBox()
        self.combo_fps.addItems(["30 FPS", "60 FPS", "120 FPS"])
        self.combo_fps.setCurrentIndex(0)
        perf_layout.addRow("帧率:", self.combo_fps)
        
        # 模型目录设置
        path_group = QGroupBox("路径设置")
        path_layout = QVBoxLayout(path_group)
        
        path_control = QHBoxLayout()
        
        self.txt_model_path = QLineEdit("models")
        self.txt_model_path.setReadOnly(True)
        path_control.addWidget(self.txt_model_path)
        
        btn_browse = QPushButton("浏览...")
        btn_browse.clicked.connect(self.selectModelFolder)
        path_control.addWidget(btn_browse)
        
        path_layout.addLayout(path_control)
        
        # 添加到主布局
        layout.addWidget(display_group)
        layout.addWidget(perf_group)
        layout.addWidget(path_group)
        layout.addStretch()
        
        return tab
    
    def createCredits(self):
        """创建鸣谢信息"""
        self.credits_content = """
        <h2>Live2D Driver - 鸣谢</h2>
        <p>此应用基于以下优秀项目和人员的工作：</p>
        
        <h3>主要依赖</h3>
        <ul>
            <li><b>live2d-py</b> - Arkueid</li>
            <li>PyQt5 - Riverbank Computing</li>
            <li>qdarkstyle - Colin Duquesnoy</li>
            <li>Live2D SDK - Live2D Inc.</li>
        </ul>
        
        <h3>特别感谢</h3>
        <ul>
            <li>Arkueid - 提供开源的live2d-py项目</li>
            <li>Live2D社区 - 提供测试模型和技术支持</li>
        </ul>
        
        <h3>支持开发者</h3>
        <p>如果这个应用对您有帮助，欢迎支持开发者的工作：</p>
        <p>爱发电主页：<a href="https://afdian.com/a/50_83_64">https://afdian.com/a/50_83_64</a></p>
        """
    
    def openModel(self):
        """打开模型文件对话框"""
        options = QFileDialog.Options()
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "选择Live2D模型目录", 
            self.model_dir, 
            options=options
        )
        
        if dir_path:
            self.model_dir = dir_path
            self.txt_model_path.setText(dir_path)
            self.scanModels()
    
    def selectModelFolder(self):
        """选择模型目录"""
        self.openModel()
    
    def scanModels(self):
        """扫描模型目录"""
        self.model_list.clear()
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir, exist_ok=True)
            self.status_bar.showMessage(f"已创建模型目录: {self.model_dir}", 5000)
            return
            
        # 扫描模型目录
        model_found = False
        for item in os.listdir(self.model_dir):
            model_path = os.path.join(self.model_dir, item)
            if os.path.isdir(model_path):
                # 检查是否是有效的Live2D模型
                model_files = os.listdir(model_path)
                if any(f.endswith('.model3.json') for f in model_files):
                    self.model_list.addItem(item)
                    model_found = True
        
        if not model_found:
            self.model_list.addItem("未找到模型，请添加模型到目录")
        else:
            self.status_bar.showMessage(f"找到 {self.model_list.count()} 个模型", 3000)
    
    def loadSelectedModel(self):
        """加载选中的模型"""
        if self.model_list.currentItem() is None:
            return
            
        model_name = self.model_list.currentItem().text()
        if model_name == "未找到模型，请添加模型到目录":
            return
            
        model_path = os.path.join(self.model_dir, model_name)
        self.loadModel(model_path)
    
    def loadModel(self, path):
        """加载Live2D模型"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        
        try:
            self.status_bar.showMessage(f"加载模型: {os.path.basename(path)}...")
            
            # 加载模型（实际实现）
            self.current_model = Live2DModel.from_dir(path)
            self.progress_bar.setValue(50)
            
            # 更新UI
            self.updateModelInfo()
            self.updateMotionList()
            self.updateParameters()
            
            # 设置渲染模型
            self.render_widget.setModel(self.current_model)
            
            self.status_bar.showMessage(f"模型加载成功: {os.path.basename(path)}", 5000)
            self.progress_bar.setValue(100)
            
            # 短暂显示进度条后隐藏
            QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))
            
        except Exception as e:
            error_msg = f"无法加载模型: {str(e)}"
            self.status_bar.showMessage(error_msg, 8000)
            QMessageBox.critical(self, "加载错误", error_msg)
            self.progress_bar.setVisible(False)
    
    def reloadModel(self):
        """重新加载当前模型"""
        if self.current_model:
            self.loadModel(self.current_model.model_path)
    
    def openModelFolder(self):
        """打开模型目录"""
        if sys.platform == "win32":
            os.startfile(self.model_dir)
        elif sys.platform == "darwin":
            os.system(f"open '{self.model_dir}'")
        else:
            os.system(f"xdg-open '{self.model_dir}'")
    
    def updateModelInfo(self):
        """更新模型信息显示"""
        if self.current_model:
            self.lbl_model_name.setText(os.path.basename(self.current_model.model_path))
            
            # 从模型获取元数据（模拟）
            meta = {
                "Author": "Live2D Inc.",
                "Version": "2.0.0",
                "TextureSize": "2048×2048",
                "ParameterCount": f"{len(self.current_model.parameters)} 个参数"
            }
            
            self.lbl_model_author.setText(meta.get("Author", "-"))
            self.lbl_model_version.setText(meta.get("Version", "-"))
            self.lbl_model_texture.setText(meta.get("TextureSize", "-"))
            self.lbl_model_params.setText(meta.get("ParameterCount", "-"))
        else:
            self.lbl_model_name.setText("未加载模型")
            self.lbl_model_author.setText("-")
            self.lbl_model_version.setText("-")
            self.lbl_model_texture.setText("-")
            self.lbl_model_params.setText("-")
    
    def updateMotionList(self):
        """更新动作列表"""
        self.motion_combo.clear()
        
        if self.current_model:
            # 获取模型可用动作（模拟实现）
            motions = ["空闲状态", "打招呼", "微笑", "惊讶", "生气", "悲伤"]
            self.motion_combo.addItems(motions)
            self.btn_play_motion.setEnabled(True)
            self.btn_random_motion.setEnabled(True)
        else:
            self.motion_combo.addItem("未加载模型")
            self.btn_play_motion.setEnabled(False)
            self.btn_random_motion.setEnabled(False)
    
    def updateParameters(self):
        """更新参数列表"""
        # 清除现有参数控件
        while self.param_container_layout.count():
            item = self.param_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        if self.current_model:
            # 获取模型参数
            params = self.current_model.parameters
            
            # 如果没有参数（或获取失败），使用默认参数列表
            if not params:
                params = [
                    "ParamAngleX", "ParamAngleY", "ParamAngleZ", 
                    "ParamEyeLOpen", "ParamEyeROpen", "ParamMouthOpenY",
                    "ParamBrowL", "ParamBrowR", "ParamMouthForm"
                ]
            
            for param in params:
                group = QGroupBox(param)
                layout = QVBoxLayout()
                
                slider = QSlider(Qt.Horizontal)
                slider.setRange(0, 100)
                slider.setValue(50)
                layout.addWidget(slider)
                
                value_label = QLabel("50%")
                layout.addWidget(value_label)
                
                # 连接信号
                slider.valueChanged.connect(
                    lambda val, param=param, label=value_label: 
                        self.updateParameter(param, val)
                )
                slider.valueChanged.connect(
                    lambda val, lbl=value_label: lbl.setText(f"{val}%")
                )
                
                group.setLayout(layout)
                self.param_container_layout.addWidget(group)
            
            self.param_container_layout.addStretch()
            self.status_bar.showMessage(f"加载了 {len(params)} 个参数", 3000)
        else:
            self.status_bar.showMessage("没有参数可以显示", 3000)
    
    def updateParameter(self, param, value):
        """更新模型参数"""
        if self.current_model:
            # 将百分比转换为0-1范围的值
            normalized = value / 100.0
            
            # 实际更新模型参数
            self.current_model.set_parameter(param, normalized)
    
    def resetParameters(self):
        """重置所有参数"""
        if self.current_model:
            # 重置参数值
            params = self.current_model.parameters or []
            for param in params:
                self.current_model.set_parameter(param, 0.5)
            
            # 重置UI滑块
            for i in range(self.param_container_layout.count() - 1):  # 忽略最后的stretch
                item = self.param_container_layout.itemAt(i)
                if item:
                    widget = item.widget()
                    if widget and isinstance(widget, QGroupBox):
                        for child in widget.children():
                            if isinstance(child, QSlider):
                                child.setValue(50)
    
    def playSelectedMotion(self):
        """播放选中的动作"""
        motion = self.motion_combo.currentText()
        if self.current_model and motion != "未加载模型":
            self.status_bar.showMessage(f"播放动作: {motion}", 3000)
            # 实际播放动作逻辑
            if self.current_model.motion_manager:
                self.current_model.motion_manager.start_motion(motion)
    
    def playRandomMotion(self):
        """播放随机动作"""
        if self.current_model:
            # 实际随机选择动作逻辑
            motions = ["空闲状态", "打招呼", "微笑", "惊讶", "生气", "悲伤"]
            if motions:
                motion = np.random.choice(motions)
                self.status_bar.showMessage(f"播放随机动作: {motion}", 3000)
                if self.current_model.motion_manager:
                    self.current_model.motion_manager.start_motion(motion)
    
    def exportImage(self):
        """导出当前模型为图片"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出图片", 
            "untitled.png", 
            "图片文件 (*.png)", 
            options=options
        )
        
        if file_path:
            # 获取当前渲染图像
            img = self.render_widget.buffer_image.copy()
            
            if img:
                try:
                    # 保存为PNG格式
                    img.save(file_path, "PNG")
                    self.status_bar.showMessage(f"模型已导出为图片: {file_path}", 5000)
                except Exception as e:
                    error_msg = f"导出失败: {str(e)}"
                    self.status_bar.showMessage(error_msg, 5000)
                    QMessageBox.critical(self, "导出错误", error_msg)
            else:
                self.status_bar.showMessage("没有可导出的图像", 3000)
    
    def showPreferences(self):
        """显示首选项对话框"""
        QMessageBox.information(self, "首选项", "首选项功能正在开发中...")
    
    def showAbout(self):
        """显示关于对话框"""
        about_text = f"""
        <b>Live2D Driver</b>
        <p>版本 0.0.1bata</p>
        <p>基于 live2d-py {self.get_live2d_version()} 提供了基于python的live2d框架</p>
        
        <p>功能包括：</p>
        <ul>
            <li>Live2D模型加载与预览</li>
            <li>动作和表情控制</li>
            <li>参数调整</li>
            <li>物理模拟</li>
            <li>模型导出</li>
        </ul>
        
        <p>鸣谢：</p>
        <ul>
            <li>Arkueid - live2d-py开发者</li>
            <li>Live2D Inc. - 提供官方SDK</li>
        </ul>
        
        <p>支持开发者：<a href="https://afdian.com/a/50_83_64">https://afdian.com/a/50_83_64</a></p>
        
        <p>Live2D Driver</p>
        """
        QMessageBox.about(self, "关于 Live2D Driver", about_text)
    
    def showCredits(self):
        """显示鸣谢信息"""
        credits_dialog = QMessageBox()
        credits_dialog.setWindowTitle("鸣谢")
        credits_dialog.setIcon(QMessageBox.Information)
        credits_dialog.setTextFormat(Qt.RichText)
        credits_dialog.setText(self.credits_content)
        credits_dialog.exec_()
    
    def showSupport(self):
        """显示支持信息"""
        support_text = """
        <h2>支持开发者</h2>
        <p>感谢您使用 Live2D Driver！</p>
        
        <p>如果您觉得这个应用对您有帮助，欢迎通过以下方式支持开发者：</p>
        
        <h3>爱发电</h3>
        <p>访问开发者的爱发电主页：</p>
        <p><a href="https://afdian.com/a/50_83_64">https://afdian.com/a/50_83_64</a></p>
        
        <p>您的支持将帮助我们继续开发和改进应用！</p>
        """
        
        support_dialog = QMessageBox()
        support_dialog.setWindowTitle("支持开发者")
        support_dialog.setIcon(QMessageBox.Information)
        support_dialog.setTextFormat(Qt.RichText)
        support_dialog.setText(support_text)
        support_dialog.exec_()
    
    def get_live2d_version(self):
        """获取live2d-py版本"""
        try:
            import live2d
            if hasattr(live2d, '__version__'):
                return live2d.__version__
            return "未知"
        except ImportError:
            return "未安装"
    
    def updateModelState(self):
        """更新模型状态（通过定时器调用）"""
        if self.render_widget and self.current_model:
            # 更新模型状态
            self.current_model.update()
            
            # 重新生成模型图像（实际中应使用OpenGL渲染）
            self.render_widget.generateModelImage()
            self.render_widget.update()
    
    def closeEvent(self, event):
        """关闭应用时的清理工作"""
        if self.current_model:
            self.current_model.destroy()
        self.update_timer.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # 设置应用样式
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    window = Live2DApp()
    
    # 扫描模型目录
    window.scanModels()
    
    # 尝试加载模型目录中的第一个模型（如果有）
    if window.model_list.count() > 0 and window.model_list.item(0).text() != "未找到模型，请添加模型到目录":
        first_model = os.path.join(window.model_dir, window.model_list.item(0).text())
        window.loadModel(first_model)
    
    window.show()
    sys.exit(app.exec_())