#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试爬虫"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, ".")
from src.scraper import fetch_tm_transfers, collect_transfer_news
from src.formatter import format_briefing

# 测试1: 原始数据
print("=" * 60)
print("测试1: 直接抓取 Transfermarkt")
print("=" * 60)
results = fetch_tm_transfers()
print("获取到 %d 条原始转会记录" % len(results))
for r in results[:10]:
    print("  [%s] %s: %s -> %s | %s" % (r['league'], r['player'], r['from_club'], r['to_club'], r['fee']))
if len(results) > 10:
    print("  ... 还有 %d 条" % (len(results)-10))

# 测试2: 分类数据
print()
print("=" * 60)
print("测试2: 分类结果")
print("=" * 60)
classified = collect_transfer_news()
for league in ["英超", "西甲", "德甲", "意甲", "法甲"]:
    items = classified.get(league, [])
    print("  %s: %d 条" % (league, len(items)))
print("  其他: %d 条" % len(classified.get("其他", [])))

# 测试3: 格式化结果
print()
print("=" * 60)
print("测试3: 格式化简报预览")
print("=" * 60)
briefing = format_briefing(classified)
print(briefing[:2000])
print()
print("=" * 60)
print("简报总长度: %d 字符" % len(briefing))
