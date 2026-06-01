#!/usr/bin/env python3
"""
课程论文图表生成脚本

用法：
  # 完整生成（JSON中所有图表）
  python generate_charts.py --input charts.json --output ./images/

  # 指定类型（从JSON中筛选）
  python generate_charts.py -i charts.json -t bar,line,pie -o ./images/

  # 指定数量（截取前N个）
  python generate_charts.py -i charts.json -n 3 -o ./images/

  # 默认模式（标准5图：柱状、雷达、流程、折线、面积）
  python generate_charts.py -i charts.json --default -o ./images/

  # 混合（指定类型 + 限制数量）
  python generate_charts.py -i charts.json -t heatmap,box -n 2 -o ./images/

支持11种图表类型：
  bar         - 柱状图（性能对比）
  radar       - 雷达图（多维对比）
  flow        - 流程图（技术演进）
  line        - 折线图（趋势/循环）
  area        - 面积图（文献趋势）
  pie         - 饼图（占比分析）
  scatter     - 散点图（相关性）
  heatmap     - 热力图（矩阵/系数）
  box         - 箱线图（分布统计）
  stacked_bar - 堆叠柱状图（构成分析）
  violin      - 小提琴图（密度分布）
"""

import json
import os
import sys
import argparse

# ── Windows 编码修复 ─────────────────────────────────────────
# Windows 中文系统默认 GBK，emoji 和特殊字符会报错
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ── 依赖检测 ─────────────────────────────────────────────────
try:
    import numpy as np
except ImportError:
    print("[ERROR] numpy not installed. Run: pip install numpy")
    sys.exit(1)

try:
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端，兼容服务器环境
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
except ImportError:
    print("[ERROR] matplotlib not installed. Run: pip install matplotlib")
    sys.exit(1)

# ── 中文字体设置（带 fallback）─────────────────────────────────
import platform
_system = platform.system()
if _system == 'Windows':
    plt.rcParams['font.sans-serif'] = ['SimSun', 'SimHei', 'Microsoft YaHei', 'Times New Roman']
elif _system == 'Darwin':  # macOS
    plt.rcParams['font.sans-serif'] = ['STSong', 'Heiti SC', 'PingFang SC', 'Times New Roman']
else:  # Linux
    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

DPI = 300
FIG_WIDTH = 8  # 英寸
FIG_HEIGHT = 5


def setup_figure():
    """创建标准尺寸的图形"""
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    return fig, ax


def save_figure(fig, output_dir, filename):
    """保存图形到指定目录"""
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    fig.savefig(filepath, dpi=DPI, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  [OK] Saved: {filepath}")
    return filepath


# ── 图1: 材料性能对比（柱状图）────────────────────────────────

def chart_bar_comparison(data, output_dir):
    """
    data 格式:
    {
      "title": "不同材料性能对比",
      "xlabel": "材料类型",
      "ylabel": "比容量 (mAh/g)",
      "categories": ["Si", "Graphite", "SiO", "Li4Ti5O12"],
      "series": [
        {"name": "理论比容量", "values": [4200, 372, 1600, 175]},
        {"name": "实际比容量", "values": [3000, 340, 1200, 160]}
      ],
      "colors": ["#2196F3", "#FF9800"]
    }
    """
    fig, ax = setup_figure()
    categories = data["categories"]
    series = data["series"]
    x = np.arange(len(categories))
    width = 0.8 / len(series)

    for i, s in enumerate(series):
        color = data.get("colors", [None])[i] if data.get("colors") else None
        bars = ax.bar(x + i * width - 0.4 + width / 2, s["values"],
                      width, label=s["name"], color=color, edgecolor='white', linewidth=0.5)
        # 在柱子上方显示数值
        for bar, val in zip(bars, s["values"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 20,
                    str(val), ha='center', va='bottom', fontsize=8)

    ax.set_xlabel(data.get("xlabel", ""), fontsize=12)
    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "材料性能对比"), fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig1_bar_comparison.png")


# ── 图2: 多维性能对比（雷达图）────────────────────────────────

def chart_radar(data, output_dir):
    """
    data 格式:
    {
      "title": "材料多维性能对比",
      "dimensions": ["比容量", "循环稳定性", "倍率性能", "导电性", "成本", "安全性"],
      "items": [
        {"name": "Si", "values": [95, 40, 60, 30, 70, 50]},
        {"name": "Graphite", "values": [50, 90, 80, 85, 90, 85]}
      ],
      "colors": ["#2196F3", "#FF9800"]
    }
    """
    fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT), dpi=DPI)
    ax = fig.add_subplot(111, polar=True)

    dims = data["dimensions"]
    n = len(dims)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    for i, item in enumerate(data["items"]):
        values = item["values"] + item["values"][:1]  # 闭合
        color = data.get("colors", [None])[i] if data.get("colors") else None
        ax.plot(angles, values, 'o-', linewidth=2, label=item["name"], color=color)
        ax.fill(angles, values, alpha=0.15, color=color)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dims, fontsize=11)
    ax.set_ylim(0, 100)
    ax.set_title(data.get("title", "多维性能对比"), fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=10, loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True, alpha=0.3)

    return save_figure(fig, output_dir, "fig2_radar.png")


# ── 图3: 结构演进示意图（流程图）────────────────────────────

def chart_flow_diagram(data, output_dir):
    """
    data 格式:
    {
      "title": "晶体管结构演进",
      "steps": [
        {"name": "平面MOSFET", "desc": "传统结构", "year": "~2000"},
        {"name": "FinFET", "desc": "3D鳍片", "year": "~2011"},
        {"name": "GAA", "desc": "全环绕栅极", "year": "~2024"}
      ]
    }
    """
    fig, ax = setup_figure()
    ax.set_xlim(-0.5, len(data["steps"]) - 0.5)
    ax.set_ylim(-1, 2)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.set_title(data.get("title", "技术演进"), fontsize=14, fontweight='bold', pad=15)

    box_width = 0.7
    box_height = 0.8
    colors = ['#E3F2FD', '#BBDEFB', '#90CAF9']

    for i, step in enumerate(data["steps"]):
        # 绘制圆角矩形
        rect = FancyBboxPatch(
            (i - box_width / 2, 0.5 - box_height / 2),
            box_width, box_height,
            boxstyle="round,pad=0.05",
            facecolor=colors[i % len(colors)],
            edgecolor='#1565C0',
            linewidth=2
        )
        ax.add_patch(rect)

        # 名称
        ax.text(i, 0.6, step["name"], ha='center', va='center',
                fontsize=12, fontweight='bold')
        # 描述
        ax.text(i, 0.35, step.get("desc", ""), ha='center', va='center',
                fontsize=9, color='#555')
        # 年份
        ax.text(i, -0.1, step.get("year", ""), ha='center', va='center',
                fontsize=10, color='#1565C0', style='italic')

        # 箭头（除最后一个）
        if i < len(data["steps"]) - 1:
            ax.annotate('', xy=(i + 0.5, 0.5), xytext=(i + 0.35, 0.5),
                        arrowprops=dict(arrowstyle='->', color='#1565C0', lw=2))

    return save_figure(fig, output_dir, "fig3_flow_diagram.png")


# ── 图4: 循环性能对比（折线图）────────────────────────────────

def chart_line_plot(data, output_dir):
    """
    data 格式:
    {
      "title": "循环性能对比",
      "xlabel": "循环次数",
      "ylabel": "容量保持率 (%)",
      "x": [0, 50, 100, 200, 300, 500],
      "series": [
        {"name": "Si/C复合", "values": [100, 95, 88, 78, 70, 60]},
        {"name": "纯Si", "values": [100, 80, 60, 40, 25, 15]}
      ],
      "colors": ["#4CAF50", "#F44336"]
    }
    """
    fig, ax = setup_figure()

    for i, s in enumerate(data["series"]):
        color = data.get("colors", [None])[i] if data.get("colors") else None
        marker = ['o', 's', '^', 'D'][i % 4]
        ax.plot(data["x"], s["values"], marker=marker, markersize=6,
                linewidth=2, label=s["name"], color=color)

    ax.set_xlabel(data.get("xlabel", ""), fontsize=12)
    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "循环性能对比"), fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig4_line_plot.png")


# ── 图5: 文献趋势分析（面积图）────────────────────────────────

def chart_area_plot(data, output_dir):
    """
    data 格式:
    {
      "title": "近10年文献发表趋势",
      "xlabel": "年份",
      "ylabel": "发表数量",
      "x": [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
      "series": [
        {"name": "FinFET", "values": [120, 150, 180, 220, 280, 350, 400, 450, 500, 520]},
        {"name": "GAA", "values": [10, 15, 20, 30, 50, 80, 130, 200, 320, 450]}
      ],
      "colors": ["#2196F3", "#FF9800"]
    }
    """
    fig, ax = setup_figure()

    for i, s in enumerate(data["series"]):
        color = data.get("colors", [None])[i] if data.get("colors") else None
        ax.fill_between(data["x"], s["values"], alpha=0.3, color=color)
        ax.plot(data["x"], s["values"], linewidth=2, label=s["name"], color=color)

    ax.set_xlabel(data.get("xlabel", ""), fontsize=12)
    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "文献趋势分析"), fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig5_area_plot.png")


# ── 图6: 饼图 ────────────────────────────────────────────────

def chart_pie(data, output_dir):
    """
    data 格式:
    {
      "title": "锂离子电池市场份额",
      "labels": ["三元材料", "磷酸铁锂", "钴酸锂", "锰酸锂", "其他"],
      "values": [45, 35, 10, 5, 5],
      "colors": ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#607D8B"],
      "explode_index": 0
    }
    """
    fig, ax = setup_figure()
    labels = data["labels"]
    values = data["values"]
    colors = data.get("colors", plt.cm.Set3(np.linspace(0, 1, len(labels))))

    # 可选：突出某一块
    explode = [0] * len(labels)
    if "explode_index" in data:
        explode[data["explode_index"]] = 0.08

    wedges, texts, autotexts = ax.pie(
        values, labels=labels, colors=colors, explode=explode,
        autopct='%1.1f%%', startangle=90, pctdistance=0.75,
        textprops={'fontsize': 11}
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_color('white')
        t.set_fontweight('bold')

    ax.set_title(data.get("title", "占比分析"), fontsize=14, fontweight='bold', pad=15)
    return save_figure(fig, output_dir, "fig_pie.png")


# ── 图7: 散点图 ──────────────────────────────────────────────

def chart_scatter(data, output_dir):
    """
    data 格式:
    {
      "title": "比容量与循环稳定性关系",
      "xlabel": "首次放电比容量 (mAh/g)",
      "ylabel": "100圈容量保持率 (%)",
      "series": [
        {"name": "Si基材料", "x": [2800, 3000, 3200, 3500], "y": [75, 68, 60, 50]},
        {"name": "碳基材料", "x": [350, 370, 400, 420], "y": [95, 92, 90, 88]}
      ],
      "colors": ["#2196F3", "#FF9800"]
    }
    """
    fig, ax = setup_figure()

    for i, s in enumerate(data["series"]):
        color = data.get("colors", [None])[i] if data.get("colors") else None
        marker = ['o', 's', '^', 'D', 'v'][i % 5]
        ax.scatter(s["x"], s["y"], s=80, marker=marker, label=s["name"],
                   color=color, edgecolors='white', linewidth=0.5, alpha=0.8)

    ax.set_xlabel(data.get("xlabel", ""), fontsize=12)
    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "散点图"), fontsize=14, fontweight='bold', pad=15)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig_scatter.png")


# ── 图8: 热力图 ──────────────────────────────────────────────

def chart_heatmap(data, output_dir):
    """
    data 格式:
    {
      "title": "材料-性能相关系数矩阵",
      "xlabel": ["比容量", "循环", "倍率", "导电性", "成本"],
      "ylabel": ["比容量", "循环", "倍率", "导电性", "成本"],
      "matrix": [
        [1.0, -0.3, 0.5, -0.2, 0.6],
        [-0.3, 1.0, 0.2, 0.7, -0.4],
        [0.5, 0.2, 1.0, 0.4, -0.1],
        [-0.2, 0.7, 0.4, 1.0, -0.3],
        [0.6, -0.4, -0.1, -0.3, 1.0]
      ],
      "cmap": "RdBu_r",
      "vmin": -1,
      "vmax": 1
    }
    """
    fig, ax = setup_figure()
    matrix = np.array(data["matrix"])

    im = ax.imshow(matrix, cmap=data.get("cmap", "RdBu_r"),
                   vmin=data.get("vmin", -1), vmax=data.get("vmax", 1))

    # 标签
    xlabels = data.get("xlabel", [str(i) for i in range(matrix.shape[1])])
    ylabels = data.get("ylabel", [str(i) for i in range(matrix.shape[0])])
    ax.set_xticks(np.arange(len(xlabels)))
    ax.set_yticks(np.arange(len(ylabels)))
    ax.set_xticklabels(xlabels, fontsize=10)
    ax.set_yticklabels(ylabels, fontsize=10)

    # 在每个格子里显示数值
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            color = 'white' if abs(matrix[i, j]) > 0.6 else 'black'
            ax.text(j, i, f'{matrix[i, j]:.2f}', ha='center', va='center',
                    fontsize=9, color=color)

    ax.set_title(data.get("title", "热力图"), fontsize=14, fontweight='bold', pad=15)
    fig.colorbar(im, ax=ax, shrink=0.8)

    return save_figure(fig, output_dir, "fig_heatmap.png")


# ── 图9: 箱线图 ──────────────────────────────────────────────

def chart_box(data, output_dir):
    """
    data 格式:
    {
      "title": "不同材料粒径分布",
      "ylabel": "粒径 (nm)",
      "categories": ["Si", "Graphite", "SiO", "Li4Ti5O12"],
      "values": [
        [120, 135, 150, 160, 180, 200, 220, 250],
        [80, 90, 95, 100, 105, 110, 120],
        [100, 110, 125, 140, 155, 170, 190, 210],
        [200, 220, 240, 260, 280, 300, 320]
      ],
      "colors": ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]
    }
    """
    fig, ax = setup_figure()

    bp = ax.boxplot(data["values"], labels=data["categories"], patch_artist=True,
                    widths=0.6, showmeans=True,
                    meanprops=dict(marker='D', markerfacecolor='white', markersize=6))

    colors = data.get("colors", plt.cm.Set2(np.linspace(0, 1, len(data["categories"]))))
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "箱线图"), fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig_box.png")


# ── 图10: 堆叠柱状图 ─────────────────────────────────────────

def chart_stacked_bar(data, output_dir):
    """
    data 格式:
    {
      "title": "各年份专利技术构成",
      "xlabel": "年份",
      "ylabel": "专利数量",
      "categories": ["2020", "2021", "2022", "2023", "2024"],
      "series": [
        {"name": "结构设计", "values": [30, 45, 60, 80, 100]},
        {"name": "工艺优化", "values": [20, 30, 40, 55, 70]},
        {"name": "材料创新", "values": [10, 15, 25, 35, 50]}
      ],
      "colors": ["#2196F3", "#4CAF50", "#FF9800"]
    }
    """
    fig, ax = setup_figure()
    categories = data["categories"]
    series = data["series"]
    x = np.arange(len(categories))

    bottom = np.zeros(len(categories))
    for i, s in enumerate(series):
        color = data.get("colors", [None])[i] if data.get("colors") else None
        ax.bar(x, s["values"], 0.6, bottom=bottom, label=s["name"],
               color=color, edgecolor='white', linewidth=0.5)
        bottom += np.array(s["values"])

    ax.set_xlabel(data.get("xlabel", ""), fontsize=12)
    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "堆叠柱状图"), fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig_stacked_bar.png")


# ── 图11: 小提琴图 ───────────────────────────────────────────

def chart_violin(data, output_dir):
    """
    data 格式:
    {
      "title": "不同工艺条件下的粒径分布",
      "ylabel": "粒径 (nm)",
      "categories": ["条件A", "条件B", "条件C", "条件D"],
      "values": [
        [100, 110, 120, 130, 140, 150, 160, 170, 180],
        [80, 90, 100, 110, 120, 130, 140],
        [150, 160, 170, 180, 190, 200, 210, 220, 230, 240],
        [90, 100, 110, 120, 130, 140, 150, 160]
      ],
      "colors": ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]
    }
    """
    fig, ax = setup_figure()

    parts = ax.violinplot(data["values"], positions=range(len(data["categories"])),
                          showmeans=True, showmedians=True, showextrema=True)

    colors = data.get("colors", plt.cm.Set2(np.linspace(0, 1, len(data["categories"]))))
    for i, pc in enumerate(parts['bodies']):
        pc.set_facecolor(colors[i % len(colors)])
        pc.set_alpha(0.7)

    ax.set_xticks(range(len(data["categories"])))
    ax.set_xticklabels(data["categories"], fontsize=11)
    ax.set_ylabel(data.get("ylabel", ""), fontsize=12)
    ax.set_title(data.get("title", "小提琴图"), fontsize=14, fontweight='bold', pad=15)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    return save_figure(fig, output_dir, "fig_violin.png")


# ── 主流程 ───────────────────────────────────────────────────

CHART_MAP = {
    "bar": ("Bar chart", chart_bar_comparison),
    "radar": ("Radar chart", chart_radar),
    "flow": ("Flow diagram", chart_flow_diagram),
    "line": ("Line chart", chart_line_plot),
    "area": ("Area chart", chart_area_plot),
    "pie": ("Pie chart", chart_pie),
    "scatter": ("Scatter plot", chart_scatter),
    "heatmap": ("Heatmap", chart_heatmap),
    "box": ("Box plot", chart_box),
    "stacked_bar": ("Stacked bar chart", chart_stacked_bar),
    "violin": ("Violin plot", chart_violin),
}


DEFAULT_TYPES = ["bar", "radar", "flow", "line", "area"]


def main():
    parser = argparse.ArgumentParser(description="课程论文图表生成")
    parser.add_argument("--input", "-i", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", "-o", default="./images", help="输出目录（默认 ./images）")
    parser.add_argument("--type", "-t", default=None,
                        help="图表类型，逗号分隔（如 bar,line,pie）。从输入JSON中筛选")
    parser.add_argument("--count", "-n", type=int, default=None,
                        help="生成图表数量（截取前N个）")
    parser.add_argument("--default", "-d", action="store_true",
                        help="默认模式，等同于 --type bar,radar,flow,line,area")
    args = parser.parse_args()

    # 自动创建输出目录
    os.makedirs(args.output, exist_ok=True)

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"[ERROR] Input file not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        charts_data = json.load(f)

    charts = charts_data.get("charts", [])

    # --default: 使用标准5图类型
    if args.default:
        filter_types = DEFAULT_TYPES
    # --type: 使用用户指定类型
    elif args.type:
        filter_types = [t.strip() for t in args.type.split(",")]
    else:
        filter_types = None

    # 筛选类型
    if filter_types:
        charts = [c for c in charts if c["type"] in filter_types]
        # 保持用户指定的顺序
        type_order = {t: i for i, t in enumerate(filter_types)}
        charts.sort(key=lambda c: type_order.get(c["type"], 99))

    # 截取数量
    if args.count is not None:
        charts = charts[:args.count]

    if not charts:
        print("[WARN] No charts to generate after filtering.")
        return

    print(f"[START] Generating {len(charts)} charts...\n")
    results = []

    for chart in charts:
        chart_type = chart["type"]
        if chart_type not in CHART_MAP:
            print(f"  [WARN] Unknown chart type: {chart_type}, skipping")
            continue

        desc, func = CHART_MAP[chart_type]
        print(f"  Generating {desc}...")
        filepath = func(chart["data"], args.output)
        results.append({
            "type": chart_type,
            "file": filepath,
            "description": chart.get("description", desc),
        })

    # Output summary
    print(f"\n[DONE] Charts generated: {len(results)}")
    summary_path = os.path.join(args.output, "chart_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"   Summary: {summary_path}")


if __name__ == "__main__":
    main()
