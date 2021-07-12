# -*- coding:utf-8 -*-
import re
import sys
from threading import Thread
import random
import subprocess
import socket
from PySide2.QtGui import QColor, QFont, QIcon, QKeySequence, QPixmap
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QApplication,  QGridLayout, QGroupBox, QInputDialog, QLabel, QLineEdit, QMainWindow, QMessageBox, QPushButton, QStyleFactory,  QVBoxLayout
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtCore import Qt

appname = '''EasyPing'''
appmessage = '''检测局域网内IP地址的使用情况'''
author = '''ordinary-student'''
version = '''v4.1.0'''
last_update = '''2021-07-12'''


class EasyPing(QMainWindow):
    '''EasyPing类'''
    _ping_signal = Signal(bool, str)

    def __init__(self, app: QApplication):
        '''构造函数'''
        super(EasyPing, self).__init__()
        self.app = app

        # 加载界面ui
        self.initUI()
        # Ping请求数
        self.ping_count = 3
        # 连接信号槽
        self._ping_signal.connect(self.set_ui)

    def initUI(self):
        '''加载界面ui'''
        # 多网卡情况下获取本地IP
        ips = socket.gethostbyname_ex(socket.gethostname())[2]
        # 最后一个IP，一般为无线网卡IP
        self.localip = ips[-1]
        # 窗口标题
        self.setWindowTitle('EasyPing--'+str(ips))
        # 设置窗口图标
        self.setWindowIcon(self.generateIcon())
        # 窗口大小
        self.resize(1000, 700)
        # 最小大小
        self.setMinimumSize(700, 500)
        # 窗口居中
        self.center()

        self.widget_easyping = QWidget(self)
        # 参数设置区域
        self.groupBox_setting = QGroupBox('设置待检测的IP范围', self.widget_easyping)

        # 起始IP
        self.lineEdit_startIP = QLineEdit(self.groupBox_setting)
        # 改变字体和大小
        font = QFont("微软雅黑", 12, QFont.Bold)
        self.lineEdit_startIP.setFont(font)
        # IP最后一点的索引
        last_point_index = self.localip.rindex('.')
        # 填写起始IP
        self.lineEdit_startIP.setText(self.localip[0:last_point_index]+'.0')
        # 绑定事件-自动填写结束IP
        self.lineEdit_startIP.textChanged.connect(self.auto_fill_endip)

        # 横条标签
        self.label_to = QLabel(' -- ')

        # 结束IP
        self.lineEdit_endIP = QLineEdit(self.groupBox_setting)
        self.lineEdit_endIP.setFont(font)
        # 填写结束IP
        self.lineEdit_endIP.setText(self.localip[0:last_point_index]+'.255')

        # ping按钮
        self.pushButton_ping = QPushButton(
            'Ping', self.groupBox_setting)
        self.pushButton_ping.setStyleSheet(
            "QPushButton:hover{color: white;background:green}")
        self.pushButton_ping.setShortcut(QKeySequence('ENTER'))
        self.pushButton_ping.clicked.connect(self.start_ping)
        # setting按钮
        self.pushButton_setting = QPushButton(
            '设置', self.groupBox_setting)
        self.pushButton_setting.setStyleSheet(
            "QPushButton:hover{color: blue}")
        self.pushButton_setting.setShortcut(QKeySequence('F2'))
        self.pushButton_setting.clicked.connect(self.ping_setting)
        # 关于按钮
        self.pushButton_about = QPushButton(
            '关于', self.groupBox_setting)
        self.pushButton_about.setStyleSheet(
            "QPushButton:hover{color: green}")
        self.pushButton_about.setShortcut(QKeySequence('F1'))
        self.pushButton_about.clicked.connect(self.about)

        # 水平布局
        self.horizontalLayout_ep = QHBoxLayout(self.groupBox_setting)
        self.horizontalLayout_ep.setSpacing(10)
        self.horizontalLayout_ep.addWidget(self.lineEdit_startIP)
        self.horizontalLayout_ep.addWidget(self.label_to)
        self.horizontalLayout_ep.addWidget(self.lineEdit_endIP)
        self.horizontalLayout_ep.addWidget(self.pushButton_ping)
        self.horizontalLayout_ep.addWidget(self.pushButton_setting)
        self.horizontalLayout_ep.addWidget(self.pushButton_about)

        # IP检测结果区域
        self.groupBox_ipstatus = QGroupBox('IP检测结果', self.widget_easyping)
        # 网格布局
        self.gridLayout_ip = QGridLayout(self.groupBox_ipstatus)
        self.gridLayout_ip.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_ip.setSpacing(5)
        # IP标签列表
        self.iplabel_list = []
        # 索引
        list_index = 0
        # 循环添加
        for i in range(1, 17):
            for j in range(1, 17):
                # 创建标签
                label = QLabel(str(list_index), self.groupBox_ipstatus)
                # 最小尺寸
                label.setMinimumSize(32, 15)
                # 背景色
                label.setStyleSheet("background-color: rgb(203, 203, 203);")
                # 居中
                label.setAlignment(Qt.AlignCenter)
                # 加入列表
                self.iplabel_list.append(label)
                # 添加控件
                self.gridLayout_ip.addWidget(label, i-1, j-1, 1, 1)
                list_index = list_index + 1

        # 本页垂直布局
        self.verticalLayout_ep = QVBoxLayout(self.widget_easyping)
        self.verticalLayout_ep.addWidget(self.groupBox_setting)
        self.verticalLayout_ep.addWidget(self.groupBox_ipstatus)
        self.verticalLayout_ep.setStretch(0, 1)
        self.verticalLayout_ep.setStretch(1, 20)

        # 设置中央容器
        self.setCentralWidget(self.widget_easyping)

    def generateIcon(self) -> QIcon:
        '''生成图标'''
        pixmap = QPixmap(256, 256)
        # 图片颜色
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        pixmap.fill(QColor(r, g, b))
        return QIcon(pixmap)

    def center(self):
        '''窗口居中显示'''
        screen = self.app.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def about(self):
        '''关于'''
        # 显示弹窗
        QMessageBox.about(self, f'关于{appname}',
                          "{}<br>{}<br>author：<a href='https://github.com/ordinary-student'>{}</a><br>版本：{}<br>Last-Update：{}".format(appname, appmessage, author, version, last_update))

    def is_ip_legal(self, ip: str) -> bool:
        '''检测IP是否合法'''
        # 检查IP地址是否合法
        pattern = r"((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))$)"
        return re.match(pattern, ip)

    def auto_fill_endip(self):
        '''自动填写结束IP'''
        # 获取起始IP
        startip = self.lineEdit_startIP.text()
        # 检查IP地址是否合法
        self.ipislegal = self.is_ip_legal(startip)
        # 判断
        if self.ipislegal:  # 合法
            # 分割
            ip_list = startip.split('.')
            # 改写
            ip_list[3] = '255'
            # 组合
            endip = '.'.join(ip_list)
            # 填写
            self.lineEdit_endIP.setText(endip)
        else:
            self.lineEdit_endIP.setText('')

    def ping_setting(self):
        '''设置Ping请求数'''
        num, ok = QInputDialog.getInt(
            self, '设置', '输入Ping请求数：', self.ping_count, 1, 100, 1)
        if ok:
            self.ping_count = num

    def reset_ui(self):
        ''' 初始化窗口IP窗格为灰色背景 '''
        for item in self.iplabel_list:
            item.setStyleSheet("background-color: rgb(203, 203, 203);")

    def set_ui(self, result: bool, ip: str):
        '''设置窗口颜色 result：线程ping的结果 ip：对应的IP地址'''
        # 获取索引
        index = int(ip.split('.')[3])
        # 判断结果
        if result:
            # 设置背景为绿色
            self.iplabel_list[index].setStyleSheet(
                "background-color: rgb(85, 170, 127);")
        else:
            # 设置背景为红色
            self.iplabel_list[index].setStyleSheet(
                "background-color: rgb(255, 142, 119);")

    def popen(self, cmd: str) -> tuple[str, str]:
        '''执行系统命令'''
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            # 执行命令
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True, startupinfo=startupinfo,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            result = process.stdout.read()
            process.stdout.close()
            error = process.stderr.read()
            process.stderr.close()

            # 输出运行结果
            # print(result)
            # 若程序没有异常，则只输出空行
            # print(error)
        except:
            return 'error', 'error'
        # 返回运行结果
        return result, error

    def is_ip_online(self, ip: str):
        '''检测IP是否在线'''
        # 命令
        cmd = "ping {} -n {} -w 600".format(ip, self.ping_count)
        # 执行命令
        result, error = self.popen(cmd)
        # 判断结果
        if result == 'error':
            # 出错
            # self.set_ui(False, ip)
            self._ping_signal.emit(False, ip)
        else:
            # 在线
            if 'TTL' in result.upper():
                # self.set_ui(True, ip)
                self._ping_signal.emit(True, ip)
            else:
                # self.set_ui(False, ip)
                self._ping_signal.emit(False, ip)

    def start_ping(self):
        '''开始Ping检测'''
        # 获取IP
        startip_str = self.lineEdit_startIP.text()
        endip_str = self.lineEdit_endIP.text()
        # 检查IP地址是否合法
        ipislegal = self.is_ip_legal(startip_str)
        ipislegal2 = self.is_ip_legal(endip_str)
        # 判断
        if ipislegal and ipislegal2:  # 合法
            # 初始化格子
            self.reset_ui()
            # 获取起始IP
            startip = startip_str.split('.')
            # 获取结束IP
            endip = endip_str.split('.')
            tmp_ip = startip
            # 多线程检测
            pthread_list = []
            for i in range(int(startip[3]), int(endip[3]) + 1):
                # 当前IP
                tmp_ip[3] = str(i)
                ip = '.'.join(tmp_ip)
                # 创建线程
                pthread_list.append(
                    Thread(target=self.is_ip_online, args=(ip,)))
            # 遍历启动线程
            for item in pthread_list:
                # 设置守护线程-主线程停止了，子线程也会停止
                item.setDaemon(True)
                item.start()
        else:
            # 显示弹窗
            QMessageBox.warning(self, '错误', 'IP地址不合法！')
            if not ipislegal:
                self.lineEdit_startIP.setFocus()
                self.lineEdit_startIP.selectAll()
            else:
                self.lineEdit_endIP.setFocus()
                self.lineEdit_endIP.selectAll()
            return


if __name__ == '__main__':
    # 创建应用
    app = QApplication(sys.argv)
    # 设置界面风格
    app.setStyle(QStyleFactory.create('Fusion'))
    # 创建窗口
    mainWindow = EasyPing(app)
    # 显示
    mainWindow.show()
    # 退出
    sys.exit(app.exec_())
