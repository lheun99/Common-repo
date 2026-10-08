---
name: common-asset-sync
description: 공통팀이 "공통 자산 정리해줘"라고 하면 사용. common-repo 변경분을 커밋하고, 커밋 내용과 소스를 읽어 common-repo/asset-index/의 공통 자산 정리집(asset-index.json)을 갱신한 뒤 정리집도 커밋한다. 사람이 직접 커밋해서 밀려 있는 커밋도 함께 정리한다.
---

# 공통 자산 정리 (커밋 + 정리집 갱신)

이 문서 하나에 절차와 정리집 작성 규칙이 모두 들어 있다. 다른 지시 파일을 찾지 않는다.

## 경로

모든 작업은 `common-repo` 저장소 **하나** 안에서 끝난다. (이 스킬이 들어 있는 저장소)

- 공통 코드: `common-repo/components/`, `common-repo/backend/`
- 정리집 폴더: `common-repo/asset-index/`
  - 정리집: `asset-index/asset-index.json`
  - 로그: `asset-index/automation.log`
- 밀린 커밋 대기열: `common-repo/.git/common-asset-pending.txt`
  (post-commit 훅이 `components/`·`backend/`가 바뀐 커밋의 해시를 한 줄씩 적어 둔다. 사람이 직접 커밋한 것도 여기에 쌓인다.)

## 핵심 원칙

1. **정리집은 커밋된 내용만 기준으로 한다.** 커밋되지 않은 파일(작업 트리의 수정본, untracked 파일)은
   정리 대상이 아니다. 소스는 항상 `git show <해시>:<경로>`로 그 커밋 시점의 내용을 읽는다.
2. **확실한 것만 반영하고, 애매하면 로그에 "판단 보류"로 남긴다.**
3. **소스에 없는 내용을 지어내지 않는다.** 추론한 부분은 반드시 표시한다.
4. **사용자 확인은 세 번 받는다: 공통 코드 커밋(2단계), 정리집 반영(5단계), push(7단계).** 정리집 내용은 이
   문서의 규칙대로 먼저 구성하고, 반영 전에 한 번에 보여 준다. 항목 하나하나를 따로 묻지 않는다.
   push는 모든 커밋이 끝난 뒤 **마지막에 한 번만** 묻는다.

## 순서

### 1. 커밋할 파일 확인 (사용자가 stage한 파일만)
커밋 대상은 **사용자가 미리 `git add`로 stage해 둔 파일뿐**이다. 무엇을 커밋할지는 사용자가 정한다.
- `git -C common-repo diff --cached --name-status`로 stage된 파일을 확인한다.
- `git -C common-repo diff --cached`로 stage된 변경 내용을 읽는다.
- stage되지 않은 수정 파일과 untracked 파일은 **커밋 대상이 아니다.** 목록에 넣지 않고, 내용도 읽지 않는다.
- stage된 파일이 **없으면** 커밋하지 않는다. "커밋할 파일을 `git add`로 올려 두면 함께 커밋합니다"라고 한 줄
  안내한 뒤 3단계(밀린 커밋 정리)로 간다.

### 2. 공통 코드 커밋 (사용자 확인 후)
- stage된 변경 내용을 보고 아래 **[커밋 메시지 형식]** 의 "공통 코드 커밋" 형식으로 메시지를 작성한다.
- 사용자에게 아래를 보여 주고 **"이대로 커밋할까요?"** 를 묻는다. (push는 여기서 묻지 않는다.)
  - stage된 파일 목록 (상태 포함)
  - 그중 정리집 대상(`components/*.tsx`, `backend/*.java`)인 파일
  - 커밋 메시지 전체 (제목 + 본문)
- stage된 파일 중 정리집 대상이 아닌 파일(설정, 문서 등)이 섞여 있으면 "정리집 대상이 아닌 파일도 함께
  커밋됩니다"라고 알려 준다. 빼거나 넣는 것은 사용자가 직접 한다.
- 승인받으면 **stage된 그대로** 커밋한다. 메시지는 아래 [커밋 메시지 형식]의 "커밋하는 방법"을 따른다.
  - `git add`를 추가로 하지 않는다. (`git add -A`, `git add .` 금지)
  - `git commit -a`나 `git commit <경로>`를 쓰지 않는다. (stage되지 않은 변경까지 커밋된다.)
- 커밋하면 post-commit 훅이 해시를 대기열에 자동으로 추가한다.
- 사용자가 커밋을 거절하면 그 변경분은 정리하지 않는다. (원칙 1) 3단계로 가서 밀린 커밋만 정리한다.

### 3. 정리 대상 커밋 모으기
- 대기열 파일의 해시 목록을 읽는다. (파일이 없거나 비어 있으면 정리할 것이 없다고 알리고 7단계(push 확인)로 간다.)
- 이미 정리집에 반영된 해시(`addedInCommit` 또는 `updatedInCommit`에 있는 것)는 건너뛴다.
- 여러 개면 오래된 커밋부터 순서대로 처리한다. (`git -C common-repo log --reverse --format=%H`의 순서)

### 4. 정리집 내용 구성 (아직 파일에 쓰지 않음)
커밋마다 다음을 수행한다. 이 단계에서는 `asset-index.json`과 로그를 **수정하지 않는다.**

1. 커밋 정보를 확인한다.
   - `git -C common-repo show --stat --format="%H%n%cI%n%s" <해시>` → 해시, 커밋 시각(ISO 8601), 메시지
   - `git -C common-repo diff-tree --no-commit-id --name-status -r <해시>` → 파일별 상태(A 추가 / M 수정 / D 삭제 / R 이름 변경)
2. 바뀐 파일마다 아래 **[정리집 작성 규칙]** 의 "자산 판별"로 대상인지 가린다.
3. 대상 파일의 소스를 `git -C common-repo show <해시>:<경로>`로 읽는다.
   (수정(M)이면 비교를 위해 `git -C common-repo show <해시>~1:<경로>`도 읽는다.)
4. 규칙에 따라 대상 파일마다 **추가 / 갱신 / 판단 보류** 중 하나로 정하고, 반영할 내용을 만든다.
   - 추가: 새 항목 JSON 전체
   - 갱신: 바뀌는 필드의 이전 값과 새 값
   - 판단 보류: 이유
   - 그리고 남길 로그 줄과 정리집 커밋 메시지

### 5. 반영 전 미리보기 (사용자 확인 후)
4단계에서 만든 내용을 아래 형식으로 **한 번에** 보여 주고 **"이대로 정리집에 반영할까요?"** 를 묻는다.

> **미리보기는 질문 도구 안에 넣지 않는다.** 질문 창에는 긴 내용이 보이지 않는다.
> 1) 먼저 미리보기 전문을 **일반 응답 메시지(채팅 본문)** 로 출력한다.
> 2) 그다음 질문 도구로는 "위 미리보기대로 정리집에 반영할까요?" 한 줄만 묻는다.
> 미리보기를 출력하지 않고 질문부터 하면 안 된다. 2단계 커밋 질문도 같은 방식으로, 파일 목록과 커밋
> 메시지를 본문에 먼저 출력한 뒤 묻는다.

미리보기는 **사람이 읽는 화면**이다. JSON을 그대로 보여 주지 않는다. 필드마다 제목을 달고, `detail`은
[detail 작성 형식]의 섹션 그대로 줄을 나눠 보여 준다. (실제 저장은 6단계에서 JSON으로 한다.)

```
[정리집 반영 미리보기]

■ 추가 — DateTimeUtils (backend-module)
  커밋  b6a0f67 (2026-10-08T05:43:23+01:00)
  경로  common-repo/backend/DateTimeUtils.java

  ▸ purpose
    공통 날짜/시간 변환 유틸 클래스.

  ▸ usage (public 메서드 4개 중 3개)
    - public static LocalDate parseDate(String text)
    - public static String formatDate(LocalDate date)
    - public static String formatDateTime(LocalDateTime dateTime)

  ▸ detail
    [설명]
    - 화면과 API에서 주고받는 날짜 문자열 형식을 회사 표준(yyyy-MM-dd, yyyy-MM-dd HH:mm:ss)으로 통일한다.
    - 각 서비스에서 DateTimeFormatter를 따로 만들지 말고 이 클래스를 사용한다.
    [사용 예]
      LocalDate d = DateTimeUtils.parseDate("2026-10-08");
      String s = DateTimeUtils.formatDateTime(LocalDateTime.now());
    [주의]
    - 모든 메서드는 서버 기본 시간대 기준이다. 시간대 변환이 필요하면 호출부에서 처리한다.
    [메서드]
    - parseDate(text): yyyy-MM-dd 형식의 날짜 문자열 → LocalDate. 형식이 맞지 않거나 null이면 IllegalArgumentException
    - formatDate(date): yyyy-MM-dd 형식 문자열 (date가 null이면 빈 문자열)
    - formatDateTime(dateTime): yyyy-MM-dd HH:mm:ss 형식 문자열 (dateTime이 null이면 빈 문자열)
    - isValidRange(from, to): 기간 검색 조건 검증용. 시작일이 종료일보다 늦으면 false. 단, 둘 중 하나라도 null이면 true

  ▸ 필드 출처
    purpose ← 클래스 Javadoc 첫 문장
    usage   ← public 메서드 시그니처 (isValidRange 제외: 최대 3개)
    detail  ← 클래스 Javadoc 본문·사용 예시·주의, 메서드 Javadoc 4개

■ 갱신 — Pagination (frontend-component)
  커밋  1a2b3c4 (2026-10-09T10:00:00+09:00)
  ▸ props
    이전: page, totalPages, onChange
    이후: page, totalPages, pageSize, onChange

■ 판단 보류 — components/Alert.tsx
  커밋  48daac6
  이유  같은 이름의 항목이 이미 있음

■ 로그에 추가할 줄
  [2026-10-08T05:43:23+01:00] commit b6a0f67 → index에 DateTimeUtils(backend-module) 추가함

■ 정리집 커밋 메시지
  docs: 공통 자산 정리집 갱신 (b6a0f67)

  - 추가: DateTimeUtils(backend-module) ← b6a0f67
```

- 각 항목에 **필드 출처**(어느 주석·interface·메서드에서 가져왔는지)를 붙인다. `(AI 추론)`이 들어간
  필드가 있으면 출처에 "추론"이라고 밝힌다.
- `usage`에서 빠진 메서드가 있으면 무엇이 빠졌는지 출처에 적는다.
- 사용자가 **수정을 요청**하면 그대로 고친 뒤 미리보기를 다시 보여 주고 다시 묻는다.
  단, 소스에 없는 내용을 넣어 달라는 요청이면 `(사용자 입력)`을 붙여 반영한다.
- 사용자가 **거절**하면 정리집과 로그를 건드리지 않고, 대기열도 그대로 둔다. (다음 실행 때 다시 정리된다.)
  2단계에서 만든 커밋이 있으면 7단계(push 확인)로 간다.
- 정리할 대상 파일이 하나도 없고 판단 보류도 없으면 미리보기 없이 "정리집에 반영할 내용이 없습니다"라고 알리고 7단계로 간다.

### 6. 정리집 반영과 커밋
승인받은 내용 **그대로** 반영한다. 미리보기에 없던 내용을 더하거나 빼지 않는다.
- `asset-index/asset-index.json`을 **UTF-8**, 들여쓰기 2칸의 올바른 JSON으로 저장한다.
  - JSON 외의 텍스트(설명, 마크다운 코드펜스 등)는 파일에 남기지 않는다.
  - **기존 서식을 유지한다.** `props`는 한 줄 배열(`["a", "b"]`), `usage`는 한 줄에 하나씩 쓴다.
    바뀌지 않은 항목의 줄바꿈·순서가 달라지면 안 된다. (파일 전체를 다시 직렬화하는 셸 명령
    `ConvertTo-Json` 등은 쓰지 않는다. 파일 편집 도구로 해당 항목만 고친다.)
  - **새 항목은 `assets` 배열의 맨 끝에 추가한다.** 마지막 항목의 닫는 `}` 뒤에 `,`를 붙이고 그 뒤에 넣는다.
    다른 항목의 중간에 끼워 넣지 않는다.
  - 저장한 뒤 **JSON이 올바른지 반드시 확인한다.**
    `node -e "JSON.parse(require('fs').readFileSync('asset-index/asset-index.json','utf8')); console.log('JSON OK')"`
    (common-repo에서 실행) 이 `JSON OK`를 출력하지 않으면 커밋하지 말고 고친 뒤 다시 확인한다.
- `asset-index/automation.log`에 미리보기의 로그 줄을 추가한다. 대상 파일마다 반드시 한 줄(추가·갱신·판단 보류 중 하나)이 남아야 한다.
- 정리집 두 파일**만** 커밋한다. 이때만 스킬이 직접 `git add`를 한다.
  ```
  git -C common-repo add asset-index/asset-index.json asset-index/automation.log
  git -C common-repo commit -m "<제목>" -m "<본문>" -- asset-index/asset-index.json asset-index/automation.log
  ```
  - 끝의 `-- <경로>`는 빼지 않는다. 사용자가 stage해 두고 2단계에서 커밋을 거절한 파일이 있어도 정리집 커밋에
    섞이지 않게 한다.
  - 메시지: 아래 [커밋 메시지 형식]의 "정리집 커밋" 형식 (제목 + 본문)
  - 정리집 커밋은 `components/`·`backend/`를 바꾸지 않으므로 훅이 대기열에 넣지 않는다.
- 처리한 해시를 대기열 파일에서 지운다. (판단 보류만 나온 커밋도 처리한 것으로 보고 지운다.)
  - 파일 편집 도구로 해당 줄만 지운다. 남은 해시가 없으면 **완전히 빈 파일**로 둔다. (`""`, 공백, 빈 줄을 남기지 않는다.)
  - 대기열을 읽을 때 40자리 16진수 해시가 아닌 줄은 무시한다.

### 7. push 확인 (마지막에 한 번)
- push 안 된 커밋을 확인한다: `git -C common-repo log --oneline @{u}..HEAD`
- push할 커밋이 하나도 없으면 묻지 않고 8단계로 간다.
- 있으면 커밋 목록을 채팅 본문에 보여 준 뒤 **"push할까요?"** 를 한 번만 묻는다.
- 승인받으면 `git -C common-repo push`를 한다. (코드 커밋과 정리집 커밋이 함께 올라간다.)
- 거절하면 push하지 않는다. 다음 실행 때 push 안 된 커밋으로 다시 확인된다.

### 8. 결과 보고
- 커밋한 내용 (코드 커밋, 정리집 커밋 각각의 해시)
- 정리집에 추가되거나 갱신된 자산 이름과 종류
- 판단 보류한 항목과 그 이유
- push 결과

## 커밋 메시지 형식

두 커밋 모두 **제목 한 줄 + 빈 줄 + 본문**으로 쓴다. 본문에는 이 커밋에 무엇이 반영됐는지 한 줄씩 적는다.
본문 내용은 diff와 소스에서 확인한 사실만 쓰고, 한 줄은 짧게(한 문장) 쓴다.

### 공통 코드 커밋 (common-repo)
- 제목: `<feat|fix|refactor|docs|chore>: <요약>` (예: `feat: Spinner 컴포넌트 추가`)
- 본문: stage된 파일마다 한 줄. `- <자산명 또는 파일 경로>: <무엇을 했는지>`

```
feat: Spinner 컴포넌트 추가

- Spinner: 로딩 스피너 신규 추가 (size/label/overlay props)
- CEN.md: 정리 흐름 설명을 stage 기준으로 수정
```

### 정리집 커밋 (common-repo, asset-index/ 두 파일)
- 제목: `docs: 공통 자산 정리집 갱신 (<짧은 해시들>)`
- 본문: 정리집에 반영한 결과를 한 줄씩. 추가·갱신·판단 보류가 없는 줄은 쓰지 않는다.

```
docs: 공통 자산 정리집 갱신 (48daac6)

- 추가: Spinner(frontend-component) ← 48daac6
- 갱신: Pagination(frontend-component) props에 pageSize 추가 ← 1a2b3c4
- 판단 보류: components/Alert.tsx - 같은 이름의 항목이 이미 있음 ← 48daac6
```

### 커밋하는 방법
메시지를 파일에 써서 `-F`로 넘기지 않는다. (Windows PowerShell이 파일을 CP949로 저장해 한글이 깨진다.)
`-m`을 두 번 써서 제목과 본문을 **명령 인자로 직접** 넘긴다. 본문은 줄바꿈을 포함한 하나의 문자열로 쓴다.

```
git -C <저장소> commit -m "feat: Spinner 컴포넌트 추가" -m "- Spinner: 로딩 스피너 신규 추가 (size/label/overlay props)
- CEN.md: 정리 흐름 설명을 stage 기준으로 수정"
```

커밋 직후 `git -C <저장소> log -1 --format=%B`로 메시지를 다시 읽어 **한글이 깨지지 않았는지 확인**한다.
깨졌으면 push하지 말고 사용자에게 알린다.

## 정리집 작성 규칙

### 자산 판별

diff에 나오는 경로는 `common-repo` **내부 기준**이라 `common-repo/` 접두사가 없다 (예: `backend/PageRequest.java`).
정리집의 `path` 필드에는 항상 `common-repo/`를 붙인 전체 경로를 적는다 (예: `common-repo/backend/PageRequest.java`).

| 종류 (`type`) | diff상 경로 패턴 | 정리집 `path` | 예 |
|---|---|---|---|
| `frontend-component` | `components/*.tsx` | `common-repo/components/*.tsx` | Button, Pagination |
| `backend-module` | `backend/*.java` | `common-repo/backend/*.java` | ApiResponse, GlobalExceptionHandler |

둘 다 아닌 파일(설정, 스크립트, 문서, 테스트 등)은 정리 대상이 아니므로 무시한다.

### 파일 상태별 처리

| 상태 | 처리 |
|---|---|
| A (추가) | 새 항목을 추가한다. 같은 `name`이 이미 있으면 추가하지 않고 판단 보류로 남긴다. |
| M (수정) | 이전 소스(`<해시>~1`)와 비교해 정리집에 적힌 필드(`props`/`usage`/`purpose`/`detail`)가 실제로 달라졌을 때만 해당 항목을 갱신한다. 정리집에 항목이 없던 자산이면 새 항목으로 추가한다. |
| D (삭제) | 항목을 지우지 않고 판단 보류로 남긴다. (삭제 반영 여부는 사람이 결정한다.) |
| R (이름 변경/이동) | 추가하지 않고 판단 보류로 남긴다. |

diff에서 바뀌지 않은 기존 항목은 절대 건드리지 않는다.

### 필드 추출 (코드에서 그대로, 추측 금지)

**frontend-component**
- `name`: 컴포넌트 함수/export 이름
- `path`: `common-repo/`를 붙인 전체 경로
- `props`: 컴포넌트가 받는 Props interface/type(예: `TabsProps`)에 정의된 prop 이름 목록.
  prop 안에서 쓰는 보조 타입(예: `items: TabItem[]`의 `TabItem`)의 필드는 `props`에 넣지 않고,
  `detail`의 `[props]`에 `- items[].key: <주석>` 형태로 넣는다.
- `purpose`: 파일 상단 주석의 **첫 문장 하나**. 없으면 props 구성으로 미루어 한 줄 요약하고 끝에 ` (AI 추론)`을 붙인다.
- `detail`: 코드 안의 **모든** 주석(상단 주석의 나머지 문장, prop별 인라인 설명, 사용 예시, 주의사항 등)을 빠짐없이 모아
  아래 [detail 작성 형식]으로 정리한다. 개발자가 실제로 적어 둔 내용만 담는다. `purpose` 외에 코드에 적힌 게 없으면 `null`.

**backend-module**
- `name`: public 클래스 이름
- `path`: `common-repo/`를 붙인 전체 경로
- `usage`: 다른 코드에서 이 클래스를 쓰는 방법. public 메서드/생성자 시그니처를 그대로, 최대 3개.
- `usage`에는 public만 넣는다. private/protected 생성자·메서드는 넣지 않는다.
- `purpose`: 클래스 상단 Javadoc의 **첫 문장 하나**. 없으면 클래스명·메서드 구성으로 미루어 한 줄 요약하고 끝에 ` (AI 추론)`을 붙인다.
- `detail`: Javadoc의 나머지 설명, `@param`/`@return`/`@throws`, 메서드별 주석, 예시 코드, "주의"·"단" 같은 개발자의
  당부까지 빠짐없이 모아 아래 [detail 작성 형식]으로 정리한다. 개발자가 실제로 적어 둔 내용만 담는다. 그 이상 설명이 없으면 `null`.

### detail 작성 형식

`detail`은 한 덩어리 문장으로 이어 붙이지 않는다. 아래 섹션 순서로 **줄을 나눠** 쓴다.
JSON에는 줄바꿈을 `\n`으로 넣은 하나의 문자열로 저장한다. 내용이 없는 섹션은 통째로 뺀다.

| 섹션 | 담는 내용 | 쓰는 법 |
|---|---|---|
| `[설명]` | 상단 주석 중 purpose(첫 문장)를 뺀 나머지 설명 | 문장마다 `- `로 시작하는 한 줄 |
| `[사용 예]` | 주석에 적힌 예시 코드 | 코드를 고치지 않고 줄마다 앞에 공백 2칸 |
| `[주의]` | "주의", "단", "반드시" 등 개발자의 당부 | 항목마다 `- ` 한 줄 |
| `[props]` (프론트) | prop별 주석 | `- <prop>: <주석>` 한 줄씩, interface에 적힌 순서대로 |
| `[메서드]` (백엔드) | 메서드별 Javadoc, `@param`/`@return`/`@throws` | `- <메서드명>(<인자명>): <설명>` 한 줄씩, 소스 순서대로 |

- **주석 문구를 그대로 옮긴다.** 띄어쓰기를 바꾸지 않는다. 특히 영문·숫자·기호 뒤에 붙은 조사를 띄우지 않는다.
  - 틀림: `API 에서`, `null 이면`, `items 의 key 는`, `onChange 가`, `index 에`
  - 맞음: `API에서`, `null이면`, `items의 key는`, `onChange가`, `index에`
  - 미리보기를 출력하기 전에 `purpose`·`detail`·로그 줄을 소스 주석과 대조해, 영문 뒤 조사 앞에 공백이 생겼으면 붙인다.
- 사용 예시가 주석에 있으면 반드시 `[사용 예]`에 넣는다. 빠뜨리지 않는다.
- 같은 문장을 `purpose`와 `detail`에 중복해서 쓰지 않는다.

저장 예 (DateTimeUtils):

```json
"purpose": "공통 날짜/시간 변환 유틸 클래스.",
"detail": "[설명]\n- 화면과 API에서 주고받는 날짜 문자열 형식을 회사 표준(yyyy-MM-dd, yyyy-MM-dd HH:mm:ss)으로 통일한다.\n- 각 서비스에서 DateTimeFormatter를 따로 만들지 말고 이 클래스를 사용한다.\n[사용 예]\n  LocalDate d = DateTimeUtils.parseDate(\"2026-10-08\");\n  String s = DateTimeUtils.formatDateTime(LocalDateTime.now());\n[주의]\n- 모든 메서드는 서버 기본 시간대 기준이다. 시간대 변환이 필요하면 호출부에서 처리한다.\n[메서드]\n- parseDate(text): yyyy-MM-dd 형식의 날짜 문자열 → LocalDate. 형식이 맞지 않거나 null이면 IllegalArgumentException\n- formatDate(date): yyyy-MM-dd 형식 문자열 (date가 null이면 빈 문자열)\n- formatDateTime(dateTime): yyyy-MM-dd HH:mm:ss 형식 문자열 (dateTime이 null이면 빈 문자열)\n- isValidRange(from, to): 기간 검색 조건 검증용. 시작일이 종료일보다 늦으면 false. 단, 둘 중 하나라도 null이면 true"
```

**공통 메타 필드**
- 새 항목: `addedInCommit`(해시 앞 7자리), `addedAt`(커밋 시각, ISO 8601)
- 갱신한 항목: `addedInCommit`/`addedAt`은 그대로 두고 `updatedInCommit`, `updatedAt`을 추가하거나 덮어쓴다.
- 시각은 작업한 시각이 아니라 **커밋 시각**을 쓴다. 반드시 `git -C common-repo show -s --format=%cI <해시>`의
  출력을 **그대로** 쓴다. (예: `2026-10-08T05:28:35+01:00`) 날짜만 쓰거나 `00:00:00`처럼 시각을 지어내지 않는다.

### 항목 예시

```json
{
  "type": "frontend-component",
  "name": "Pagination",
  "path": "common-repo/components/Pagination.tsx",
  "purpose": "목록 하단 페이지 넘기기",
  "props": ["page", "totalPages", "onChange"],
  "detail": null,
  "addedInCommit": "370478a",
  "addedAt": "2026-09-10T12:34:53+09:00"
}
```

### 로그 형식 (`asset-index/automation.log`, 한 줄씩 추가)

- 파일 편집 도구로 파일 끝에 줄을 추가하고 **UTF-8**로 저장한다. 셸의 `echo`/`>>`/`Add-Content`/`Out-File`로
  쓰지 않는다. (Windows에서 한글이 CP949로 깨진다.)
- 줄 앞뒤에 따옴표를 붙이지 않는다. 화살표는 `→`, `[커밋시각]`은 `%cI` 값을 그대로 쓴다.
- **기존 줄은 절대 고치지 않는다.** 파일 끝에 새 줄만 추가한다. (띄어쓰기 정리도 하지 않는다.)
- 아래 형식의 글자를 그대로 쓴다. `index에`, `index의`는 붙여 쓴다.

- 추가: `[커밋시각] commit <해시7> → index에 <자산명>(<종류>) 추가함`
- 갱신: `[커밋시각] commit <해시7> → index의 <자산명>(<종류>) 갱신함: <바뀐 필드>`
- 보류: `[커밋시각] commit <해시7> → 판단 보류: <파일 경로> - <이유>`

## 하지 말 것
- `common-repo` 소스 코드를 수정하지 않는다. (커밋만 한다.)
- 승인 없이 커밋하거나 push하지 않는다.
- 사용자가 stage하지 않은 파일을 `git add`하거나 커밋에 넣지 않는다. (예외: 6단계의 정리집 두 파일)
- 커밋되지 않은 파일을 정리집에 반영하지 않는다. 작업 트리 파일을 직접 읽어서 정리하지 않는다.
- 어떤 커밋에도 없는 변경을 다른 커밋의 해시로 기록하지 않는다.
- 소스에 없는 내용을 지어내서 정리집에 적지 않는다.
