# -*- coding: utf-8 -*-
"""把 src/ 中的章节片段包装成完整页面（统一侧边栏、目录、翻页）。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

NAV = [
    ("起点", [
        ("index", "00", "学习地图", "总览 · 路线 · 怎么用"),
    ]),
    ("第一部分 · 基础", [
        ("01-foundations", "01", "数学基础", "张量 · 微积分 · 概率与信息论"),
        ("02-ml-basics", "02", "机器学习基础", "任务范式 · 损失 · 评估"),
        ("03-neural-nets", "03", "神经网络与反向传播", "MLP · 链式法则 · 计算图"),
        ("04-training", "04", "训练与优化", "优化器 · 正则化 · 归一化"),
    ]),
    ("第二部分 · 核心架构", [
        ("05-cnn", "05", "卷积神经网络", "卷积 · 感受野 · ResNet"),
        ("06-sequence", "06", "序列模型", "RNN · LSTM · Seq2Seq"),
        ("07-transformer", "07", "注意力与 Transformer", "Self-Attention · 多头 · 位置编码"),
        ("08-pretraining", "08", "预训练与自监督", "语言模型 · 对比学习 · CLIP"),
    ]),
    ("第三部分 · 生成与决策", [
        ("09-generative", "09", "生成模型", "VAE · GAN · 扩散模型"),
        ("10-reinforcement", "10", "强化学习", "MDP · 策略梯度 · PPO"),
        ("11-gnn", "11", "图神经网络", "消息传递 · GCN · GAT"),
    ]),
    ("第四部分 · 大模型与工程", [
        ("12-llm", "12", "大模型与微调", "Scaling · LoRA · RLHF/DPO"),
        ("13-efficient", "13", "压缩与部署", "量化 · 蒸馏 · 推理服务"),
        ("14-engineering", "14", "工程实践", "数据 · 调试 · 复现 · 分布式"),
    ]),
    ("第五部分 · 应用与资源", [
        ("15-applications", "15", "应用领域", "视觉 · 语言 · 科学计算"),
        ("16-resources", "16", "学习路线与资源", "课程 · 论文 · 项目清单"),
    ]),
    ("第六部分 · 光学深度学习", [
        ("17-optics", "17", "光学中的深度学习",
         "相位恢复 · U-Net · 超表面 · 光子计算"),
    ]),
]

PAGES = [item for _, items in NAV for item in items]

TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{TITLE}} · 深度学习学习站</title>
<meta name="description" content="{{DESC}}">
<link rel="stylesheet" href="assets/site.css">
</head>
<body data-slug="{{SLUG}}">
<div class="layout">
<aside class="sidebar" id="sidebar">
  <div class="brand">
    <a class="brand-link" href="index.html">
      <span class="brand-mark">DL</span>
      <span class="brand-text">
        <strong>深度学习学习站</strong>
        <em>从数学基础到大模型落地</em>
      </span>
    </a>
  </div>
  <div class="nav-search">
    <input id="nav-search" type="search" placeholder="筛选章节（按 / 聚焦）" autocomplete="off">
  </div>
  <nav class="nav" id="nav">
{{NAV}}
  </nav>
  <div class="side-foot">
    <div class="progress-top"><span>学习进度</span><span id="progress-count">0 / 17</span></div>
    <div class="progress-bar"><i id="progress-bar"></i></div>
    <a class="side-link" href="16-resources.html">资源与项目清单 →</a>
  </div>
</aside>
<main class="main">
  <div class="topbar">
    <button class="nav-toggle" id="nav-toggle" type="button">☰ 目录</button>
    <span class="topbar-chapter">{{CRUMB}}</span>
    <span class="topbar-line"></span>
    <span>离线可用 · 无需联网</span>
  </div>
  <article class="content">
{{BODY}}
{{ACTIONS}}
{{PAGER}}
  </article>
  <footer class="page-foot">
    <span>深度学习学习站 · 共 17 章，按顺序阅读效果最佳</span>
    <span>公式为 HTML 排版，代码基于 PyTorch 2.x</span>
  </footer>
</main>
</div>
<script src="assets/site.js"></script>
</body>
</html>
"""

ACTIONS = """    <div class="chapter-actions">
      <button class="mark-done" id="mark-done" type="button">标记本章已学完</button>
      <span class="hint">进度保存在本机浏览器，用于跟踪学习路线</span>
    </div>"""


def outline_of(body: str) -> str:
    items = re.findall(r'<h[23] id="([^"]+)"[^>]*>(.*?)</h[23]>', body, re.S)
    if len(items) < 2:
        return ""
    lis = []
    for anchor, raw in items:
        text = re.sub(r"<[^>]+>", "", raw).strip()
        lis.append('<li><a href="#%s">%s</a></li>' % (anchor, text))
    return (
        '<nav class="outline" id="outline" aria-label="本章目录">\n'
        '  <div class="outline-head"><span>本章目录</span>'
        '<button class="outline-toggle" id="outline-toggle" type="button">收起</button></div>\n'
        "  <ol>\n    " + "\n    ".join(lis) + "\n  </ol>\n</nav>"
    )


def nav_html(active: str) -> str:
    out = []
    for group, items in NAV:
        out.append('    <div class="nav-group">')
        out.append('      <span class="nav-group-title">%s</span>' % group)
        for slug, num, title, sub in items:
            cls = "nav-item active" if slug == active else "nav-item"
            chapter = ' data-chapter="1"' if slug != "index" else ' data-chapter="0"'
            out.append(
                '      <a class="%s" href="%s.html" data-page="%s"%s>'
                % (cls, slug, slug, chapter)
            )
            out.append(
                '        <span class="nav-num">%s</span>'
                '<span class="nav-body"><strong>%s</strong><em>%s</em></span>'
                '<span class="tick" aria-hidden="true"></span>' % (num, title, sub)
            )
            out.append("      </a>")
        out.append("    </div>")
    return "\n".join(out)


def pager_html(slug: str) -> str:
    idx = [p[0] for p in PAGES].index(slug)
    prev_item = PAGES[idx - 1] if idx > 0 else None
    next_item = PAGES[idx + 1] if idx < len(PAGES) - 1 else None
    parts = ['    <nav class="pager" aria-label="章节翻页">']
    if prev_item:
        parts.append(
            '      <a class="prev" href="%s.html"><span class="dir">← 上一章</span>'
            '<span class="ttl">%s</span></a>' % (prev_item[0], prev_item[2])
        )
    else:
        parts.append('      <span class="empty"></span>')
    if next_item:
        parts.append(
            '      <a class="next" href="%s.html"><span class="dir">下一章 →</span>'
            '<span class="ttl">%s</span></a>' % (next_item[0], next_item[2])
        )
    else:
        parts.append('      <span class="empty"></span>')
    parts.append("    </nav>")
    return "\n".join(parts)


def build_page(slug: str, num: str, title: str, sub: str) -> str:
    src = SRC / ("%s.html" % slug)
    body = src.read_text(encoding="utf-8").strip()
    outline = "" if slug == "index" else outline_of(body)
    if outline:
        if "</header>" in body:
            body = body.replace("</header>", "</header>\n" + outline, 1)
        else:
            body = outline + "\n" + body
    crumb = "深度学习学习站 · %s" % ("学习地图" if slug == "index" else "第 %s 章" % num)
    actions = "" if slug == "index" else ACTIONS
    html = (
        TPL.replace("{{TITLE}}", title)
        .replace("{{DESC}}", sub)
        .replace("{{NAV}}", nav_html(slug))
        .replace("{{CRUMB}}", crumb)
        .replace("{{BODY}}", body)
        .replace("{{ACTIONS}}", actions)
        .replace("{{PAGER}}", pager_html(slug))
        .replace("{{SLUG}}", slug)
    )
    return html


def main() -> None:
    missing = [p[0] for p in PAGES if not (SRC / ("%s.html" % p[0])).exists()]
    if missing:
        raise SystemExit("缺少章节片段：%s" % ", ".join(missing))
    for slug, num, title, sub in PAGES:
        out = ROOT / ("%s.html" % slug)
        out.write_text(build_page(slug, num, title, sub), encoding="utf-8")
        print("built %-24s %6.1f KB" % (out.name, out.stat().st_size / 1024))
    print("done: %d pages" % len(PAGES))


if __name__ == "__main__":
    main()
