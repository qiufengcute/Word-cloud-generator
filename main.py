import sys
import os
import argparse
from fontTools.ttLib import TTFont
from pathlib import Path
from io import BytesIO
import re
import wordcloud
import jieba
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPlainTextEdit, QPushButton, QLabel, 
                               QFileDialog, QMessageBox, QSizePolicy, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QIcon

__version__ = "1.2.0"

translation_dict = {
    "zh": {
        "词云生成器": "词云生成器",
        "请输入词语，每行一个...": "请输入词语，每行一个...",
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
    import re
    
    def clean_font_name(name):
        """清理字体名称中的特殊字符"""
        if not name:
            return ""
        # 移除控制字符和特殊符号
        name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', name)
        # 移除常见的特殊符号（但保留中文、英文、数字）
        name = re.sub(r'[^\u4e00-\u9fa5\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\w\s\-_.()]', '', name)
        # 移除多余的空白字符
        name = re.sub(r'\s+', ' ', name).strip()
        return name
    
    try:
        font = TTFont(font_path)
        # 尝试获取中文字体名称
        for record in font['name'].names:
            # 优先查找中文字体名称 (nameID=4 是完整字体名称)
            if record.nameID == 4:
                # Windows 平台中文编码
                if record.platformID == 3 and record.platEncID in (1, 10):  # Windows Unicode
                    try:
                        name = record.string.decode('utf-16-be').strip('\x00')
                        if name and not name.startswith('?') and name.strip():  # 检查是否是有效名称
                            cleaned_name = clean_font_name(name)
                            if cleaned_name:
                                return cleaned_name
                    except:
                        pass
                # Macintosh 平台
                elif record.platformID == 1:
                    try:
                        name = record.string.decode('mac_roman').strip('\x00')
                        if name and not name.startswith('?') and name.strip():
                            cleaned_name = clean_font_name(name)
                            if cleaned_name:
                                return cleaned_name
                    except:
                        pass
                # 其他编码尝试
                else:
                    encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin1']
                    for encoding in encodings:
                        try:
                            name = record.string.decode(encoding).strip('\x00')
                            if name and not name.startswith('?') and name.strip():
                                cleaned_name = clean_font_name(name)
                                if cleaned_name:
                                    return cleaned_name
                        except:
                            continue
        
        # 如果没有找到完整字体名称，尝试查找字体家族名称 (nameID=1)
        for record in font['name'].names:
            if record.nameID == 1:
                # Windows 平台中文编码
                if record.platformID == 3 and record.platEncID in (1, 10):  # Windows Unicode
                    try:
                        name = record.string.decode('utf-16-be').strip('\x00')
                        if name and not name.startswith('?') and name.strip():
                            cleaned_name = clean_font_name(name)
                            if cleaned_name:
                                return cleaned_name
                    except:
                        pass
                # Macintosh 平台
                elif record.platformID == 1:
                    try:
                        name = record.string.decode('mac_roman').strip('\x00')
                        if name and not name.startswith('?') and name.strip():
                            cleaned_name = clean_font_name(name)
                            if cleaned_name:
                                return cleaned_name
                    except:
                        pass
                # 其他编码尝试
                else:
                    encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin1']
                    for encoding in encodings:
                        try:
                            name = record.string.decode(encoding).strip('\x00')
                            if name and not name.startswith('?') and name.strip():
                                cleaned_name = clean_font_name(name)
                                if cleaned_name:
                                    return cleaned_name
                        except:
                            continue
        
        # 如果还是获取不到，返回文件名（去掉扩展名）
        font_filename = os.path.basename(font_path)
        name_without_ext = os.path.splitext(font_filename)[0]
        cleaned_name = clean_font_name(name_without_ext)
        return cleaned_name if cleaned_name else "Unknown Font"
    except Exception as e:
        # 如果读取失败，返回文件名（去掉扩展名）
        try:
            font_filename = os.path.basename(font_path)
            name_without_ext = os.path.splitext(font_filename)[0]
            cleaned_name = clean_font_name(name_without_ext)
            return cleaned_name if cleaned_name else "Unknown Font"
        except:
            return "Unknown Font"

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

def get_fonts():
    font_extensions = {'.ttf', '.otf'}
    fonts_path = Path("C:/Windows/Fonts")
    
    fonts_list = [
        str(file) for file in fonts_path.rglob('*') 
        if file.suffix.lower() in font_extensions
    ]

    if check_file_exists("./SMILEYSANS.TTF"):
        fonts_list.append("./SMILEYSANS.TTF")

    fonts_list = remove_duplicate_fonts_by_name(fonts_list)
    res = {}
    for i in fonts_list:
        res[get_font_name(i)] = i

    return res

def check_file_exists(file_path):
    return Path.exists(Path(file_path)) and Path.is_file(Path(file_path))

class WordCloudGenerator(QMainWindow):
    def __init__(self, lang="zh"):
        super().__init__()
        self.lang = lang
        self.font_path_index = {}
        self.wordcloud_image = None
        self.last_valid_index = 0
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(tr(self.lang, "词云生成器"))
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口图标
        icon_path = "./icon.ico"
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        # 标题
        title_label = QLabel(tr(self.lang, "词云生成器"))
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # VERSION文本
        self.top_right_text = QLabel(f"VERSION {__version__}")
        self.top_right_text.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        title_layout.addStretch()
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.top_right_text)
        
        main_layout.addLayout(title_layout)
        
        # 输入框
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(tr(self.lang, "请输入词语，每行一个..."))
        self.text_edit.setMinimumHeight(200)
        main_layout.addWidget(self.text_edit)

        # 字体
        self.font_path_index = get_fonts(self.lang)
        self.font_path_index[tr(self.lang, "默认")] = None

        # 字体选择
        self.font_combo = QComboBox()
        self.font_combo.addItems(self.font_path_index.keys())
        # 添加"添加新字体"选项
        self.font_combo.addItem(tr(self.lang, "+ 添加新字体"))
        self.font_combo.currentIndexChanged.connect(self.on_selection_changed)
        main_layout.addWidget(self.font_combo)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 分割文本按钮
        self.split_button = QPushButton(tr(self.lang, "分割文本"))
        self.split_button.clicked.connect(self.split_text)
        self.split_button.setFixedSize(100, 40)
        button_layout.addWidget(self.split_button)
        
        button_layout.addSpacing(20)
        
        # 生成按钮
        self.generate_button = QPushButton(tr(self.lang, "生成"))
        self.generate_button.clicked.connect(self.generate_wordcloud)
        self.generate_button.setFixedSize(100, 40)
        button_layout.addWidget(self.generate_button)
        
        button_layout.addSpacing(20)
        
        # 下载按钮（初始禁用）
        self.download_button = QPushButton(tr(self.lang, "下载"))
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
        self.image_label.setText(tr(self.lang, "词云预览"))
        self.image_label.hide()
        main_layout.addWidget(self.image_label)
        
        # 添加弹性空间使所有元素居中
        main_layout.addStretch(1)

    def on_selection_changed(self, index):
        if self.font_combo.itemText(index) == tr(self.lang, "+ 添加新字体"):
            self.font_combo.setCurrentIndex(self.last_valid_index)
            text, ok = QFileDialog.getOpenFileName(
                self,
                tr(self.lang, "选择字体"),
                str(Path.home()),
                "TTF Fonts (*.ttf);;OTF Fonts (*.otf);;All Files (*)"
            )
            if ok and text.strip():
                # 获取字体的真实名称
                font_name = get_font_name(text.strip())
                if font_name not in self.font_path_index:
                    self.font_combo.insertItem(self.font_combo.count() - 1, font_name)
                    self.font_path_index[font_name] = text.strip()
                    self.font_combo.setCurrentText(font_name)
                    self.last_valid_index = self.font_combo.currentIndex()
                else:
                    QMessageBox.warning(self, tr(self.lang, "重复选项"), tr(self.lang, "该选项已存在!"))
        else:
            self.last_valid_index = index

    def generate_wordcloud(self):
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, tr(self.lang, "警告"), tr(self.lang, "请输入文本内容!"))
            return
        
        # 处理文本，每行作为一个词语
        lines = text.split('\n')
        word_freq = {}
        for line in lines:
            line = line.strip()
            if line:
                word_freq[line] = word_freq.get(line, 0) + 1
        
        if not word_freq:
            QMessageBox.warning(self, tr(self.lang, "警告"), tr(self.lang, "没有有效的词语输入!"))
            return

        QApplication.setOverrideCursor(Qt.WaitCursor)
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
                font_path=self.font_path_index[font],
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
            QMessageBox.critical(self, tr(self.lang, "错误"), f"{tr(self.lang, '生成词云时出错')}:{str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def download_wordcloud(self):
        if self.wordcloud_image is None:
            QMessageBox.warning(self, tr(self.lang, "警告"), tr(self.lang, "请先生成词云!"))
            return
        
        # 获取保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            tr(self.lang, "保存词云图片"), 
            str(Path.home() / "wordcloud.png"),
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg);;All Files (*)"
        )
        
        if file_path:
            try:
                self.wordcloud_image.save(file_path)
                QMessageBox.information(self, tr(self.lang, "成功"), f"{tr(self.lang, '词云已保存到')}:{file_path}")
            except Exception as e:
                QMessageBox.critical(self, tr(self.lang, "错误"), f"{tr(self.lang, '保存图片时出错')}:{str(e)}")

    def split_text(self):
        """分割文本功能"""
        # 获取输入框中的文本
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, tr(self.lang, "警告"), tr(self.lang, "请输入文本内容!"))
            return
        
        # 去除隐藏字符
        cleaned_text = re.sub(r'[\x00-\x1f\x7f-\x9f\u200b\u200c\u200d\u200e\u200f\ufeff\u202a-\u202e]', '', text)
        
        # 分割文本
        lines = []
        
        # 检查是否包含中文
        if re.search(r'[\u4e00-\u9fff]', cleaned_text):
            # 使用jieba进行中文分词
            words = jieba.lcut(cleaned_text)
            lines = [word.strip() for word in words if word.strip()]
        else:
            # 对于其他语言，使用正则表达式分割
            # 按空格、标点符号等分割
            import nltk
            try:
                # 尝试使用nltk进行分词
                tokens = nltk.word_tokenize(cleaned_text)
                lines = [token.strip() for token in tokens if token.strip()]
            except:
                # 如果nltk不可用，使用简单的正则表达式分割
                tokens = re.findall(r'\b\w+\b|[^\w\s]', cleaned_text, re.UNICODE)
                lines = [token.strip() for token in tokens if token.strip()]
        
        # 将分割后的文本按行输入到输入框
        self.text_edit.setPlainText('\n'.join(lines))

    def closeEvent(self, event):
        """窗口关闭事件"""
        event.accept()

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
