---
name: common-asset-notify
description: 공통팀이 "공통 변경 알림 보내줘", "관련자 알려줘", "<자산> 쓰는 곳 찾아줘", "영향도 분석해줘"라고 할 때, 또는 common-asset-sync가 끝난 뒤 변경 기록(asset-index/changes/)의 관련자 알림을 이어서 진행하기로 했을 때 사용.
---

# 공통 변경 관련자 파악 및 알림

공통 자산의 변경이 **어느 프로젝트의 어느 코드에 영향을 주는지** 실제 소스를 스캔해 찾고,
그 코드를 작성한 개발자와 프로젝트 담당자에게 보낼 알림을 만든다.

- 개발자가 AI로 만들었든 직접 짰든 상관없이 **코드 기준**으로 찾는다.
- 알림은 파일(`asset-index/notifications/`)로만 만든다. 실제 발송(PMS, 메일)은 하지 않는다.
  나중에 PMS를 연동하면 이 파일의 `messages`를 그대로 보낸다.
- 변경 내용 자체(무엇이 어떻게 바뀌었나)는 `common-asset-sync`가 남긴 변경 기록을 그대로 쓴다. 다시 판정하지 않는다.

## 경로

- 변경 기록: `common-repo/asset-index/changes/<해시7>.json` (common-asset-sync가 만든다)
- 정리집: `common-repo/asset-index/asset-index.json` (자산의 path·종류 확인용, 읽기만 한다)
- 프로젝트 목록: `common-repo/asset-index/projects.json` (공통팀이 관리한다)
  - `path`는 common-repo 기준 상대 경로이거나 절대 경로다.
- 알림 파일: `common-repo/asset-index/notifications/<YYYYMMDD>-<해시7들>.json`

## 두 가지 모드

| 모드 | 요청 예 | 하는 일 | 파일 생성 |
|---|---|---|---|
| **알림** | "공통 변경 알림 보내줘", sync 이후 이어서 진행 | 미처리 변경 기록 → 스캔 → 알림 파일 | O (승인 후) |
| **조회** | "Pagination 쓰는 곳 찾아줘", "DateTimeUtils 영향도 알려줘" | 지정한 자산만 스캔 → 결과를 채팅으로 보고 | X |

조회 모드는 아래 2~3단계(스캔, 담당자)만 하고 결과를 표로 보여 준 뒤 끝낸다. 커밋하지 않는다.

## 핵심 원칙

1. **프로젝트 저장소는 읽기만 한다.** 수정, 커밋, 브랜치 변경을 하지 않는다.
2. **커밋된 코드만 스캔한다.** `git -C <프로젝트> grep`, `ls-files`, `blame`을 쓴다. (작업 트리의 미커밋 변경은 보지 않는다.)
3. **찾은 것만 알린다.** 스캔에서 나오지 않은 사용처나 담당자를 지어내지 않는다.
4. **공개되는 결과물에는 깨끗한 문장만 남긴다.** 알림 파일과 메시지에 `(AI 추론)` 같은 표시를 넣지 않는다.
   추론이 필요한 판단(대체 후보 등)은 미리보기에서 `⚠ 추론 — 확인 필요`로 보여 주고, 공통팀이 승인한 것만 넣는다.
5. **사용자 확인은 두 번 받는다: 알림 파일 생성(4단계), push(6단계).**

## 순서 (알림 모드)

### 1. 처리할 변경 기록 모으기
- `asset-index/changes/*.json` 중 `notified`가 `false`인 파일을 읽는다. 커밋 시각(`committedAt`) 순으로 정렬한다.
- 각 파일의 `changes` 중 `grade`가 `docs`인 항목은 알림 대상에서 뺀다.
- 처리할 항목이 없으면 "알릴 변경이 없습니다"라고 알리고 끝낸다.
  (모든 항목이 `docs`인 기록 파일은 4단계 승인 없이 `notified: true`로 바꾸지 않는다. 다음 알림 때 함께 처리한다.)
- `projects.json`을 읽는다. 없거나 프로젝트가 0개면 "projects.json에 스캔할 프로젝트를 등록해 주세요"라고 안내하고 끝낸다.

### 2. 사용처 스캔
항목(자산)마다, 프로젝트마다 아래 [사용처 탐지 규칙]을 적용한다.
- 프로젝트 경로가 없거나 git 저장소가 아니면 건너뛰고 "스캔 실패: <프로젝트> - <이유>"로 기록한다.
- 결과는 사용처 목록이다: 프로젝트, 파일, 줄, 코드 한 줄, 사용 방식(`import` / `copy` / `copy-modified`), `hit` 여부.

### 3. 담당자 파악
아래 [담당자 규칙]을 적용한다.

### 4. 미리보기 (사용자 확인 후)
미리보기 전문을 **채팅 본문**에 먼저 출력한 뒤, 질문 도구로 **"이대로 알림 파일을 만들까요?"** 한 줄만 묻는다.
질문 창에는 긴 내용이 보이지 않는다.
**질문 전 확인**: 바로 위 응답 본문에 `[관련자 알림 미리보기]` 블록 전문이 있는가? 없으면 질문하지 말고 블록부터 출력한다.

```
[관련자 알림 미리보기]
(⚠ 표시는 검토용이며 알림 파일에는 저장되지 않습니다)

■ 🔴 비호환 — Pagination  (635c4ba)
  요약   onChange 인자가 page 숫자에서 { page, pageSize } 객체로 바뀌었습니다.
  할 일  onChange 핸들러가 객체를 받도록 수정하세요.

  영향 대상 3곳 (프로젝트 2개)
  shop-app
    - frontend/src/pages/OrderList.tsx:13    import   onChange 사용 ●   작성 김개발
    - frontend/src/pages/ProductList.tsx:15  import   onChange 사용 ●   작성 박개발
  admin-app
    - frontend/src/components/Pagination.tsx  copy-modified (공통 원본을 복사 후 수정)   작성 이개발
      사용 줄: frontend/src/pages/UserList.tsx:10   작성 이개발
      → 복사본이라 공통 변경이 자동 반영되지 않습니다. 새 버전 반영 여부를 직접 판단해야 합니다.

■ ⚪ 신규 — DateTimeUtils  (b6a0f67)
  대체 후보 1곳  ⚠ 추론 — 확인 필요
    - admin-app  backend/src/main/java/com/admin/util/DateFormat.java   작성 이개발
      근거: DateTimeFormatter.ofPattern("yyyy-MM-dd"), toDate/toDateTime/parse가 DateTimeUtils와 같은 역할
  → 포함할 후보를 골라 주세요. (기본: 모두 제외)

■ 받는 사람 (4명)
  김개발  shop-app   Pagination 🔴
  박개발  shop-app   Pagination 🔴
  이개발  admin-app  Pagination 🔴 (복사본)
  최PL    shop-app   담당자 참조 — Pagination 🔴 2곳
  정PL    admin-app  담당자 참조 — Pagination 🔴 1곳

■ 스캔 결과
  shop-app ✓  admin-app ✓  hr-app ✓ (해당 없음)

■ 알림 파일
  asset-index/notifications/20261014-635c4ba.json

■ 커밋 메시지
  docs: 공통 변경 알림 생성 (635c4ba)

  - Pagination [비호환]: 3곳, 프로젝트 2개, 수신 5명
```

- `●`은 `hit`(스캔 키가 실제로 쓰인 줄)이다. 비호환인데 `hit`가 없는 사용처는 "사용은 하지만 바뀐 부분은 쓰지 않음 — 확인 권장"으로 보여 준다.
- 대체 후보는 **공통팀이 고른 것만** 알림에 넣는다. 고르지 않으면 넣지 않는다.
- 사용자가 수정을 요청하면 고친 뒤 미리보기를 다시 보여 주고 다시 묻는다.
- 사용자가 거절하면 아무 파일도 만들지 않고 변경 기록도 그대로 둔다.
- 영향 대상이 0곳인 항목도 미리보기에 "영향 대상 없음"으로 보여 준다. 승인하면 알림 파일에 그대로 남기고 처리한 것으로 본다.

### 5. 알림 파일 생성과 커밋
승인받은 내용 **그대로** 만든다. `⚠` 표시와 근거 메모는 저장하지 않는다.
- `asset-index/notifications/<YYYYMMDD>-<해시7들>.json`을 만든다. (UTF-8, 들여쓰기 2칸, 형식은 아래 [알림 파일 형식])
  - `<YYYYMMDD>`는 알림을 만든 날짜, `<해시7들>`은 포함된 변경 기록의 해시를 `-`로 이은 것.
- 처리한 변경 기록 파일마다 `notified: true`, `notifiedAt`(지금 시각, ISO 8601), `notification`(알림 파일 이름)을 넣는다.
  파일 편집 도구로 이 세 필드만 고친다. 다른 필드는 건드리지 않는다.
- JSON이 올바른지 확인한다. (common-repo에서 실행)
  `node -e "for (const f of process.argv.slice(1)) JSON.parse(require('fs').readFileSync(f,'utf8')); console.log('JSON OK')" <알림 파일> <변경 기록 파일들>`
- 알림 파일과 고친 변경 기록 파일**만** 커밋한다. 경로는 하나씩 적는다.
  ```
  git -C common-repo add <알림 파일> <변경 기록 파일들>
  git -C common-repo commit -m "<제목>" -m "<본문>" -- <알림 파일> <변경 기록 파일들>
  ```
  - 제목: `docs: 공통 변경 알림 생성 (<해시7들>)`
  - 본문: 자산마다 한 줄. `- <자산> [<등급>]: <N>곳, 프로젝트 <M>개, 수신 <K>명`
  - 메시지는 `-F` 파일 대신 `-m`을 두 번 써서 명령 인자로 넘긴다. 커밋 직후 `git -C common-repo log -1 --format=%B`로 한글이 깨지지 않았는지 확인한다.

### 6. push 확인
- `git -C common-repo log --oneline @{u}..HEAD`로 push 안 된 커밋을 확인한다. upstream이 없으면 묻지 않고 보고에 적는다.
- 있으면 목록을 보여 주고 **"push할까요?"** 를 한 번만 묻는다.

### 7. 결과 보고
- 알림 파일 이름
- 자산별 등급과 영향 대상 수 (프로젝트, 파일)
- 받는 사람 목록
- 스캔 실패한 프로젝트와 이유
- push 결과

## 사용처 탐지 규칙

자산의 `name`을 `<Name>`이라 한다. 공통 원본 경로는 정리집의 `path`에서 `common-repo/`를 뺀 것이다 (예: `components/Pagination.tsx`).
모든 검색은 `git -C <프로젝트> grep -n -E "<패턴>"`과 `git -C <프로젝트> ls-files`로 한다. (추적되는 파일만 검색되므로 node_modules·빌드 산출물은 자동으로 빠진다.)

### ① 복사본 찾기
- `git -C <프로젝트> ls-files`에서 파일 이름이 공통 원본과 같은 파일(`<Name>.tsx` 또는 `<Name>.java`)을 찾는다.
- 그 파일 안에 `export function <Name>` / `export const <Name>` / `class <Name>`이 있어야 복사본으로 본다. (이름만 같은 다른 파일 제외)
- 복사본이 공통 원본의 어느 버전과 같은지 확인한다.
  ```
  git -C <프로젝트> hash-object <복사본 경로>                                  → <blob>
  git -C common-repo log --format="%h %cI" --find-object=<blob> -- <공통 원본 경로>
  ```
  - 결과가 있으면 `copy`. 첫 줄의 해시를 `copiedFrom`으로 기록한다. (그 버전을 수정 없이 복사한 것)
  - 결과가 없으면 `copy-modified`. (복사한 뒤 수정한 것)
  - 줄바꿈 차이(CRLF/LF)는 `hash-object`가 정규화하므로 신경 쓰지 않는다.

### ② import 찾기
- TS: `git -C <프로젝트> grep -n -E "import .*\b<Name>\b.* from ['\"][^'\"]*/<Name>['\"]"`
- Java: `git -C <프로젝트> grep -n -E "^import [a-zA-Z0-9_.]+\.<Name>;"`
- import 경로로 출처를 구분한다.
  - 공통 패키지(TS 경로에 `common`이 들어간 패키지 경로, Java `com.company.common.`)이면 → 사용 방식 `import`
  - ①에서 찾은 복사본을 가리키면(상대 경로나 프로젝트 패키지) → 그 복사본의 사용 방식(`copy` / `copy-modified`)
  - 둘 다 아니면(다른 라이브러리의 같은 이름) → 사용처가 아니다. 버린다.
- Java는 같은 패키지 안에서 import 없이 쓸 수 있다. 복사본과 같은 패키지에 있는 파일은 ③의 사용 줄 패턴으로 직접 확인한다.

### ③ 사용 줄 찾기
②에서 찾은 파일마다 실제로 쓰는 줄을 찾는다. import 줄은 사용 줄이 아니다.
- 프론트: `<<Name>[ />]`, `<<Name>$`
- 백엔드: `\b<Name>\.`, `new <Name>\(`, `\b<Name><`, 변수·인자 타입 선언 `\b<Name> [a-z]`
- 한 파일에 사용 줄이 여러 개면 모두 기록한다. 하나도 없으면 import 줄을 사용 위치로 기록한다.

### ④ 정밀 확인 (`breaking` 항목만)
변경 기록의 `scanHints`(바뀐 prop·메서드 이름)가 사용 줄에서 쓰이는지 확인한다.
- 프론트: 사용 줄부터 그 JSX 요소가 닫힐 때까지(`/>` 또는 `</<Name>>`) 안에 `<hint>=` 또는 `<hint>:`가 있으면 `hit`
- 백엔드: `<Name>.<hint>(`, `.<hint>(` (사용 줄의 변수에 대해)가 있으면 `hit`
- 판단이 어려우면 파일을 읽어 확인한다. 그래도 애매하면 `hit: false`로 두고 미리보기에서 "확인 권장"으로 보여 준다.

### ⑤ 대체 후보 (`new` 항목만)
새 자산이 하는 일을 프로젝트가 **직접 구현한** 곳을 찾는다. 자산의 소스(`git -C common-repo show HEAD:<공통 원본 경로>`)를 읽고
핵심 구현을 나타내는 검색어를 정한다.
- 예: DateTimeUtils → `DateTimeFormatter.ofPattern\("yyyy-MM-dd`, `formatDate|toDate|parseDate`
- 예: MaskingUtils → `replaceAll\(.*\*`, `mask[A-Z]`
- ①②에서 이미 이 자산을 쓰는 파일은 뺀다.
- 결과는 항상 추론이다. 미리보기에서 `⚠ 추론 — 확인 필요`와 근거(검색에 걸린 코드)를 함께 보여 주고, 공통팀이 고른 것만 넣는다.

## 담당자 규칙

- **작성자**: 사용 줄마다 blame으로 찾는다.
  ```
  git -C <프로젝트> blame -L <줄>,<줄> --porcelain -- <파일>
  ```
  출력의 `author`, `author-mail`(앞뒤 `<>` 제거)을 쓴다.
  - import 줄과 사용 줄의 작성자가 다르면 둘 다 넣는다.
  - `copy` / `copy-modified`이면 복사본 파일을 마지막으로 커밋한 사람(`git -C <프로젝트> log -1 --format="%an|%ae" -- <복사본>`)도 넣는다.
  - `Not Committed Yet`은 미커밋 줄이므로 원칙 2에 따라 나오지 않는다. 나오면 그 줄은 버린다.
- **프로젝트 담당자**: `projects.json`의 `owner`를 `role: "owner"`로 넣는다. 영향 대상이 있는 프로젝트의 담당자만 넣는다.
- 같은 사람(이메일 기준)은 한 번만 센다.

## 알림 파일 형식

```json
{
  "id": "20261014-635c4ba",
  "createdAt": "2026-10-14T11:00:00+09:00",
  "sourceCommits": ["635c4ba"],
  "items": [
    {
      "asset": "Pagination",
      "type": "frontend-component",
      "commit": "635c4ba",
      "grade": "breaking",
      "summary": "onChange 인자가 page 숫자에서 { page, pageSize } 객체로 바뀌었습니다.",
      "action": "onChange 핸들러가 객체를 받도록 수정하세요. 예: onChange={({ page }) => setPage(page)}",
      "targets": [
        {
          "project": "shop-app",
          "pmsProjectId": null,
          "file": "frontend/src/pages/OrderList.tsx",
          "line": 13,
          "code": "<Pagination page={page} totalPages={totalPages} onChange={setPage} />",
          "usageKind": "import",
          "hit": true,
          "recipients": [
            { "name": "김개발", "email": "kim.dev@example.com", "role": "author" }
          ]
        }
      ],
      "candidates": []
    }
  ],
  "scanErrors": [],
  "messages": [
    {
      "to": { "name": "김개발", "email": "kim.dev@example.com" },
      "role": "author",
      "project": "shop-app",
      "pmsProjectId": null,
      "title": "[공통 변경] Pagination 비호환 변경 - 수정 필요",
      "body": "공통 컴포넌트 Pagination이 변경되어 작성하신 코드의 수정이 필요합니다.\n\n■ 변경 내용\nonChange 인자가 page 숫자에서 { page, pageSize } 객체로 바뀌었습니다.\n\n■ 할 일\nonChange 핸들러가 객체를 받도록 수정하세요. 예: onChange={({ page }) => setPage(page)}\n\n■ 해당 위치\n- shop-app frontend/src/pages/OrderList.tsx:13\n\n(공통 변경 커밋: 635c4ba)"
    }
  ]
}
```

- `targets[].usageKind`: `import` / `copy` / `copy-modified`. 복사본이면 `copyFile`(복사본 경로)과 `copiedFrom`(`copy`일 때만)을 함께 넣는다.
- `hit`: `breaking` 항목에서만 넣는다.
- `candidates`: `new` 항목에서 공통팀이 고른 대체 후보. `{ "project", "file", "line", "code", "recipients" }`
- `messages`: **받는 사람 × 프로젝트**마다 하나. 한 사람이 같은 프로젝트에서 여러 자산에 해당하면 한 메시지로 묶는다.
  - `title`: `[공통 변경] <자산들> <가장 높은 등급 이름> - <요청 수준>`
    - 요청 수준: 🔴 `수정 필요`, 🟡 `확인 필요`, 🟢 `참고`, ⚪ `도입 검토`
  - `body`: 사람이 읽는 본문. 순서: 인사 한 줄 → `■ 변경 내용` → `■ 할 일` → `■ 해당 위치` → 커밋 해시.
    - 복사본이면 `■ 할 일`에 "복사해서 쓰는 파일이라 공통 변경이 자동으로 반영되지 않습니다."를 덧붙인다.
    - 담당자(`owner`) 메시지는 그 프로젝트의 모든 해당 위치와 작성자를 나열하는 요약으로 쓴다.
  - 등급 표시에는 이모지 대신 `[비호환]`, `[동작 변경]`, `[호환 추가]`, `[신규]`를 쓴다. (PMS에서 깨지지 않게)

## 하지 말 것
- 프로젝트 저장소를 수정하거나, 프로젝트 저장소에서 커밋·checkout·pull 하지 않는다.
- 실제로 메일, 메신저, PMS로 보내지 않는다.
- 변경 기록의 `notified`·`notifiedAt`·`notification` 외 필드를 고치지 않는다. 정리집(`asset-index.json`)을 고치지 않는다.
- 스캔에서 나오지 않은 사용처나 담당자를 넣지 않는다.
- 공통팀이 고르지 않은 대체 후보를 알림에 넣지 않는다.
