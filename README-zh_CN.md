# NDSS Papers Spider

该程序用于爬取 NDSS (Network and Distributed System Security Symposium) 会议论文。

## 功能特点

- 支持爬取指定年份的 NDSS 会议论文
- 下载论文 PDF 和 演示幻灯片（Video 可自行添加，在论文详情处添加 button 即可）
- 将论文信息保存为 CSV 文件用于索引、查询等
- 支持断点续传（避免重复下载）

## 使用方法

1. 运行程序：

```bash
python spider.py
```

2. 输入要爬取的年份（如：2024）

3. 程序会自动：
   - 创建目录结构
   - 获取论文列表
   - 下载论文和幻灯片
   - 生成 CSV 文件

## 目录结构

ndss{year}/
├── papers/ # 存放论文 PDF
├── slides/ # 存放演示幻灯片
└── paper_list.csv # 论文信息列表

## CSV 文件格式

paper_list.csv 包含以下列：

- index: 序号（从 1 开始）
- title: 论文标题
- authors: 作者列表
- cycle: 论文所属周期（Summer/Fall）
- details_url: 论文详情页面 URL

## 依赖说明

```
requests>=2.31.0
beautifulsoup4>=4.12.2
pandas>=2.1.0
lxml>=4.9.3
```

## 注意事项

1. 建议使用 Python 3.8 或更高版本
2. 下载过程中会自动跳过已存在的文件

## 错误处理

程序包含完整的错误处理机制：

- 网络连接错误
- 文件下载失败
- 解析错误
- 文件保存错误

错误会被记录并显示，但不会中断程序的执行。

## 代码结构

- `NDSSSpider` 类：主要爬虫类
  - `__init__`: 初始化配置和路径
  - `create_dirs`: 创建必要的目录
  - `sanitize_filename`: 清理文件名
  - `get_paper_list`: 获取论文列表
  - `download_file`: 下载文件
  - `get_paper_details`: 获取论文详情
  - `save_paper_list_to_csv`: 保存 CSV 文件
  - `run`: 主运行函数
