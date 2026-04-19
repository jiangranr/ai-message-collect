AI Daily Pulse - 银行后台业务AI赋能助手

一个自动化每日AI资讯与金融AI应用案例搜集工具，为银行后台业务人员提供AI赋能业务建议。

功能特性





📰 多平台AI资讯抓取（Twitter、Reddit、Hacker News、TechCrunch等）



💰 金融AI应用案例聚焦（未道客、雷锋网、36氪等）



🎯 推特KOL技术博客推荐提取



💡 基于LLM生成业务赋能建议



📱 微信自动推送



💾 SQLite本地存储，支持历史复盘

快速开始

1. 安装依赖

pip install -r requirements.txt

2. 配置环境变量

复制 .env.example 到 .env 并配置：

cp .env.example .env

3. 修改配置文件

编辑 config.yaml 配置数据源和参数

4. 运行

python src/main.py

项目结构

ai-daily-pulse/
├── src/
│   ├── config/          # 配置模块
│   ├── fetcher/        # 数据抓取
│   ├── processor/      # 数据处理
│   ├── generator/      # LLM生成
│   ├── storage/        # 数据存储
│   ├── formatter/      # 格式化
│   ├── publisher/      # 推送
│   └── main.py         # 入口
├── config.yaml         # 配置文件
├── .env                # 环境变量
└── requirements.txt    # 依赖

License

MIT
