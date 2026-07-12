# ⚽ 五大联赛转会日报 · 每日自动推送

每天北京时间 **09:00** 自动抓取英超、西甲、德甲、意甲、法甲五大联赛最新转会动态，整理成结构化 Markdown 表格，通过钉钉机器人推送到你的手机。

**完全免费** ✅ 无需 API Key ✅ 只需 GitHub 账号

## 工作流程

```
每天 09:00 UTC+8
    ↓
GitHub Actions 定时触发
    ↓
爬取 Transfermarkt 最新转会数据（✅ 已完成）
    ↓
按联赛分类，格式化 Markdown 表格
    ↓
通过钉钉机器人 Webhook 推送到钉钉群
```

## 配置方法

### 1. 创建 GitHub 仓库

在 GitHub 新建一个仓库（例如 `daily-transfer-briefing`），把本代码推上去。

### 2. 添加 GitHub Secrets

在仓库 **Settings → Secrets and variables → Actions** 中添加：

| Name | Value |
|------|-------|
| `DINGTALK_WEBHOOK_URL` | 你的钉钉机器人 Webhook 地址 |
| `DINGTALK_SECRET` | 钉钉机器人的加签密钥（如果开启了加签） |

### 3. 获取钉钉 Webhook

1. 在钉钉群 → 群设置 → 智能群助手 → 添加机器人
2. 选择 **自定义（通过 Webhook 接入）**
3. 安全设置选择 **加签**，复制 Secret
4. 复制 Webhook URL（格式：`https://oapi.dingtalk.com/robot/send?access_token=xxx`）

### 4. 手动触发测试

在 Actions 页面选择 **⚽ 每日转会简报推送 → Run workflow**，确认钉钉群收到消息。

### 5. 自动生效

确认成功后，每天早上 **09:00** 会自动推送。

## 日报内容

| 列 | 说明 |
|:--:|:----:|
| 球员 | 英文名（中文名） |
| 方向 | 原俱乐部 → 新俱乐部 |
| 转会费 | 金额 / 免签 / 租借 |
| 状态 | ✅ 已完成 |

## 项目结构

```
daily-transfer-briefing/
├── .github/workflows/daily-briefing.yml   # GitHub Actions 定时任务（UTC 01:00）
├── src/
│   ├── scraper.py     # Transfermarkt 数据爬虫
│   ├── formatter.py   # Markdown 简报格式化
│   ├── notifier.py    # 钉钉机器人推送
│   └── players.py     # 球员中英文名映射表（120+ 名将）
├── main.py            # 入口
├── requirements.txt   # Python 依赖
└── README.md
```

## 数据来源

- [Transfermarkt - 最新转会](https://www.transfermarkt.com/statistik/neuestetransfers) — 全球最权威的转会数据平台
- 只包含 **已完成转会**（✅），数据准确

## 费用

| 项目 | 费用 |
|------|:----:|
| GitHub Actions | 免费（2000分钟/月，此任务约1分钟/天） |
| 钉钉机器人 | 免费 |
| 数据来源 | 免费 |
| **总计** | **完全免费** 🆓 |

## 本地运行

```bash
pip install -r requirements.txt

# 设置环境变量
set DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
set DINGTALK_SECRET=SECxxx

# 运行
python main.py
```
