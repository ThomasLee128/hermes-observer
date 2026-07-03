from __future__ import annotations

import re


NEGATIVE_WORDS = ["改", "修", "删", "停", "重启", "补发", "继续", "跑一遍", "执行", "安装", "清理", "迁移"]

STATUS_WORDS = [
    "咋样",
    "怎么样",
    "进度",
    "状态",
    "跑完",
    "跑了吗",
    "在干嘛",
    "在忙啥",
    "忙啥",
    "忙什么",
    "忙着啥",
    "干嘛",
    "做到哪",
    "卡住",
    "没动静",
    "没发",
    "这啥意思",
    "啥意思",
    "正常吗",
    "看下",
    "看看",
    "查下",
    "检查下",
    "理论上",
    "不应该",
    "是不是应该",
    "为什么",
    "为啥",
]

TASK_WORDS = ["Hermes", "hermes", "任务", "cron", "Cron", "队列", "转写", "同步"]


def classify_observer_intent(text: str) -> dict:
    clean = (text or "").strip()
    if not clean:
        return {"is_observer": False, "confidence": 0.0, "reason": "空消息"}
    if any(word in clean for word in NEGATIVE_WORDS):
        return {"is_observer": False, "confidence": 0.05, "reason": "包含执行/修改类词"}

    score = 0.0
    hits: list[str] = []
    for word in STATUS_WORDS:
        if word in clean:
            score += 0.22
            hits.append(word)
    for word in TASK_WORDS:
        if word in clean:
            score += 0.12
            hits.append(word)
    if re.search(r"(为什么|为啥).*(没|不|没有|失败|空|发)", clean):
        score += 0.25
    if re.search(r"(理论上|这个时候|现在).*(应该|不应该|是不是)", clean):
        score += 0.25
    if re.search(r"(帮我)?(看|查|检查).*(任务|状态|进度|Hermes|cron|队列)", clean, re.I):
        score += 0.25
    if clean in {"现在咋样", "跑得咋样", "任务咋样了", "跑完了吗", "在干嘛", "你在忙啥啊", "你在忙啥啊？", "忙啥呢", "忙什么呢", "做到哪了", "这啥意思", "这个正常吗"}:
        score += 0.25

    confidence = min(score, 0.98)
    return {
        "is_observer": confidence >= 0.32,
        "confidence": round(confidence, 2),
        "reason": "、".join(sorted(set(hits))) or "语义弱匹配",
    }


def abstract_pattern(text: str) -> str:
    s = re.sub(r"\d{1,2}[:：]\d{2}", "<时间>", text or "")
    s = re.sub(r"\d+", "<数字>", s)
    s = re.sub(r"\s+", "", s)
    keep = []
    for token in ["咋样", "跑完", "在干嘛", "忙啥", "忙什么", "做到哪", "卡住", "啥意思", "正常吗", "没发", "没动静", "理论上", "不应该", "是不是应该", "看下", "查下", "检查下", "为什么", "为啥"]:
        if token in s:
            keep.append(token)
    return " / ".join(keep) or s[:40]
