#!/usr/bin/env python3
"""
五大联赛转会简报生成器
"""
import os
from src.scraper import collect_transfer_news
from src.formatter import format_briefing
from src.notifier import send_briefing


def main():
    print("=" * 50)
    print("⚽ 五大联赛转会简报生成器")
    print("=" * 50)

    classified = collect_transfer_news()
    briefing = format_briefing(classified)

    print("\n" + "=" * 50)
    # 预览前几行
    preview_lines = briefing.split('\n')[:12]
    for line in preview_lines:
        print(line)
    print("...")
    print("=" * 50)

    # 推送
    success = send_briefing(briefing)
    if success:
        print("\n🎉 今日转会简报已成功推送到钉钉群！")
    else:
        print("\n⚠ 简报已生成但推送失败，检查 DINGTALK_WEBHOOK_URL 配置")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
