# Jyutping Transfer

**Version / 版本：1.0.0**

Jyutping Transfer is a desktop tool for annotating Cantonese lyrics with Jyutping. It converts Chinese lyrics into editable Jyutping tokens, highlights polyphonic characters, keeps local history and favorites, and exports annotated lyrics as PNG or PDF files.

Jyutping Transfer 是一个用于粤语歌词粤拼标注的桌面工具。它可以把中文歌词转换为可编辑的粤拼注音结果，提示多音字，保存本地历史记录与收藏，并支持导出 PNG 图片或 PDF 文件。

## Features / 功能特色

- Automatic Jyutping annotation for Cantonese lyrics.
- Polyphonic character detection with selectable pronunciations.
- Simplified/Traditional Chinese conversion through OpenCC.
- Local history and favorites powered by SQLite.
- Adjustable font, character spacing, and line spacing.
- Export annotated lyrics to high-resolution PNG or PDF.

- 自动为粤语歌词生成粤拼注音。
- 检测多音字，并可手动选择正确读音。
- 通过 OpenCC 支持简繁转换。
- 使用 SQLite 保存本地历史记录与收藏。
- 可调整字体、字间距和行距。
- 可将注音歌词导出为高清 PNG 或 PDF。

## Requirements / 环境要求

- Python 3.10 or later
- Windows is recommended for the bundled font paths used by PNG/PDF export

- Python 3.10 或更高版本
- 推荐在 Windows 上运行，以便使用导出功能中配置的系统字体路径

## Installation / 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If you use PowerShell and script execution is blocked, activate the environment with:

如果 PowerShell 阻止脚本执行，可改用：

```powershell
.\.venv\Scripts\Activate.ps1
```

## Usage / 使用方法

```bash
python main.py
```

Then paste or type Cantonese lyrics, choose the conversion/font/spacing options you need, and click **开始转换**. Click highlighted polyphonic characters to choose another Jyutping reading. After conversion, you can save the result to favorites or export it as PNG/PDF.

启动后粘贴或输入粤语歌词，按需要选择简繁转换、字体、字间距与行距，然后点击 **开始转换**。高亮的多音字可以点击并切换读音。转换完成后，可收藏结果，或导出为 PNG/PDF。

## Project Structure / 项目结构

```text
.
├── core/              # Conversion and SQLite data layer / 转换逻辑与 SQLite 数据层
├── export/            # PNG and PDF export modules / PNG 与 PDF 导出模块
├── ui/                # PySide6 desktop UI / PySide6 桌面界面
├── main.py            # Application entry point / 程序入口
└── requirements.txt   # Runtime dependencies / 运行依赖
```

## Local Data / 本地数据

The app creates `lyrics_data.db` in the project directory to store history and favorites. This file is ignored by Git because it contains local user data.

程序会在项目目录中创建 `lyrics_data.db`，用于保存历史记录和收藏。该文件属于本地用户数据，不会提交到 Git 仓库。

## Dependencies / 主要依赖

- PySide6
- ToJyutping
- opencc-python-reimplemented
- Pillow
- reportlab

## License / 许可证

No license has been specified yet. Add a license before distributing the project publicly.

暂未指定许可证。如需公开分发，建议先补充许可证文件。
