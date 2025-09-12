import sys
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPlainTextEdit, QPushButton, QLabel, 
                               QFileDialog, QMessageBox, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
import wordcloud
from io import BytesIO
import re

class WordCloudGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.wordcloud_image = None
        
    def initUI(self):
        self.setWindowTitle("词云生成器")
        self.setGeometry(100, 100, 800, 600)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("词云生成器")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 输入框
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText("请输入词语，每行一个...")
        self.text_edit.setMinimumHeight(200)
        main_layout.addWidget(self.text_edit)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 生成按钮
        self.generate_button = QPushButton("生成")
        self.generate_button.clicked.connect(self.generate_wordcloud)
        self.generate_button.setFixedSize(100, 40)
        button_layout.addWidget(self.generate_button)
        
        button_layout.addSpacing(20)
        
        # 下载按钮（初始禁用）
        self.download_button = QPushButton("下载")
        self.download_button.clicked.connect(self.download_wordcloud)
        self.download_button.setEnabled(False)
        self.download_button.setFixedSize(100, 40)
        button_layout.addWidget(self.download_button)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 图片预览
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(400, 300)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.image_label.setStyleSheet("border: 1px solid #ccc; background-color: #f8f8f8;")
        self.image_label.setText("词云预览")
        self.image_label.hide()
        main_layout.addWidget(self.image_label)
        
        # 添加弹性空间使所有元素居中
        main_layout.addStretch(1)
        
    def generate_wordcloud(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本内容！")
            return
        
        # 处理文本，每行作为一个词语
        lines = text.split('\n')
        word_freq = {}
        for line in lines:
            line = line.strip()
            if line:
                word_freq[line] = word_freq.get(line, 0) + 1
        
        if not word_freq:
            QMessageBox.warning(self, "警告", "没有有效的词语输入！")
            return
        
        # 生成词云
        try:
            # 净化文本
            clean_word_freq = {}
            # 编译正则表达式模式（只需一次，效率更高）
            control_chars_pattern = re.compile(r'[\x00-\x1f\x7f-\x9f\u200b\u200c\u200d\u200e\u200f\ufeff\u202a-\u202e]')

            # 遍历原始字典的每一个键值对
            for word, freq in word_freq.items():
                # 净化单词（键）
                clean_word = control_chars_pattern.sub('', word)
                # 将净化后的单词和原来的频率存入新字典
                clean_word_freq[clean_word] = clean_word_freq.get(clean_word, 0) + freq
            # 创建词云对象
            wc = wordcloud.WordCloud(
                width=800,
                height=600,
                background_color='white',
                font_path=("./SMILEYSANS.TTF" if (Path.exists(Path("./SMILEYSANS.TTF")) and Path.is_file(Path("./SMILEYSANS.TTF"))) else None),  # 如果自带字体存在则使用自带字体,否则使用默认字体
                colormap='viridis',
                prefer_horizontal=0.8  # 调整水平放置词的概率
            )
            
            # 生成词云
            wc.generate_from_frequencies(clean_word_freq)
            
            # 转换为QPixmap并显示
            img_buffer = BytesIO()
            wc.to_image().save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(img_buffer.getvalue())
            self.image_label.setPixmap(pixmap.scaled(
                400, 300, 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.image_label.show()
            
            # 保存生成的图像供下载使用
            self.wordcloud_image = wc.to_image()
            
            # 启用下载按钮
            self.download_button.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"生成词云时出错：{str(e)}")
    
    def download_wordcloud(self):
        if self.wordcloud_image is None:
            QMessageBox.warning(self, "警告", "请先生成词云！")
            return
        
        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存词云图片", 
            str(Path.home() / "wordcloud.png"),
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.wordcloud_image.save(file_path)
                QMessageBox.information(self, "成功", f"词云已保存到：{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存图片时出错：{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordCloudGenerator()
    window.show()
    sys.exit(app.exec())
