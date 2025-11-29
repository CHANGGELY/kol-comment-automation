# 评论区引流器（KOL 工具包）

- 目标：跨平台（YouTube/B 站/抖音）评论执行与视觉自动化监控。
- 特性：视觉 OCR 自动化、选择器自学习、拟人化交互、服务化架构、可配置环境。

## 快速开始
- 安装依赖：`pip install -r 评论区引流器/-2/requirements.txt`
- 安装浏览器：`python -m playwright install`
- 配置 `.env`（可选）：`ENABLE_HEADLESS=true`、`PROXY_SERVER=socks5://127.0.0.1:1080`

## 目录
- `-2/services/`：服务层（`browser_service.py`、`task_service.py`）
- `ghost_protocol/phase_2_task_executor/`：行为内核与任务执行器
- `-2/visual_automation/`：视觉核心与验证码模块

## 使用示例
- 在 `TaskService` 中：`run_comment_task({account_id, platform, video_id, content})`

## 开发规范
- 使用结构化日志与性能打点；异常采用专用类型。
- 统一依赖与环境变量；避免将敏感信息写入日志。

## 后续路线
- 完整验证码类型覆盖与数据驱动的选择器版本化。
- 单测覆盖率 80%+ 与 CI；最小化 E2E 验证。
