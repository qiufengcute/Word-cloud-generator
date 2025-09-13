# Word-cloud-generator

一个开箱即用的桌面应用程序，轻松将文本转换为美观的词云图。

**当前版本：** `v1.0.0` | **发布日期：** `2025-09-12` | **开发者：** `Qiufeng`

---
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Stable-brightgreen.svg)
![Download](https://img.shields.io/badge/Download-Latest_Release-success.svg)

---

## 📁 目录
- [✨ 1. 软件简介](#-1-软件简介)
- [📥 2. 下载与安装](#-2-下载与安装)
- [🎯 3. 使用指南](#-3-使用指南)
- [⚙️ 4. 技术架构](#️-4-技术架构)

---

## ✨ 1. 软件简介

**WordCloud Generator** 是一款轻量级、跨平台的桌面词云生成工具。您无需任何编程知识，只需输入词语，即可一键生成专业的词云图并保存为图片。

**核心特点：**
- **即开即用**：下载后直接运行，无需安装复杂环境。
- **极致简单**：清晰的界面，专注于输入和生成。
- **高质量输出**：生成高清词云图片，支持PNG/JPEG格式。
- **智能稳定**：自动处理输入文本中的异常字符，防止生成失败。

---

## 📥 2. 下载与安装

1.  前往项目的 **[Release发布页面](https://github.com/qiufengcute/Word-cloud-generator/releases)**。
2.  下载最新版本（`v1.0.0`）的exe文件（`Windows-x64.exe`）。
3.  运行下载的exe文件。

> **⚠️ 注意**：目前仅支持Windows系统。

---

## 🎯 3. 使用指南

使用流程非常简单，只需三步：

1.  **输入文本**：
    在软件界面的文本框中输入词语，**每行一个**。
    > **示例**：
    > `Python`
    > `WordCloud`
    > `GUI`
    > `软件`

2.  **生成词云**：
    点击 **`生成`** 按钮。稍等片刻，下方预览区就会显示出生成的词云图。

3.  **保存图片**：
    生成成功后，点击 **`下载`** 按钮，选择您想保存的位置和图片格式（PNG/JPEG），即可将词云图保存到您的电脑上。

---

## ⚙️ 4. 技术架构

本软件使用以下技术打包而成，用户无需关心这些细节，仅供开发者或感兴趣的朋友参考。

| 组件 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **核心语言** | Python 3.10+ | 应用程序逻辑 |
| **GUI框架** | PySide6 (Qt for Python) | 构建现代、流畅的桌面界面 |
| **词云引擎** | wordcloud + matplotlib | 核心词云生成算法 |
| **打包工具** | PyInstaller | 将Python代码打包成独立可执行文件 |
| **文本处理** | 正则表达式 (`re`) | 净化输入，过滤零宽字符等 |

---

**License:** 本项目采用 **MIT许可证**，您可以自由地使用、修改和分发。
