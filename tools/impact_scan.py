#!/usr/bin/env python3
"""공통 자산 영향도 스캔 (common-asset-notify의 2~3단계를 대신한다).

변경 기록을 읽어 프로젝트마다 사용처를 찾고, 줄마다 blame으로 작성자를 찾아 JSON으로 출력한다.
프로젝트 저장소는 읽기만 한다. (git ls-files / grep / blame / hash-object / log)

사용:
  python tools/impact_scan.py --records a34a18c.json 6731a2f.json
  python tools/impact_scan.py --assets PageRequest MaskingUtils          # 변경 기록 없이 자산 이름으로 조회

출력: stdout에 JSON 한 덩어리. 로그는 stderr.
표준 라이브러리만 쓴다.
"""
import argparse
import functools
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX_DIR = os.path.join(REPO, "asset-index")
GRADE_RANK = {"breaking": 4, "behavior": 3, "compatible": 2, "new": 1, "docs": 0}
HTTP_TOKENS = ("fetch(", "axios", "RestTemplate", "WebClient", "@GetMapping", "@PostMapping",
               "@PutMapping", "@DeleteMapping", "@RequestMapping", "restTemplate", "webClient")


def log(msg):
    print(msg, file=sys.stderr)


def git(repo, *args):
    """git -C <repo> ... 실행. (성공 여부, stdout)"""
    p = subprocess.run(["git", "-c", "core.quotepath=off", "-C", repo, *args],
                       capture_output=True, encoding="utf-8", errors="replace")
    return p.returncode == 0, p.stdout


def read_json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


# ---------------------------------------------------------------- 입력 모으기

def collect_assets(record_names, asset_names):
    """변경 기록(또는 자산 이름)에서 조사할 자산을 모은다. 같은 자산은 하나로 묶는다."""
    merged = {}
    new_only = {}
    records = []
    if record_names:
        for name in record_names:
            path = name if os.path.isabs(name) else os.path.join(INDEX_DIR, "changes", os.path.basename(name))
            rec = read_json(path)
            records.append(rec)
    for rec in sorted(records, key=lambda r: r.get("committedAt", "")):
        for ch in rec.get("changes", []):
            grade = ch.get("grade")
            if grade == "docs":
                continue
            target = new_only if grade == "new" else merged
            m = target.setdefault(ch["asset"], {
                "name": ch["asset"], "grade": grade, "commits": [], "summaries": [], "actions": [],
                "scanHints": [], "affectedApi": [],
            })
            if GRADE_RANK[grade] > GRADE_RANK[m["grade"]]:
                m["grade"] = grade
            m["commits"].append(rec["commit"])
            m["summaries"].append({"commit": rec["commit"], "at": rec.get("committedAt"), "grade": grade,
                                   "summary": ch.get("summary")})
            if ch.get("action"):
                m["actions"].append(ch["action"])
            for k in ("scanHints", "affectedApi"):
                for v in ch.get(k, []) or []:
                    if v not in m[k]:
                        m[k].append(v)
    for name in asset_names or []:
        merged.setdefault(name, {"name": name, "grade": None, "commits": [], "summaries": [], "actions": [],
                                 "scanHints": [], "affectedApi": []})
    # new와 다른 등급이 섞이면 그 다른 등급 항목으로 조사한다.
    only_new = [v for k, v in new_only.items() if k not in merged]
    return list(merged.values()), only_new


def load_index():
    d = read_json(os.path.join(INDEX_DIR, "asset-index.json"))
    return {a["name"]: a for a in d["assets"]}


def load_projects():
    d = read_json(os.path.join(INDEX_DIR, "projects.json"))
    out = []
    for p in d["projects"]:
        path = p["path"]
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(REPO, path))
        out.append({**p, "abs": path})
    return out


# ---------------------------------------------------------------- 스캔 도구

def grep(repo, pattern, fixed=False, paths=None):
    """git grep -n. [(file, line, text)]"""
    args = ["grep", "-n", "-I", "-F" if fixed else "-E", "-e", pattern]
    if paths:
        args += ["--", *paths]
    ok, out = git(repo, *args)
    res = []
    if not ok:
        return res
    for ln in out.splitlines():
        m = re.match(r"^(.*?):(\d+):(.*)$", ln)
        if m:
            res.append((m.group(1), int(m.group(2)), m.group(3).rstrip("\r")))
    return res


def blame(repo, file, line):
    ok, out = git(repo, "blame", "-L", f"{line},{line}", "--porcelain", "--", file)
    if not ok:
        return None
    name = mail = None
    for ln in out.splitlines():
        if ln.startswith("author "):
            name = ln[7:]
        elif ln.startswith("author-mail "):
            mail = ln[12:].strip("<>")
    if name is None or name == "Not Committed Yet":
        return None
    return {"name": name, "email": mail}


def last_author(repo, file):
    ok, out = git(repo, "log", "-1", "--format=%an|%ae", "--", file)
    if ok and "|" in out:
        n, e = out.strip().split("|", 1)
        return {"name": n, "email": e}
    return None


@functools.lru_cache(maxsize=None)
def show_file(repo, file):
    ok, out = git(repo, "show", f"HEAD:{file}")
    return out if ok else ""


def add_author(lst, a):
    if a and a["email"] not in [x["email"] for x in lst]:
        lst.append(a)


# ---------------------------------------------------------------- 사용처 탐지 (① ~ ④)

def find_copies(proj, name, ext, origin):
    """① 복사본 찾기. [{file, kind, copiedFrom}]"""
    ok, out = git(proj, "ls-files")
    copies = []
    if not ok:
        return copies
    for f in out.splitlines():
        if os.path.basename(f) != name + ext:
            continue
        text = show_file(proj, f)
        if not re.search(rf"(export\s+(function|const)\s+{name}\b|class\s+{name}\b)", text):
            continue
        ok2, blob = git(proj, "hash-object", f)
        copied_from = None
        if ok2:
            ok3, found = git(REPO, "log", "--format=%h %cI", f"--find-object={blob.strip()}", "--", origin)
            if ok3 and found.strip():
                copied_from = found.splitlines()[0].split()[0]
        copies.append({"file": f, "kind": "copy" if copied_from else "copy-modified", "copiedFrom": copied_from})
    return copies


def java_package_of(proj, file):
    m = re.search(r"^package\s+([\w.]+);", show_file(proj, file), re.M)
    return m.group(1) if m else ""


def usage_lines(proj, file, name, is_java, methods=None):
    """③ 사용 줄 찾기. import 줄은 제외. methods가 있으면 그 메서드 호출 줄로 좁힌다."""
    text = show_file(proj, file).split("\n")
    if is_java:
        pats = [rf"\b{name}\.", rf"new {name}\(", rf"\b{name}<", rf"\b{name} [a-z]"]
    else:
        pats = [rf"<{name}[ />]", rf"<{name}$"]
    if methods:
        pats = [rf"\.{re.escape(m)}\(" for m in methods]
    res = []
    for i, t in enumerate(text, 1):
        s = t.strip()
        if s.startswith("import ") or s.startswith("//") or s.startswith("*") or s.startswith("/*"):
            continue
        if any(re.search(p, t) for p in pats):
            res.append((i, t.rstrip("\r").strip()))
    return res


def check_hit(proj, file, name, is_java, hints, line_no):
    """④ 정밀 확인 (breaking). 바뀐 이름이 사용 줄에서 쓰이는지."""
    if not hints:
        return False
    lines = show_file(proj, file).split("\n")
    if is_java:
        body = "\n".join(lines)
        return any(re.search(rf"\.{re.escape(h)}\(", body) for h in hints)
    # 프론트: 사용 줄부터 JSX 요소가 닫힐 때까지
    block = []
    for t in lines[line_no - 1:line_no + 30]:
        block.append(t)
        if "/>" in t or f"</{name}>" in t:
            break
    blk = "\n".join(block)
    return any(re.search(rf"\b{re.escape(h)}\s*[=:]", blk) for h in hints)


def scan_class(proj, name, ext, origin, hints, methods, grade):
    """파일 하나인 자산(또는 기능 자산의 시작 클래스) 하나를 ①~④로 스캔한다."""
    is_java = ext == ".java"
    usages = []
    copies = find_copies(proj["abs"], name, ext, origin)
    copy_files = {c["file"]: c for c in copies}
    copy_pkgs = {}
    for c in copies:
        if is_java:
            copy_pkgs[java_package_of(proj["abs"], c["file"])] = c

    # ② import 찾기
    if is_java:
        found = grep(proj["abs"], rf"^import [a-zA-Z0-9_.]+\.{name};")
    else:
        found = grep(proj["abs"], rf"import .*\b{name}\b.* from ['\"][^'\"]*/{name}['\"]")
    files = {}  # file -> (kind, copiedFrom)
    for f, ln, text in found:
        kind = None
        if is_java:
            m = re.match(r"import ([\w.]+)\." + name + ";", text.strip())
            pkg = m.group(1) if m else ""
            # 복사본은 패키지 줄까지 그대로 복사했을 수 있어, 파일 경로로 먼저 맞춰 본다.
            suffix = pkg.replace(".", "/") + "/" + name + ext
            by_path = [c for cf, c in copy_files.items() if cf.replace("\\", "/").endswith(suffix)]
            if by_path:
                kind = (by_path[0]["kind"], by_path[0]["copiedFrom"])
            elif pkg.startswith("com.company.common"):
                kind = ("import", None)
            elif pkg in copy_pkgs:
                c = copy_pkgs[pkg]
                kind = (c["kind"], c["copiedFrom"])
        else:
            m = re.search(r"from ['\"]([^'\"]+)['\"]", text)
            path = m.group(1) if m else ""
            if "common" in path:
                kind = ("import", None)
            else:
                base = os.path.normpath(os.path.join(os.path.dirname(f), path)).replace("\\", "/")
                for cf, c in copy_files.items():
                    if cf.replace("\\", "/").startswith(base):
                        kind = (c["kind"], c["copiedFrom"])
        if kind:
            files.setdefault(f, kind)
    # 복사본과 같은 패키지(import 없이 사용)와 복사본 파일 자체
    if is_java:
        for cf, c in copy_files.items():
            files.setdefault(cf, (c["kind"], c["copiedFrom"]))
            d = os.path.dirname(cf)
            ok, out = git(proj["abs"], "ls-files", d)
            for f in out.splitlines() if ok else []:
                if f.endswith(".java") and f != cf and f not in files:
                    if re.search(rf"\b{name}\.|new {name}\(", show_file(proj["abs"], f)):
                        files[f] = (c["kind"], c["copiedFrom"])
    else:
        for cf, c in copy_files.items():
            files.setdefault(cf, (c["kind"], c["copiedFrom"]))

    # ③ 사용 줄 + 작성자
    for f, (kind, copied_from) in sorted(files.items()):
        lines = usage_lines(proj["abs"], f, name, is_java, methods)
        is_copy_file = f in copy_files
        if not lines:
            # 사용 줄이 없으면 import 줄(또는 파일 자체)을 사용 위치로 기록
            lines = [(ln, t) for ff, ln, t in grep(proj["abs"], rf"\b{name}\b", paths=[f])][:1]
            if is_copy_file and not lines:
                lines = [(1, "")]
        authors = []
        for ln, _ in lines:
            add_author(authors, blame(proj["abs"], f, ln))
        for ff, ln, _ in grep(proj["abs"], rf"\b{name}\b", paths=[f]):
            if re.match(r"\s*import ", show_file(proj["abs"], f).split("\n")[ln - 1]):
                add_author(authors, blame(proj["abs"], f, ln))
                break
        if kind != "import":
            add_author(authors, last_author(proj["abs"], f if is_copy_file else next(iter(copy_files), f)))
        hit = False
        if kind == "import" and grade == "breaking" and lines:
            hit = check_hit(proj["abs"], f, name, is_java, hints, lines[0][0])
        usages.append({
            "project": proj["name"], "file": f, "lines": [{"line": ln, "code": t} for ln, t in lines],
            "kind": kind, "copiedFrom": copied_from, "hit": hit, "authors": authors,
        })
    return usages


# ---------------------------------------------------------------- 기능 자산 (⑤)

def feature_classes(asset):
    """기능 자산에서 개발자가 직접 쓰는 시작 클래스(Service·Util 인터페이스)를 고른다."""
    stems = []
    for f in asset.get("files", []):
        if not f.endswith(".java"):
            continue
        stem = os.path.splitext(os.path.basename(f))[0]
        if re.search(r"(Service|Util|Utils|Facade|Client)$", stem):
            stems.append((stem, f))
    if not stems:
        p = asset["path"]
        stems = [(os.path.splitext(os.path.basename(p))[0], p)]
    return stems


def scan_http(proj, endpoints, hints):
    """HTTP로 호출하는 곳. 경로의 고정 부분(첫 { 앞)을 문자열로 찾는다."""
    usages = []
    prefixes = []
    for ep in endpoints:
        m = re.match(r"^(GET|POST|PUT|DELETE|PATCH)\s+(\S+)", ep)
        if not m:
            continue
        fixed = m.group(2).split("{")[0]
        cands = [fixed]
        if proj.get("apiPrefix"):
            cands.append(proj["apiPrefix"] + fixed)
        prefixes.append((m.group(1), fixed, cands))
    seen = set()
    for method, fixed, cands in prefixes:
        for c in cands:
            for f, ln, text in grep(proj["abs"], c, fixed=True):
                if (f, ln) in seen:
                    continue
                window = "\n".join(show_file(proj["abs"], f).split("\n")[max(0, ln - 4):ln + 3])
                if not any(tok in window for tok in HTTP_TOKENS):
                    continue
                if text.strip().startswith(("//", "*", "#")):
                    continue
                seen.add((f, ln))
                authors = []
                add_author(authors, blame(proj["abs"], f, ln))
                hit = any(h in show_file(proj["abs"], f) for h in hints)
                usages.append({
                    "project": proj["name"], "file": f, "lines": [{"line": ln, "code": text.strip()}],
                    "kind": "api-call", "copiedFrom": None, "hit": hit, "authors": authors,
                    "endpoint": f"{method} {fixed}",
                })
    return usages


# ---------------------------------------------------------------- 메인

def scan_asset(item, entry, projects):
    name = item["name"]
    atype = entry.get("type", "")
    origin = entry["path"].replace("common-repo/", "", 1)
    ext = os.path.splitext(origin)[1]
    hints = item["scanHints"]
    methods = [a for a in item["affectedApi"] if re.fullmatch(r"\w+", a)]
    endpoints = [a for a in item["affectedApi"] if re.match(r"^(GET|POST|PUT|DELETE|PATCH)\s", a)]
    if not endpoints and atype.endswith("-feature"):
        endpoints = entry.get("api", [])
    result = {"name": name, "type": atype, "grade": item["grade"], "commits": item["commits"],
              "summaries": item["summaries"], "actions": item["actions"], "scanHints": hints,
              "affectedApi": item["affectedApi"], "usages": [], "projects": []}
    for proj in projects:
        status = {"name": proj["name"], "ok": True, "error": None}
        if not os.path.isdir(proj["abs"]) or not git(proj["abs"], "rev-parse", "--git-dir")[0]:
            status.update(ok=False, error="경로가 없거나 git 저장소가 아님")
            result["projects"].append(status)
            continue
        try:
            if atype.endswith("-feature"):
                for stem, f in feature_classes(entry):
                    result["usages"] += scan_class(proj, stem, os.path.splitext(f)[1],
                                                   f.replace("common-repo/", "", 1), hints, methods, item["grade"])
                if endpoints:
                    result["usages"] += scan_http(proj, endpoints, hints)
            else:
                result["usages"] += scan_class(proj, name, ext, origin, hints, None, item["grade"])
        except Exception as e:  # 한 프로젝트의 실패가 전체를 막지 않게
            status.update(ok=False, error=str(e))
        result["projects"].append(status)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--records", nargs="*", help="asset-index/changes/ 안의 변경 기록 파일")
    ap.add_argument("--assets", nargs="*", help="자산 이름으로 직접 조회 (변경 기록 없이)")
    a = ap.parse_args()
    if not a.records and not a.assets:
        ap.error("--records 또는 --assets가 필요합니다")

    items, new_items = collect_assets(a.records, a.assets)
    index = load_index()
    projects = load_projects() if items else []
    out = {"assets": [], "newAssets": [], "owners": {}, "projects": [{"name": p["name"], "owner": p.get("owner")} for p in projects]}
    for n in new_items:
        out["newAssets"].append({"name": n["name"], "commits": n["commits"], "summaries": n["summaries"]})
    for item in items:
        entry = index.get(item["name"])
        if not entry:
            out["assets"].append({"name": item["name"], "error": "정리집에 없는 자산"})
            continue
        log(f"스캔: {item['name']} ({item['grade']})")
        out["assets"].append(scan_asset(item, entry, projects))
    # 영향 대상이 있는 프로젝트의 담당자
    for asset in out["assets"]:
        for u in asset.get("usages", []):
            for p in projects:
                if p["name"] == u["project"] and p.get("owner"):
                    out["owners"][p["name"]] = p["owner"]
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
