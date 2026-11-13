#!/usr/bin/env python3
"""공통 자산 정리 반영 (common-asset-sync의 6단계를 대신한다).

AI가 승인받은 내용을 payload JSON 한 파일에 담아 주면, 이 스크립트가 한 번에 처리한다.
  1. asset-index/asset-index.json : 항목 추가(맨 끝) / 갱신(그 항목 부분만 교체). 다른 항목의 줄은 건드리지 않는다.
  2. asset-index/changes/<해시7>.json : 커밋마다 새 파일
  3. asset-index/automation.log : 로그 줄 추가 (UTF-8)
  4. .git/common-asset-pending.txt : 처리한 해시 제거
  5. JSON 검증. 실패하면 모든 파일을 원래대로 되돌리고 종료 코드 1.
커밋은 하지 않는다. (AI가 승인 절차에 따라 커밋한다.)

사용:
  python tools/apply_sync.py --payload <payload.json> [--dry-run]
  python tools/apply_sync.py --selftest        # 현재 정리집을 이 스크립트의 서식으로 다시 써 보고 일치율 확인

payload 형식은 .claude/skills/common-asset-sync/SKILL.md 의 [payload 형식] 참고.
표준 라이브러리만 쓴다.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX = os.path.join(REPO, "asset-index", "asset-index.json")
CHANGES = os.path.join(REPO, "asset-index", "changes")
LOG = os.path.join(REPO, "asset-index", "automation.log")
PENDING = os.path.join(REPO, ".git", "common-asset-pending.txt")

KEY_ORDER = ["type", "name", "path", "files", "purpose", "api", "props", "usage", "detail", "related",
             "addedInCommit", "addedAt", "updatedInCommit", "updatedAt", "history"]
INLINE_LISTS = {"props", "related"}          # ["a", "b"] 한 줄
BLOCK_LISTS = {"files", "api", "usage"}      # 한 줄에 하나씩


def j(v):
    return json.dumps(v, ensure_ascii=False)


# ---------------------------------------------------------------- 정리집 항목 직렬화 (기존 서식과 같게)

def ser_entry(e, base=4):
    pad = " " * base
    keys = [k for k in KEY_ORDER if k in e] + [k for k in e if k not in KEY_ORDER]
    lines = []
    for k in keys:
        v = e[k]
        ind = pad + "  "
        if k in INLINE_LISTS and isinstance(v, list):
            body = "[" + ", ".join(j(x) for x in v) + "]"
        elif k in BLOCK_LISTS and isinstance(v, list) and v:
            items = ",\n".join(f"{ind}  {j(x)}" for x in v)
            body = "[\n" + items + "\n" + ind + "]"
        elif k == "history" and isinstance(v, list):
            items = ",\n".join(
                f"{ind}  {{ " + ", ".join(f'{j(hk)}: {j(hv)}' for hk, hv in h.items()) + " }" for h in v)
            body = "[\n" + items + "\n" + ind + "]"
        else:
            body = j(v)
        lines.append(f"{ind}{j(k)}: {body}")
    return "{\n" + ",\n".join(lines) + "\n" + pad + "}"


def find_asset_blocks(text):
    """assets 배열 안의 최상위 {...} 구간 [(start, end)] (end는 닫는 } 다음 위치). 문자열 안의 괄호는 무시."""
    i = text.index('"assets"')
    i = text.index("[", i)
    blocks, depth, in_str, esc, start = [], 0, False, False, None
    for pos in range(i + 1, len(text)):
        c = text[pos]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            if depth == 0:
                start = pos
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                blocks.append((start, pos + 1))
        elif c == "]" and depth == 0:
            break
    return blocks


# ---------------------------------------------------------------- 변경 기록 직렬화

def ser_change_record(rec):
    out = ["{"]
    top = []
    for k in ("commit", "committedAt", "subject"):
        top.append(f"  {j(k)}: {j(rec[k])}")
    changes = []
    for ch in rec["changes"]:
        f = []
        for k, v in ch.items():
            if k == "details":
                if v:
                    items = ",\n".join("        { " + ", ".join(f"{j(a)}: {j(b)}" for a, b in d.items()) + " }" for d in v)
                    f.append(f'      {j(k)}: [\n{items}\n      ]')
                else:
                    f.append(f'      {j(k)}: []')
            elif k == "changedFiles" and v:
                items = ",\n".join(f"        {j(x)}" for x in v)
                f.append(f'      {j(k)}: [\n{items}\n      ]')
            elif isinstance(v, list):
                f.append(f'      {j(k)}: [' + ", ".join(j(x) for x in v) + "]")
            else:
                f.append(f'      {j(k)}: {j(v)}')
        changes.append("    {\n" + ",\n".join(f) + "\n    }")
    top.append('  "changes": [\n' + ",\n".join(changes) + "\n  ]")
    top.append('  "notified": false')
    out.append(",\n".join(top))
    out.append("}")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- 파일 입출력 (줄바꿈 보존)

def read_text(path):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    text = raw.decode("utf-8-sig") if raw.startswith(b"\xef\xbb\xbf") else raw.decode("utf-8")
    return text.replace("\r\n", "\n"), crlf, raw


def write_text(path, text, crlf):
    data = text.replace("\n", "\r\n") if crlf else text
    with open(path, "wb") as f:
        f.write(data.encode("utf-8"))


def git(*args):
    p = subprocess.run(["git", "-C", REPO, *args], capture_output=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, p.stdout.strip()


# ---------------------------------------------------------------- 반영

def apply(payload, dry):
    t0 = time.time()
    index_text, index_crlf, index_raw = read_text(INDEX)
    log_raw = open(LOG, "rb").read() if os.path.exists(LOG) else b""
    pending_raw = open(PENDING, "rb").read() if os.path.exists(PENDING) else None
    created = []
    log_lines = []
    done_hashes = []
    summary = []

    try:
        for c in payload["commits"]:
            h7 = c["commit"]
            at = c["committedAt"]
            changes = c.get("changes", [])
            by_asset = {ch["asset"]: ch for ch in changes}

            for op in c.get("assets", []):
                blocks = find_asset_blocks(index_text)
                existing = {json.loads(index_text[s:e]).get("name"): (s, e) for s, e in blocks}
                if op["op"] == "add":
                    name = op["entry"]["name"]
                    if name in existing:
                        raise ValueError(f"이미 있는 자산을 추가하려 함: {name}")
                    ch = by_asset.get(name)
                    if not ch:
                        raise ValueError(f"변경 기록에 없는 자산: {name}")
                    entry = dict(op["entry"])
                    entry["addedInCommit"] = h7
                    entry["addedAt"] = at
                    entry["history"] = [{"commit": h7, "at": at, "grade": ch["grade"], "summary": ch["summary"]}]
                    last_end = blocks[-1][1]
                    index_text = index_text[:last_end] + ",\n    " + ser_entry(entry) + index_text[last_end:]
                    log_lines.append(f"[{at}] commit {h7} → index에 {name}({entry['type']}) 추가함 [{ch['grade']}]"
                                     + op.get("logSuffix", ""))
                    summary.append(f"추가 {name}")
                elif op["op"] == "update":
                    name = op["name"]
                    if name not in existing:
                        raise ValueError(f"정리집에 없는 자산을 갱신하려 함: {name}")
                    ch = by_asset.get(name)
                    if not ch:
                        raise ValueError(f"변경 기록에 없는 자산: {name}")
                    s, e = existing[name]
                    entry = json.loads(index_text[s:e])
                    entry.update(op["set"])
                    entry["updatedInCommit"] = h7
                    entry["updatedAt"] = at
                    entry.setdefault("history", []).append(
                        {"commit": h7, "at": at, "grade": ch["grade"], "summary": ch["summary"]})
                    index_text = index_text[:s] + ser_entry(entry) + index_text[e:]
                    log_lines.append(f"[{at}] commit {h7} → index의 {name}({entry['type']}) 갱신함: "
                                     + ", ".join(op["set"].keys()) + f" [{ch['grade']}]" + op.get("logSuffix", ""))
                    summary.append(f"갱신 {name}")
                else:
                    raise ValueError(f"알 수 없는 op: {op['op']}")

            for hold in c.get("holds", []):
                log_lines.append(f"[{at}] commit {h7} → 판단 보류: {hold['path']} - {hold['reason']} [{hold['grade']}]")
                summary.append(f"보류 {hold['path']}")

            if changes:
                path = os.path.join(CHANGES, f"{h7}.json")
                if os.path.exists(path):
                    raise ValueError(f"변경 기록이 이미 있음: {h7}.json")
                rec = {"commit": h7, "committedAt": at, "subject": c["subject"], "changes": changes}
                text = ser_change_record(rec)
                if not dry:
                    write_text(path, text, False)
                created.append(path)
            done_hashes.append(h7)

        # 검증
        json.loads(index_text)
        for p in created:
            if not dry:
                json.load(open(p, encoding="utf-8"))
    except Exception:
        for p in created:
            if os.path.exists(p):
                os.remove(p)
        raise

    if dry:
        print(json.dumps({"dryRun": True, "summary": summary, "logLines": log_lines}, ensure_ascii=False, indent=2))
        return

    try:
        write_text(INDEX, index_text, index_crlf)
        json.load(open(INDEX, encoding="utf-8"))
        # 로그: 기존 줄은 그대로 두고 끝에 추가
        add = ("\n".join(log_lines) + "\n").encode("utf-8")
        if log_raw and not log_raw.endswith(b"\n"):
            add = b"\n" + add
        with open(LOG, "ab") as f:
            f.write(add)
        # 대기열에서 처리한 해시 제거
        if pending_raw is not None:
            lines = pending_raw.decode("utf-8", errors="replace").splitlines()
            keep = [ln for ln in lines if not any(ln.strip().startswith(h) for h in done_hashes)]
            with open(PENDING, "wb") as f:
                f.write(("\n".join(keep) + "\n").encode("utf-8") if keep else b"")
    except Exception:
        with open(INDEX, "wb") as f:
            f.write(index_raw)
        with open(LOG, "wb") as f:
            f.write(log_raw)
        if pending_raw is not None:
            with open(PENDING, "wb") as f:
                f.write(pending_raw)
        for p in created:
            if os.path.exists(p):
                os.remove(p)
        raise

    rel = lambda p: os.path.relpath(p, REPO).replace("\\", "/")
    print(json.dumps({
        "ok": True, "summary": summary,
        "files": ["asset-index/asset-index.json", "asset-index/automation.log", *[rel(p) for p in created]],
        "elapsedSec": round(time.time() - t0, 2),
    }, ensure_ascii=False, indent=2))


def selftest():
    text, _, _ = read_text(INDEX)
    blocks = find_asset_blocks(text)
    same = 0
    diff = []
    for s, e in blocks:
        raw = text[s:e]
        parsed = json.loads(raw)
        if ser_entry(parsed) == raw:
            same += 1
        else:
            diff.append(parsed.get("name"))
    print(f"항목 {len(blocks)}개 중 서식 일치 {same}개, 불일치: {diff}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--payload")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.payload:
        ap.error("--payload가 필요합니다")
    with open(a.payload, encoding="utf-8-sig") as f:
        payload = json.load(f)
    try:
        apply(payload, a.dry_run)
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
