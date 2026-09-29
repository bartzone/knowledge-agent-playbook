#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dual-layer info filter — 位置感知的信息源风险预扫
================================================================

它做什么
--------
一篇外部材料（公众号文、博客、行业简报、White Paper…）拿过来，
在**人工细读之前**回答两个问题：

  ① 它有没有明显的「夹带私货」信号？（引流 / 带货 / 招募 / 导流就医 / 邀请码）
  ② 那些信号出现在**哪里**？—— 正文中段，还是**只在文末**？

设计上的两个核心判断
--------------------
1. **预扫只报信号，不判对错。** 它的输出是「这里有个东西，你自己看」，
   ⛔ 不是评分、不是通过/不通过。
2. **位置本身是信息。** 同一个词出现在正文中段和只出现在文末，
   风险完全不同：

       「咨询」在正文里 → 普通词，行业分析里到处都是
       「咨询」只在文末第一次出现 → 转化动作

   所以本工具**单独扫文末**，且**只报「正文里完全没有、只在文末出现」的词**。

它不是万能的
------------
* 词表是**可解释的经验判据**，不是模型。会有漏报，也会误报。
* 它**只做初筛**。终审归人。
* ⛔ 别把它当过滤器用（别因为「扫过没报警」就放心）。
  正确用法是：**它扫完 + 你读到结尾**，两条都过才算过。

用法
----
    python3 scan.py article.txt
    python3 scan.py article.txt --json
    python3 scan.py article.txt --tail-ratio 0.20

    from scan import scan_text
    r = scan_text(open("a.txt", encoding="utf-8").read())

许可证：MIT
"""

from __future__ import annotations

import argparse
import json
import re
import sys

# --------------------------------------------------------------------------
# 词表
# --------------------------------------------------------------------------
# ⚠️ 词表纪律：
#   * 只放**语用上很少正当出现**的词。像「门诊」「医院」「购买」这类
#     在正当科普与行业分析里到处都是，⛔ 不要放进来（否则误报淹没信号）。
#   * 要加词，**先拿样本回测**：确认它能抓到正样本、且不误伤正经文。

# ① 引流 / 带货 / 交易动作
COMMERCE_STRONG = [
    "点击购买", "立即购买", "马上抢", "限时优惠", "限时折扣", "领取优惠券",
    "下单", "加购物车", "直播间", "橱窗", "小店", "上架", "开售", "预售",
    "扫码购买", "团购", "拼团", "秒杀", "满减", "返现",
]

# ② 私域导流 / 加联系
LEAD_STRONG = [
    "加微信", "加我微信", "扫码添加", "私信我", "添加好友", "进群", "入群",
    "社群", "扫码进群", "扫码咨询", "一对一咨询", "私聊", "联系我们获取",
]

# ③ 招募 / 多层次（MLM）信号
RECRUIT_STRONG = [
    "招商", "代理招募", "加盟", "事业说明会", "团队裂变", "拉人头", "下级",
    "层级返佣", "推荐奖励", "发展下线", "直销",
]

# ④ 邀请码 / 返利 / 返佣
REFERRAL_STRONG = [
    "我的邀请码", "邀请码", "推荐码", "返利", "返佣", "佣金", "分成",
    "领取额外", "薅羊毛", "专属链接", "专属优惠码",
]

# ⑤ 线下就医 / 到店转化（⚠️ 只放强动作，不放「门诊」「医院」「就诊」等正当词）
CLINIC_STRONG = [
    "预约挂号", "点击挂号", "挂号就诊", "预约门诊", "预约就诊", "预约咨询",
    "扫码预约", "预约面诊", "面诊", "到院", "到店咨询", "在线咨询",
]

# ⑥ 招生 / 课程 / 论坛抢票（⚠️ 只用在文末位置加权里，不做全文强判）
TAIL_TERMS = [
    "预约", "挂号", "门诊", "问诊", "面诊", "到店", "到院", "私信",
    "加微信", "扫码", "进群", "社群", "报名", "下单", "购买", "领券",
    "优惠券", "折扣", "限时", "名额", "邀请码", "推荐码", "返利", "返佣",
    "佣金", "学费", "招生", "训练营", "开班", "发车", "小店", "橱窗",
    "直播间", "上架", "咨询", "代理", "加盟", "事业说明会",
]

# ⚠️ 全行业通用的编辑部尾巴 —— 是噪音不是信号，扫之前先剥掉。
#    这些句子在**任何**公众号文末都有，留着只会淹没真正的信号。
TAIL_EXEMPT = [
    "合作或投稿，请私信联系",
    "投稿请私信联系",
    "点赞、在看、转发",
    "点赞在看转发",
    "点个赞、在看、转发",
    "星标⭐",
    "下次见",
    "我们下次见",
    "预览时标签不可点",
    "不喜欢",
]

# 文末窗口比例
TAIL_RATIO = 0.15

# 判定阈值
#   ⚠️ 为什么这里不需要 ≥2 门槛：像「我的邀请码」这种第一人称强词，
#      几乎没有正当的第三人称用法，命中一条就够。
#      而像「上架」「直播间」这类会出现在正当行业分析里的词，
#      必须靠 TAIL_TERMS 的位置加权来判，⛔ 不进这里。
STRONG_GROUPS = {
    "commerce": COMMERCE_STRONG,
    "lead": LEAD_STRONG,
    "recruit": RECRUIT_STRONG,
    "referral": REFERRAL_STRONG,
    "clinic": CLINIC_STRONG,
}

GROUP_LABEL = {
    "commerce": "带货 / 交易",
    "lead": "私域导流",
    "recruit": "招募 / MLM",
    "referral": "邀请码 / 返利",
    "clinic": "线下就医导流",
}


def _strip_exempt(tail: str) -> str:
    """剥离通用编辑部尾巴，避免它们淹没真信号。"""
    for s in TAIL_EXEMPT:
        tail = tail.replace(s, "")
    return tail


def scan_text(text: str, tail_ratio: float = TAIL_RATIO) -> dict:
    """扫一篇文本，返回结构化结果（不改动输入）。"""
    if not text:
        return {"error": "empty text"}

    # ── 全文强词命中 ──────────────────────────────────────────
    groups: dict[str, list[str]] = {}
    for key, words in STRONG_GROUPS.items():
        hit = [w for w in words if w in text]
        if hit:
            groups[key] = hit

    # ── 文末位置加权 ─────────────────────────────────────────
    cut = max(1, int(len(text) * (1.0 - tail_ratio)))
    body, tail = text[:cut], _strip_exempt(text[cut:])

    tail_all = [w for w in TAIL_TERMS if w in tail]
    # ⭐ 只报「正文里完全没有、只在文末出现」的词 —— 这几乎零误报
    tail_only = [w for w in tail_all if w not in body]

    # ── 汇总 ────────────────────────────────────────────────
    flags = {f"{k}_flag": bool(v) for k, v in groups.items()}
    flags["tail_only_flag"] = bool(tail_only)

    return {
        "length": len(text),
        "groups": groups,
        "flags": flags,
        "tail_window_chars": len(tail),
        "tail_all_hits": tail_all,
        "tail_only_hits": tail_only,
        "any_flag": any(flags.values()),
    }


def render(result: dict) -> str:
    """人读版输出。"""
    if "error" in result:
        return f"无法扫描：{result['error']}"

    out = []
    out.append("=" * 72)
    out.append("位置感知风险预扫 —— 只报信号，不判对错")
    out.append("=" * 72)
    out.append(f"文本长度 {result['length']} 字符｜文末窗口 {result['tail_window_chars']} 字符")
    out.append("")

    any_hit = False
    for key, label in GROUP_LABEL.items():
        hit = result["groups"].get(key)
        if hit:
            any_hit = True
            out.append(f"【{label}】⚠️ 命中 {len(hit)} 项：{'、'.join(hit)}")
        else:
            out.append(f"【{label}】✅ 无")

    out.append("")
    if result["tail_only_hits"]:
        any_hit = True
        out.append("【⭐ 文末独有信号】⚠️ 这些词**正文里完全没有、只在文末出现**：")
        out.append(f"    {'、'.join(result['tail_only_hits'])}")
        out.append("    ⭐ 判据：正经文章的词，不会只在结尾才第一次出现。")
    else:
        out.append("【⭐ 文末独有信号】✅ 无")
        if result["tail_all_hits"]:
            out.append(f"    （文末另有这些词，但正文里也出现过，按普通词处理："
                       f"{'、'.join(result['tail_all_hits'])}）")

    out.append("")
    out.append("-" * 72)
    out.append("⚠️ 预扫只报信号，不判对错。它扫完 ≠ 你读完。")
    out.append("⚠️ 它会漏报，也会误报。终审归人。")
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description="位置感知的信息源风险预扫")
    ap.add_argument("path", help="待扫描的文本文件")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--tail-ratio", type=float, default=TAIL_RATIO,
                    help=f"文末窗口比例（默认 {TAIL_RATIO}）")
    args = ap.parse_args()

    try:
        with open(args.path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"读不到文件：{e}", file=sys.stderr)
        return 2

    result = scan_text(text, tail_ratio=args.tail_ratio)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
