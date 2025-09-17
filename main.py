import sys
import os
import argparse
from fontTools.ttLib import TTFont
from pathlib import Path
from io import BytesIO
import re
import wordcloud
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPlainTextEdit, QPushButton, QLabel, 
                               QFileDialog, QMessageBox, QSizePolicy, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

translation_dict = {
    "zh": {
        "词云生成器": "词云生成器",
        "请输入词语，每行一个...": "请输入词语，每行一个...",
        "得意黑": "得意黑", 
        "默认": "默认",
        "+ 添加新字体": "+ 添加新字体",
        "生成": "生成",
        "下载": "下载",
        "词云预览":"词云预览",
        "选择字体":"选择字体",
        "重复选项":"重复选项",
        "该选项已存在!":"该选项已存在!",
        "警告":"警告",
        "请输入文本内容!":"请输入文本内容!",
        "没有有效的词语输入!":"没有有效的词语输入!",
        "错误":"错误",
        "生成词云时出错":"生成词云时出错",
        "请先生成词云!":"请先生成词云!",
        "保存词云图片":"保存词云图片",
        "词云已保存到":"词云已保存到",
        "保存图片时出错":"保存图片时出错"
    },
    "en": {
        "词云生成器": "Word Cloud Generator",
        "请输入词语，每行一个...": "Enter words, one per line...",
        "得意黑": "Smiley Sans",
        "默认": "Default",
        "+ 添加新字体": "+ Add New Font",
        "生成": "Generate",
        "下载": "Download",
        "词云预览": "Preview",
        "选择字体": "Select Font",
        "重复选项": "Duplicate Option", 
        "该选项已存在!": "This option already exists!",
        "警告": "Warning",
        "请输入文本内容!": "Please enter text content!",
        "没有有效的词语输入!": "No valid words entered!",
        "错误": "Error",
        "生成词云时出错": "Error generating word cloud",
        "请先生成词云!": "Please generate a word cloud first!",
        "保存词云图片": "Save Word Cloud Image",
        "词云已保存到": "Word cloud saved to",
        "保存图片时出错": "Error saving image"
    }
}

def tr(lang, key):
    try:
        return translation_dict[lang][key]
    except:
        return key

def get_font_name(font_path):
    """获取字体的真正名称"""
    try:
        font = TTFont(font_path)
        # 获取字体名称（通常从name表的英文字体名或中文字体名获取）
        for record in font['name'].names:
            if record.nameID == 4:
                return record.string.decode('utf-16-be') if hasattr(record.string, 'decode') else str(record.string)
        return os.path.basename(font_path)  # 如果获取失败，返回文件名
    except:
        return os.path.basename(font_path)  # 如果读取失败，返回文件名

def remove_duplicate_fonts_by_name(font_list):
    """根据字体名称去重"""
    seen_names = set()
    unique_fonts = []
    
    for font_path in font_list:
        try:
            font_name = get_font_name(font_path)
            if font_name not in seen_names:
                seen_names.add(font_name)
                unique_fonts.append(font_path)
        except:
            # 如果无法读取字体信息，保留该字体
            unique_fonts.append(font_path)
    
    return unique_fonts

def get_fonts(lang="zh"):
    font_extensions = {'.ttf', '.otf'}
    fonts_path = Path("C:/Windows/Fonts")
    
    fonts_list = [
        str(file) for file in fonts_path.rglob('*') 
        if file.suffix.lower() in font_extensions
    ]

    if check_file_exists("./SMILEYSANS.TTF"):
        fonts_list.append(tr(lang, "得意黑"))

    return remove_duplicate_fonts_by_name(fonts_list)

def check_file_exists(file_path):
    return Path.exists(Path(file_path)) and Path.is_file(Path(file_path))

class WordCloudGenerator(QMainWindow):
    def __init__(self,lang):
        super().__init__()
        self.wordcloud_image = None
        self.last_valid_index = 0
        self.lang = lang
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(tr(lang, "词云生成器"))
        self.setGeometry(100, 100, 800, 600)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel(tr(lang, "词云生成器"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 输入框
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(tr(lang, "请输入词语，每行一个..."))
        self.text_edit.setMinimumHeight(200)
        main_layout.addWidget(self.text_edit)
        
        # 字体选择
        self.font_combo = QComboBox()
        self.font_combo.addItems(get_fonts(lang) + [tr(lang, "默认"), tr(lang, "+ 添加新字体")])
        self.font_combo.currentIndexChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.font_combo)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 生成按钮
        self.generate_button = QPushButton(tr(lang, "生成"))
        self.generate_button.clicked.connect(self.generate_wordcloud)
        self.generate_button.setFixedSize(100, 40)
        button_layout.addWidget(self.generate_button)
        
        button_layout.addSpacing(20)
        
        # 下载按钮（初始禁用）
        self.download_button = QPushButton(tr(lang, "下载"))
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
        self.image_label.setText(tr(lang, "词云预览"))
        self.image_label.hide()
        main_layout.addWidget(self.image_label)
        
        # 添加弹性空间使所有元素居中
        main_layout.addStretch(1)

    def on_selection_changed(self, index):
        if self.font_combo.itemText(index) == tr(lang, "+ 添加新字体"):
            self.font_combo.setCurrentIndex(self.last_valid_index)
            text, ok = QFileDialog.getOpenFileName(
                self,
                tr(lang, "选择字体"),
                str(Path.home()),
                "TTF Fonts (*.ttf);;OTF Fonts (*.otf);;All Files (*)"
            )
            if ok and text.strip():
                if text.strip() not in [self.font_combo.itemText(i) for i in range(self.font_combo.count() - 1)]:
                    self.font_combo.insertItem(self.font_combo.count() - 1, text.strip())
                    self.font_combo.setCurrentText(text.strip())
                    self.last_valid_index = self.font_combo.currentIndex()
                else:
                    QMessageBox.warning(self, tr(lang, "重复选项"), tr(lang, "该选项已存在!"))
        else:
            self.last_valid_index = index

    def generate_wordcloud(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, tr(lang, "警告"), tr(lang, "请输入文本内容!"))
            return
        
        # 处理文本，每行作为一个词语
        lines = text.split('\n')
        word_freq = {}
        for line in lines:
            line = line.strip()
            if line:
                word_freq[line] = word_freq.get(line, 0) + 1
        
        if not word_freq:
            QMessageBox.warning(self, tr(lang, "警告"), tr(lang, "没有有效的词语输入!"))
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
            font = self.font_combo.currentText()
            # 创建词云对象
            wc = wordcloud.WordCloud(
                width=800,
                height=600,
                background_color='white',
                font_path=("./SMILEYSANS.TTF" if font == tr(lang, "得意黑") else (None if font == tr(lang, "默认") else font)),
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
            QMessageBox.critical(self, tr(lang, "错误"), f"{tr(lang, '生成词云时出错')}:{str(e)}")

    def download_wordcloud(self):
        if self.wordcloud_image is None:
            QMessageBox.warning(self, tr(lang, "警告"), tr(lang, "请先生成词云!"))
            return
        
        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr(lang, "保存词云图片"), 
            str(Path.home() / "wordcloud.png"),
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.wordcloud_image.save(file_path)
                QMessageBox.information(self, tr(lang, "成功"), f"{tr(lang, '词云已保存到')}:{file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr(lang, "错误"), f"{tr(lang, '保存图片时出错')}:{str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a word cloud.')
    parser.add_argument('-l', '--lang', '--language',
                        choices=['zh', 'en'], # 只允许这两种选择
                        default='zh',         # 默认中文
                        help='Language for the UI (zh: 中文, en: English). Default is zh.')

    args, unknown = parser.parse_known_args()
    lang = args.lang
    app = QApplication(sys.argv)
    window = WordCloudGenerator(lang)
    window.show()
    sys.exit(app.exec())
