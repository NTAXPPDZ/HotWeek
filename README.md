# GitHub热榜网页项目

一个自动获取并展示GitHub每周热榜项目的静态网页，通过GitHub Actions实现自动化更新，并通过GitHub Pages部署。

## 功能特性

- 📊 **自动获取数据**：每周自动获取GitHub热榜项目
- 🎨 **卡片式布局**：美观的卡片式UI设计
- 🔍 **筛选功能**：支持按编程语言筛选项目
- ⚡ **快速访问**：通过GitHub Pages部署，访问速度快
- 🤖 **完全自动化**：GitHub Actions定时更新数据

## 项目结构

```
HotWeek/
├── scripts/           # Python数据处理脚本
│   ├── fetch_trending.py    # 数据获取脚本
│   └── process_data.py     # 数据处理脚本
├── styles/            # 样式文件
│   └── main.css       # 主样式文件
├── data/              # 数据文件
│   └── trending.json # 热榜项目数据
├── index.html         # 主页面
├── .github/
│   └── workflows/     # GitHub Actions工作流
│       └── update.yml # 自动化更新配置
└── docs/              # 项目文档
    └── GitHub热榜网页/ # 详细设计文档
```

## 技术栈

- **前端**：HTML5 + CSS3 + JavaScript（原生）
- **数据获取**：Python + requests库
- **自动化**：GitHub Actions
- **部署**：GitHub Pages

## 使用说明

1. 访问部署后的GitHub Pages地址
2. 浏览GitHub热榜项目
3. 使用筛选功能按语言查看项目
4. 数据每周一凌晨自动更新

## 开发说明

### 本地开发

1. 克隆项目
2. 安装Python依赖：`pip install requests`
3. 运行数据获取脚本：`python scripts/fetch_trending.py`
4. 打开`index.html`查看效果

### 自动化部署

项目配置了GitHub Actions工作流，每周一凌晨自动：
- 获取最新的GitHub热榜数据
- 更新数据文件
- 重新部署到GitHub Pages

## 许可证

MIT License