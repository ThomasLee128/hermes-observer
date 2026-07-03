from __future__ import annotations

import json
import os
import subprocess
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .wake import abstract_pattern, classify_observer_intent


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def append_jsonl(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def expand_path(value: str, base_env: dict[str, str]) -> Path:
    expanded = value
    for key, val in base_env.items():
        expanded = expanded.replace("${" + key + "}", val)
    return Path(os.path.expandvars(expanded)).expanduser()


def tail_jsonl(path: Path, limit: int = 20) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            continue
    return rows


def run_cmd(cmd: list[str], timeout: int = 10) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=timeout)
        return proc.returncode, "\n".join(x.strip() for x in (proc.stdout, proc.stderr) if x.strip())
    except Exception as exc:
        return 1, f"{type(exc).__name__}: {exc}"


class Observer:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = read_json(config_path, {})
        env = self.config.get("env", {})
        self.env = {k: os.environ.get(k, str(v)) for k, v in env.items()}
        self.state_dir = expand_path(self.config.get("state_dir", "${HERMES_HOME}/data/hermes_observer"), self.env)
        self.candidates_path = self.state_dir / "observer_wake_candidates.json"
        self.patterns_path = self.state_dir / "observer_wake_patterns.json"
        self.runs_path = self.state_dir / "observer_runs.jsonl"

    def gpu_status(self) -> dict[str, Any]:
        if not self.config.get("gpu", {}).get("enabled", True):
            return {"available": False, "note": "GPU 检查未启用"}
        code, out = run_cmd(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total", "--format=csv,noheader,nounits"], timeout=8)
        if code != 0 or not out:
            return {"available": False, "error": out}
        try:
            util, used, total = [int(x.strip()) for x in out.splitlines()[0].split(",")[:3]]
            idle_util = int(self.config.get("gpu", {}).get("idle_util_pct", 20))
            idle_mem = int(self.config.get("gpu", {}).get("idle_memory_mb", 2500))
            return {"available": True, "util": util, "memoryUsedMb": used, "memoryTotalMb": total, "idle": util <= idle_util and used <= idle_mem}
        except Exception:
            return {"available": False, "error": out}

    def cron_status(self) -> dict[str, Any]:
        jobs_path = expand_path(self.config.get("cron", {}).get("jobs_path", "${HERMES_HOME}/cron/jobs.json"), self.env)
        jobs = read_json(jobs_path, {}).get("jobs", [])
        enabled = [j for j in jobs if j.get("enabled")]
        failed = [j for j in enabled if str(j.get("last_status")) in {"error", "failed"}]
        upcoming = sorted([j for j in enabled if j.get("next_run_at")], key=lambda j: str(j.get("next_run_at")))[:5]
        return {
            "enabled": len(enabled),
            "failed": [{"name": j.get("name") or j.get("id"), "script": j.get("script"), "error": j.get("last_error")} for j in failed[:5]],
            "upcoming": [{"name": j.get("name") or j.get("id"), "next": j.get("next_run_at")} for j in upcoming],
        }

    def json_manifest_modules(self) -> list[str]:
        lines = []
        for module in self.config.get("json_manifests", []):
            label = module.get("label", "状态文件")
            path = expand_path(module["path"], self.env)
            data = read_json(path, {})
            if not data:
                lines.append(f"- {label}：未找到或不可读")
                continue
            fields = []
            for name in module.get("fields", []):
                fields.append(f"{name} {data.get(name, '未知')}")
            lines.append(f"- {label}：" + "，".join(fields))
        return lines

    def queue_modules(self) -> list[str]:
        lines = []
        for module in self.config.get("queues", []):
            label = module.get("label", "队列")
            path = expand_path(module["path"], self.env)
            data = read_json(path, {"items": []})
            items = data.get("items", []) if isinstance(data, dict) else []
            counts = Counter(str(x.get("status", "unknown")) for x in items)
            if not items:
                lines.append(f"- {label}：队列为空")
            else:
                parts = [f"{k} {v}" for k, v in sorted(counts.items())]
                lines.append(f"- {label}：" + "，".join(parts))
        return lines

    def learn_wake_phrases(self, trigger_text: str) -> dict[str, Any]:
        # Portable version learns only from explicitly supplied trigger history file.
        history_path = self.config.get("wake_learning", {}).get("history_jsonl")
        if not history_path:
            write_json(self.candidates_path, read_json(self.candidates_path, {"items": []}))
            write_json(self.patterns_path, read_json(self.patterns_path, {"items": []}))
            return {"learned": [], "candidateCount": len(read_json(self.candidates_path, {"items": []}).get("items", []))}

        path = expand_path(history_path, self.env)
        lookback = int(self.config.get("wake_learning", {}).get("lookback_minutes", 60))
        cutoff = datetime.now() - timedelta(minutes=lookback)
        candidates = read_json(self.candidates_path, {"items": []})
        items = candidates.setdefault("items", [])
        learned = []
        if path.exists():
            for line in path.read_text(encoding="utf-8", errors="replace").splitlines()[-500:]:
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                text = str(row.get("text", ""))
                if text == trigger_text:
                    continue
                try:
                    ts = datetime.fromisoformat(str(row.get("ts", "")))
                except Exception:
                    continue
                if ts.replace(tzinfo=None) < cutoff:
                    continue
                result = classify_observer_intent(text)
                if not result["is_observer"]:
                    continue
                pattern = abstract_pattern(text)
                found = next((x for x in items if x.get("pattern") == pattern), None)
                if found:
                    found["evidenceCount"] = int(found.get("evidenceCount", 1)) + 1
                    found["lastSeenAt"] = now_iso()
                else:
                    found = {"pattern": pattern, "intent": "hermes_status_check", "confidence": result["confidence"], "evidenceCount": 1, "status": "candidate", "createdAt": now_iso(), "lastSeenAt": now_iso()}
                    items.append(found)
                learned.append(found)
                if len(learned) >= 3:
                    break
        candidates["items"] = items[:30]
        write_json(self.candidates_path, candidates)
        write_json(self.patterns_path, read_json(self.patterns_path, {"items": []}))
        return {"learned": learned, "candidateCount": len(candidates["items"])}

    def report(self, trigger_text: str = "", learn: bool = True) -> tuple[str, dict[str, Any]]:
        gpu = self.gpu_status()
        cron = self.cron_status()
        manifest_lines = self.json_manifest_modules()
        queue_lines = self.queue_modules()
        learning = self.learn_wake_phrases(trigger_text) if learn else {"learned": []}

        gpu_line = "未读到 GPU 状态"
        if gpu.get("available"):
            gpu_line = f"GPU {gpu['util']}%，显存 {gpu['memoryUsedMb']}/{gpu['memoryTotalMb']}MB"
            gpu_line += "，当前空闲" if gpu.get("idle") else "，当前不算空闲"
        cron_line = "最近没有需要立即处理的 cron 失败"
        if cron["failed"]:
            cron_line = "；".join(f"{x['name']}：{x.get('error') or '失败'}" for x in cron["failed"][:3])
        next_line = "；".join(f"{x['name']} {x['next']}" for x in cron["upcoming"][:3]) or "暂无"

        lines = [
            "Hermes 当前状态",
            "",
            "结论：",
            "- Observer 已完成只读检查；如有业务模块配置，会按模块解释状态。",
            "",
            "资源：",
            f"- {gpu_line}",
            "",
            "业务进展：",
            *(manifest_lines or ["- 未配置 JSON manifest 业务模块"]),
            *(queue_lines or ["- 未配置队列业务模块"]),
            "",
            "Cron：",
            f"- {cron_line}",
            "",
            "下一步：",
            f"- 近期计划：{next_line}",
        ]
        if learning.get("learned"):
            lines.append(f"- Observer 记录了 {len(learning['learned'])} 个唤醒候选。")
        report = "\n".join(lines)
        append_jsonl(self.runs_path, {"ts": now_iso(), "trigger": trigger_text, "learned": len(learning.get("learned", []))})
        return report, {"gpu": gpu, "cron": cron, "learning": learning}
