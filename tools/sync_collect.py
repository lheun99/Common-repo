#!/usr/bin/env python3
"""공통 자산 정리 대상 모으기 (common-asset-sync의 3단계와 4단계의 소스 읽기를 대신한다).

대기열(.git/common-asset-pending.txt)의 커밋 중 아직 정리하지 않은 것을 찾아,
커밋별로 정보·파일 상태·이전/이후 소스·같은 폴더의 연결 파일·정리집의 기존 항목을 JSON 하나로 낸다.
파일은 읽기만 한다. (아무것도 쓰거나 지우지 않는다.)

사용:
  python tools/sync_collect.py                  # 대기열 전체 (오래된 커밋부터)
  python tools/sync_collect.py --hashes 8777d82 # 지정한 커밋만 (대기열과 상관없이)

출력: stdout에 JSON 한 덩어리.
표준 라이브러리만 쓴다.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX = os.path.join(REPO, "asset-index", "asset-index.json")
CHANGES = os.path.join(REPO, "asset-index", "changes")
PENDING = os.path.join(REPO, ".git", "common-asset-pending.txt")
SCOPE_DIRS = ("components/", "backend/")
SOURCE_EXT = (".tsx", ".ts", ".jsx", ".js", ".java", ".xml")
MAX_FILE_CHARS = 60000


def git(*args):
    p = subprocess.run(["git", "-c", "core.quotepath=off", "-C", REPO, *args],
                       capture_output=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, p.stdout


def show(rev, path):
    ok, out = git("show", f"{rev}:{path}")
    if not ok:
        return None
    return out if len(out) <= MAX_FILE_CHARS else out[:MAX_FILE_CHARS] + "\n...(잘림)"


def pending_hashes():
    if not os.path.exists(PENDING):
        return []
    res = []
    for ln in open(PENDING, encoding="utf-8", errors="replace").read().splitlines():
        ln = ln.strip()
        if re.fullmatch(r"[0-9a-f]{40}", ln) and ln not in res:
            res.append(ln)
    return res


def order_oldest_first(hashes):
    ok, out = git("rev-list", "--reverse", "HEAD")
    if not ok:
        return hashes
    pos = {h: i for i, h in enumerate(out.split())}
    return sorted(hashes, key=lambda h: pos.get(h, 10**9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hashes", nargs="*", help="대기열 대신 이 커밋만 (앞 7자리 이상)")
    a = ap.parse_args()

    index = json.load(open(INDEX, encoding="utf-8-sig"))["assets"]
    done = set()
    for e in index:
        for k in ("addedInCommit", "updatedInCommit"):
            if e.get(k):
                done.add(e[k][:7])
        for h in e.get("history", []):
            done.add(h["commit"][:7])
    if os.path.isdir(CHANGES):
        done |= {f[:-5] for f in os.listdir(CHANGES) if f.endswith(".json")}

    if a.hashes:
        hashes = []
        for h in a.hashes:
            ok, full = git("rev-parse", "--verify", h + "^{commit}")
            if ok:
                hashes.append(full.strip())
        queue = hashes
    else:
        queue = pending_hashes()
    queue = order_oldest_first(queue)

    out = {"pendingCount": len(queue), "alreadyProcessed": [], "commits": []}
    for h in queue:
        h7 = h[:7]
        if h7 in done and not a.hashes:
            out["alreadyProcessed"].append(h7)
            continue
        ok, info = git("show", "-s", "--format=%H%n%cI%n%s", h)
        if not ok:
            continue
        full, at, subject = (info.split("\n") + ["", "", ""])[:3]
        ok, ds = git("diff-tree", "--no-commit-id", "--name-status", "-r", "-M", h)
        files = []
        for ln in ds.splitlines():
            parts = ln.split("\t")
            status = parts[0][0]
            if status == "R":
                path, old = parts[2], parts[1]
            else:
                path, old = parts[1], None
            files.append({"status": status, "path": path, "oldPath": old,
                          "inScope": path.startswith(SCOPE_DIRS) and path.endswith(SOURCE_EXT)})

        sources = {}
        for f in files:
            if not f["inScope"] and not (f["oldPath"] and f["oldPath"].startswith(SCOPE_DIRS)):
                continue
            s = f["status"]
            sources[f["path"]] = {
                "before": show(h + "~1", f["oldPath"] or f["path"]) if s in ("M", "D", "R") else None,
                "after": show(h, f["path"]) if s != "D" else None,
            }

        # 같은 폴더의 연결 파일(바뀌지 않았어도 기능 전체를 이해하려면 필요). 하위 폴더 안의 파일만.
        siblings = {}
        for f in files:
            if not f["inScope"]:
                continue
            d = os.path.dirname(f["path"])
            if d in ("components", "backend") or d in siblings:
                continue
            ok, ls = git("ls-tree", "-r", "--name-only", h, "--", d + "/")
            names = [n for n in ls.splitlines() if n.endswith(SOURCE_EXT)]
            siblings[d] = {n: (sources[n]["after"] if n in sources else show(h, n)) for n in names}

        # 정리집에 이미 있는 항목 (바뀐 파일을 path 또는 files로 가진 것)
        changed_paths = {"common-repo/" + f["path"] for f in files}
        existing = [e for e in index
                    if e.get("path") in changed_paths or changed_paths & set(e.get("files", []))]

        out["commits"].append({"commit": h7, "hash": full, "committedAt": at, "subject": subject,
                               "files": files, "sources": sources, "siblings": siblings,
                               "existingEntries": existing})
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
