# 알림 메시지 초안(asset-index/messages/*.json)을 Slack DM으로 보낸다. 표준 라이브러리만 사용.
# 사용: python tools/send_slack.py <메시지 파일> [--dry-run] [--resend] [--to 이름,이름]
#   --resend: 이미 보낸 메시지도 다시 보낸다 (재전송)
#   --to 김개발,이개발: 지정한 수신자에게만 보낸다 (없으면 파일의 수신자 전원)
#   토큰: 환경변수 SLACK_BOT_TOKEN 또는 common-repo/.slack-token (한 줄, git 제외)
#   수신자 매핑: asset-index/slack-users.json  {"김개발": "U...."}  (비밀 아님)
import json, os, ssl, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS = os.path.join(ROOT, "asset-index", "slack-users.json")
TOKEN_FILE = os.path.join(ROOT, ".slack-token")
CONFIG = os.path.join(ROOT, "asset-index", "slack-config.json")  # {"senderName": "공통 안내"} (선택)

def sender_name():
    try:
        with open(CONFIG, encoding="utf-8") as f:
            return json.load(f).get("senderName") or None
    except Exception:
        return None

def read_token():
    t = os.environ.get("SLACK_BOT_TOKEN", "").strip()
    if not t and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, encoding="utf-8") as f:
            t = f.read().strip()
    return t

def _call(token, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request("https://slack.com/api/chat.postMessage", data=body, method="POST",
        headers={"Authorization": "Bearer " + token, "Content-Type": "application/json; charset=utf-8"})
    with urllib.request.urlopen(req, timeout=15, context=ssl.create_default_context()) as r:
        return json.loads(r.read().decode("utf-8"))

def post(token, channel, text):
    payload = {"channel": channel, "text": text, "mrkdwn": False}
    name = sender_name()
    if name:  # 보낸 사람 이름 지정 (chat:write.customize 권한 필요). 권한이 없으면 이름 없이 다시 보낸다.
        res = _call(token, dict(payload, username=name))
        if res.get("ok") or res.get("error") != "missing_scope":
            return res
    return _call(token, payload)

def main():
    argv = sys.argv[1:]
    only = None
    if "--to" in argv:
        i = argv.index("--to")
        only = {n.strip() for n in (argv[i + 1] if i + 1 < len(argv) else "").split(",") if n.strip()}
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    dry = "--dry-run" in sys.argv
    resend = "--resend" in sys.argv
    if not args:
        print("사용: python tools/send_slack.py <메시지 파일> [--dry-run] [--resend]"); sys.exit(2)
    path = args[0]
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    with open(USERS, encoding="utf-8") as f:
        users = json.load(f)
    token = "" if dry else read_token()
    if not dry and not token:
        print("오류: Slack 토큰이 없습니다. common-repo/.slack-token 파일 또는 SLACK_BOT_TOKEN을 설정하세요."); sys.exit(1)

    sent = skipped = failed = 0
    for m in doc.get("messages", []):
        name = m["recipient"]["name"]
        if only is not None and name not in only:
            continue
        first = m["text"].split("\n")[0]
        again = bool(m.get("sentAt"))
        if again and not resend:
            print(f"[이미 보냄] {name} — {first}"); sent += 1; continue
        uid = users.get(name)
        if not uid:
            print(f"[건너뜀] {name} — Slack 계정 매핑 없음"); skipped += 1; continue
        if dry:
            print(f"[{'다시 보낼 예정' if again else '보낼 예정'}] {name} → {uid} — {first}"); continue
        try:
            res = post(token, uid, m["text"])
        except Exception as e:
            print(f"[실패] {name} — {e}"); failed += 1; continue
        if res.get("ok"):
            m["sentAt"] = time.strftime("%Y-%m-%dT%H:%M:%S+09:00")
            m["slackTs"] = res.get("ts")
            m["sendCount"] = m.get("sendCount", 1 if again else 0) + 1
            print(f"[{'재전송' if again else '전송'}] {name} — {first}"); sent += 1
        else:
            print(f"[실패] {name} — {res.get('error')}"); failed += 1
    if only is not None:
        found = {m["recipient"]["name"] for m in doc.get("messages", [])}
        for n in sorted(only - found):
            print(f"[없음] {n} — 이 파일에 받는 사람으로 없음")
    else:
        for b in doc.get("broadcasts", []):
            print(f"[건너뜀] 전체 공지 {b['asset']} — 받는 곳 미정"); skipped += 1

    if dry:
        print("미리보기만 했습니다. 전송하지 않았습니다."); return
    all_sent = all(m.get("sentAt") for m in doc.get("messages", [])) and not doc.get("broadcasts")
    doc["status"] = "sent" if (failed == 0 and all_sent) else ("partial" if any(m.get("sentAt") for m in doc.get("messages", [])) else doc.get("status", "draft"))
    if sent:
        doc["sentAt"] = time.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"전송 {sent}건, 건너뜀 {skipped}건, 실패 {failed}건 · status={doc['status']}")

main()
