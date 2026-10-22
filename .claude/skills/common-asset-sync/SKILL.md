---
name: common-asset-sync
description: 공통팀이 "공통 자산 정리해줘"라고 하거나, common-repo의 components/·backend/ 변경을 커밋하고 공통 자산 정리집(asset-index.json)에 반영해야 할 때, 또는 사람이 직접 커밋해서 정리집 반영이 밀려 있을 때 사용.
---

# 공통 자산 정리 (커밋 + 정리집 + 변경 기록)

이 문서 하나에 절차와 정리집 작성 규칙이 모두 들어 있다. 다른 지시 파일을 찾지 않는다.

이 스킬의 목적은 공통팀의 개발 사항을 개발팀에 **잘 설명하는 것**이다. 주석이나 커밋 메시지를 옮겨 적는 데
그치지 않고, **소스를 읽고 실제 동작을 정리**한다. 누가 영향을 받는지 찾아 알리는 일은 이 스킬이 하지 않는다.
그 일은 `common-asset-notify` 스킬이 이 스킬이 남긴 변경 기록(`asset-index/changes/`)을 읽어서 한다.

## 경로

모든 작업은 `common-repo` 저장소 **하나** 안에서 끝난다. (이 스킬이 들어 있는 저장소)

- 공통 코드: `common-repo/components/`, `common-repo/backend/`
- 정리집 폴더: `common-repo/asset-index/`
  - 정리집: `asset-index/asset-index.json`
  - 로그: `asset-index/automation.log`
  - 변경 기록: `asset-index/changes/<해시7>.json` (코드 커밋 하나에 파일 하나)
- 밀린 커밋 대기열: `common-repo/.git/common-asset-pending.txt`
  (post-commit 훅이 `components/`·`backend/`가 바뀐 커밋의 해시를 한 줄씩 적어 둔다. 사람이 직접 커밋한 것도 여기에 쌓인다.)

## 핵심 원칙

1. **정리집은 커밋된 내용만 기준으로 한다.** 커밋되지 않은 파일(작업 트리의 수정본, untracked 파일)은
   정리 대상이 아니다. 소스는 항상 `git show <해시>:<경로>`로 그 커밋 시점의 내용을 읽는다.
2. **근거가 있는 내용만 쓴다.** 근거는 세 가지다.
   - **주석**: 개발자가 적어 둔 문구
   - **코드 확인**: 코드에서 직접 확인한 사실 (분기, 기본값, null 처리, 예외, 부수효과, 렌더링 조건 등)
   - **추론**: 코드로 확인되지 않는 해석. 최소화하고, 쓴 경우 미리보기에서 반드시 확인받는다.
3. **공개되는 결과물에는 깨끗한 문장만 남긴다.** 정리집·변경 기록은 모든 개발자가 탐색 페이지와 MCP로 본다.
   `(AI 추론)` 같은 표시나 근거 코드 조각은 **미리보기에서만** 보여 주고, 파일에는 넣지 않는다.
   공통팀이 미리보기를 승인하면 그 내용은 "공통팀이 확인한 내용"이다.
4. **애매하면 반영하지 않고 로그에 "판단 보류"로 남긴다.**
5. **사용자 확인은 세 번 받는다: 공통 코드 커밋(2단계), 정리집 반영(5단계), push(7단계).** 정리집 내용은 이
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
- 먼저 **채팅 본문**에 아래 블록을 그대로 출력한다. 질문 창에는 긴 내용이 보이지 않으므로, 이 블록이 사용자가
  커밋 내용을 확인하는 유일한 화면이다.

  ```
  [커밋 미리보기]

  ■ stage된 파일
    M  components/Pagination.tsx    정리집 대상
    A  components/EmptyState.tsx    정리집 대상

  ■ 커밋 메시지
    feat: Pagination onChange 인자 변경, EmptyState 컴포넌트 추가

    - Pagination: pageSize prop 추가, onChange 인자를 { page, pageSize } 객체로 변경
    - EmptyState: 빈 목록 안내 컴포넌트 신규 추가
  ```
  - stage된 파일 중 정리집 대상이 아닌 파일(설정, 문서 등)이 섞여 있으면 블록 끝에 "정리집 대상이 아닌 파일도
    함께 커밋됩니다"를 넣는다. 빼거나 넣는 것은 사용자가 직접 한다.
- **질문 전 확인**: 바로 위 응답 본문에 `[커밋 미리보기]` 블록과 커밋 메시지 전문이 있는가?
  없으면 질문하지 말고 블록부터 출력한다.
- 그다음 질문 도구로 **"위 미리보기대로 커밋할까요?"** 한 줄만 묻는다. (push는 여기서 묻지 않는다.)
- 승인받으면 **stage된 그대로** 커밋한다. 메시지는 아래 [커밋 메시지 형식]의 "커밋하는 방법"을 따른다.
  - `git add`를 추가로 하지 않는다. (`git add -A`, `git add .` 금지)
  - `git commit -a`나 `git commit <경로>`를 쓰지 않는다. (stage되지 않은 변경까지 커밋된다.)
- 커밋하면 post-commit 훅이 해시를 대기열에 자동으로 추가한다.
- 사용자가 커밋을 거절하면 그 변경분은 정리하지 않는다. (원칙 1) 3단계로 가서 밀린 커밋만 정리한다.

### 3. 정리 대상 커밋 모으기
- 대기열 파일의 해시 목록을 읽는다. 40자리 16진수 해시가 아닌 줄은 무시한다.
  (파일이 없거나 비어 있으면 정리할 것이 없다고 알리고 7단계(push 확인)로 간다.)
- 이미 정리한 해시는 건너뛴다. 정리집의 `addedInCommit`/`updatedInCommit`에 있거나
  `asset-index/changes/<해시7>.json`이 이미 있으면 정리한 것이다.
- 여러 개면 오래된 커밋부터 순서대로 처리한다. (`git -C common-repo log --reverse --format=%H`의 순서)

### 4. 정리집 내용 구성 (아직 파일에 쓰지 않음)
커밋마다 다음을 수행한다. 이 단계에서는 `asset-index/` 아래 어떤 파일도 **수정하지 않는다.**

1. 커밋 정보를 확인한다.
   - `git -C common-repo show -s --format="%H%n%cI%n%s" <해시>` → 해시, 커밋 시각(ISO 8601), 메시지
   - `git -C common-repo diff-tree --no-commit-id --name-status -r <해시>` → 파일별 상태(A 추가 / M 수정 / D 삭제 / R 이름 변경)
2. 바뀐 파일들을 아래 **[정리집 작성 규칙]** 의 "자산 판별"로 **자산 단위로 묶는다.**
   함께 커밋된 파일 중 서로 연결된 파일들은 기능 하나다. 이후 단계는 파일이 아니라 자산 단위로 한다.
3. 자산마다 그 자산의 **모든 파일**을 `git -C common-repo show <해시>:<경로>`로 그 커밋 시점의 내용을 **끝까지** 읽는다.
   - 이번 커밋에서 바뀌지 않은 파일도 그 자산의 `files`에 있으면 함께 읽는다. (예: XML만 바뀌어도 Controller·Service를 함께 읽어야 기능 전체의 동작을 안다)
   - 수정이면 비교를 위해 `<해시>~1` 시점의 같은 파일들도 읽는다.
4. 규칙에 따라 자산마다 **추가 / 갱신 / 판단 보류** 중 하나로 정하고, 반영할 내용을 만든다.
   - 추가: 새 항목 전체
   - 갱신: 바뀌는 필드의 이전 값과 새 값
   - 판단 보류: 이유
5. 자산마다 **변경 등급**을 정하고 변경 기록을 만든다. (아래 [변경 기록 작성 규칙])
6. 남길 로그 줄과 정리집 커밋 메시지를 만든다.
7. 항목마다 **근거 메모**를 만든다. 미리보기 전용이며 파일에는 저장하지 않는다.
   - `[동작]`의 각 줄이 어느 코드에서 확인됐는지 (예: `if (!open) return null`)
   - 추론한 부분이 있으면 무엇을 추론했는지
   - 주석과 코드가 서로 다른 부분
   - 여러 파일로 된 자산이면 묶은 파일 목록, 시작 파일로 본 이유, 확인하지 못한 연결(`⚠ 연결 끊김`)

### 5. 반영 전 미리보기 (사용자 확인 후)
4단계에서 만든 내용을 아래 형식으로 **한 번에** 보여 주고 **"이대로 정리집에 반영할까요?"** 를 묻는다.

> **미리보기는 질문 도구 안에 넣지 않는다.** 질문 창에는 긴 내용이 보이지 않는다.
> 1) 먼저 미리보기 전문을 **일반 응답 메시지(채팅 본문)** 로 출력한다.
> 2) 그다음 질문 도구로는 "위 미리보기대로 정리집에 반영할까요?" 한 줄만 묻는다.
> **질문 전 확인**: 바로 위 응답 본문에 `[정리집 반영 미리보기]` 블록 전문이 있는가? 없으면 질문하지 말고 블록부터 출력한다.

미리보기는 **사람이 읽는 화면**이다. JSON을 그대로 보여 주지 않는다. 필드마다 제목을 달고, `detail`은
[detail 작성 형식]의 섹션 그대로 줄을 나눠 보여 준다. (실제 저장은 6단계에서 JSON으로 한다.)
`[동작]` 줄 뒤에는 `← 근거: <코드>`를 붙이고, 추론한 줄에는 `⚠ 추론 — 확인 필요`를 붙인다.
이 표시는 미리보기에만 있고 파일에는 저장되지 않는다는 점을 미리보기 맨 위에 한 줄로 밝힌다.

```
[정리집 반영 미리보기]
(← 근거, ⚠ 표시는 검토용이며 정리집에는 저장되지 않습니다)

■ 추가 — Modal (frontend-component)
  커밋  477e742 (2026-09-10T16:27:43+09:00)
  경로  common-repo/components/Modal.tsx

  ▸ purpose
    제목과 닫기 버튼이 있는 오버레이 모달 창.   ← 근거: 코드 동작 요약 (상단 주석 없음)

  ▸ props
    open, title, onClose, children

  ▸ detail
    [사용 예]   ⚠ 생성 — 확인 필요
      <Modal open={open} title="상세 정보" onClose={() => setOpen(false)}>
        <p>내용</p>
      </Modal>
    [동작]
    - open이 false이면 아무것도 렌더링하지 않는다.   ← 근거: if (!open) return null
    - 배경을 클릭하면 onClose가 호출된다. 모달 안쪽 클릭은 닫히지 않는다.   ← 근거: backdrop onClick, e.stopPropagation()
    - 헤더에 "닫기" 버튼이 항상 표시된다.   ← 근거: <button onClick={onClose}>닫기</button>
    [props]
    - children: 선택 (없으면 본문이 비어 있다)   ← 근거: children?: ReactNode

  ▸ related
    (없음)

  ▸ 변경 등급  ⚪ 신규
    요약  Modal 컴포넌트 추가

■ 갱신 — Pagination (frontend-component)
  커밋  1a2b3c4 (2026-10-09T10:00:00+09:00)
  ▸ props
    이전: page, totalPages, onChange
    이후: page, totalPages, pageSize, onChange
  ▸ 변경 등급  🔴 비호환
    요약     onChange 인자가 page 숫자에서 { page, pageSize } 객체로 바뀜
    상세     onChange: (page: number) => void → (value: { page: number; pageSize: number }) => void
             pageSize prop 추가 (선택, 기본 20)
    할 일    onChange 핸들러가 객체를 받도록 수정한다.
    스캔 키  onChange
  ▸ 변경 이력에 추가
    2026-10-09T10:00:00+09:00  1a2b3c4  🔴 비호환  onChange 인자가 page 숫자에서 { page, pageSize } 객체로 바뀌었습니다.

■ 갱신 — Code (backend-feature)
  커밋  7f8e9d0 (2026-10-15T11:00:00+09:00)
  바뀐 파일  backend/code/code_SQL.xml
  묶음  정리집 files에 있음 → Code 기능 (CodeController, CodeService, CodeServiceImpl, CodeMapper, CodeVO, code_SQL.xml 함께 읽음)
  영향  code_SQL.xml의 selectCodeList를 CodeController의 GET /common/code/{groupId}가 사용
  ▸ detail [동작]
    추가: - 사용하지 않는 코드는 조회되지 않는다.   ← 근거: WHERE use_yn = 'Y' 추가
  ▸ 변경 등급  🟡 동작 변경
    요약       코드 목록 조회에서 사용하지 않는 코드가 빠집니다.
    영향 API   GET /common/code/{groupId}, selectCodeList
    할 일      사용하지 않는 코드도 화면에 보여야 하는 곳이 있는지 확인하세요.
  ⚠ 연결 끊김: CodeService 구현체가 2개(CodeServiceImpl, CachedCodeServiceImpl) — 어느 것이 쓰이는지 확인 필요

■ 판단 보류 — components/Alert.tsx
  커밋  48daac6
  이유  같은 이름의 항목이 이미 있음

■ 로그에 추가할 줄
  [2026-09-10T16:27:43+09:00] commit 477e742 → index에 Modal(frontend-component) 추가함

■ 변경 기록 파일
  asset-index/changes/477e742.json (1건: ⚪ Modal)

■ 정리집 커밋 메시지
  docs: 공통 자산 정리집 갱신 (477e742)

  - 추가: Modal(frontend-component) ← 477e742
```

- 주석과 코드가 다른 부분이 있으면 해당 항목 맨 위에 `⚠ 주석과 코드 불일치: ...`로 보여 준다.
- 사용자가 **수정을 요청**하면 그대로 고친 뒤 미리보기를 다시 보여 주고 다시 묻는다.
  사용자가 넣어 달라는 내용은 소스에 없더라도 공통팀이 확인한 내용으로 보고 표시 없이 반영한다.
- 사용자가 **거절**하면 `asset-index/`의 어떤 파일도 건드리지 않고, 대기열도 그대로 둔다. (다음 실행 때 다시 정리된다.)
  2단계에서 만든 커밋이 있으면 7단계(push 확인)로 간다.
- 정리할 대상 파일이 하나도 없고 판단 보류도 없으면 미리보기 없이 "정리집에 반영할 내용이 없습니다"라고 알리고
  대기열에서 그 해시를 지운 뒤 7단계로 간다.

### 6. 정리집 반영과 커밋
승인받은 내용 **그대로** 반영한다. 미리보기에 없던 내용을 더하거나 빼지 않는다. 근거 메모와 `⚠` 표시는 저장하지 않는다.
- `asset-index/asset-index.json`을 **UTF-8**, 들여쓰기 2칸의 올바른 JSON으로 저장한다.
  - JSON 외의 텍스트(설명, 마크다운 코드펜스 등)는 파일에 남기지 않는다.
  - **기존 서식을 유지한다.** `props`·`related`는 한 줄 배열(`["a", "b"]`), `usage`는 한 줄에 하나씩 쓴다.
    바뀌지 않은 항목의 줄바꿈·순서가 달라지면 안 된다. (파일 전체를 다시 직렬화하는 셸 명령
    `ConvertTo-Json` 등은 쓰지 않는다. 파일 편집 도구로 해당 항목만 고친다.)
  - **새 항목은 `assets` 배열의 맨 끝에 추가한다.** 마지막 항목의 닫는 `}` 뒤에 `,`를 붙이고 그 뒤에 넣는다.
    다른 항목의 중간에 끼워 넣지 않는다.
  - 추가·갱신한 항목마다 `history`에 이번 커밋 줄을 붙인다. (아래 [정리집 작성 규칙]의 "변경 이력")
- 변경 기록 `asset-index/changes/<해시7>.json`을 커밋마다 새 파일로 만든다. (UTF-8, 들여쓰기 2칸)
- 저장한 뒤 **JSON이 올바른지 반드시 확인한다.** (common-repo에서 실행)
  `node -e "for (const f of process.argv.slice(1)) JSON.parse(require('fs').readFileSync(f,'utf8')); console.log('JSON OK')" asset-index/asset-index.json asset-index/changes/<해시7>.json`
  `JSON OK`가 나오지 않으면 커밋하지 말고 고친 뒤 다시 확인한다.
- `asset-index/automation.log`에 미리보기의 로그 줄을 추가한다. 대상 파일마다 반드시 한 줄(추가·갱신·판단 보류 중 하나)이 남아야 한다.
- 정리집 파일**만** 커밋한다. 이때만 스킬이 직접 `git add`를 한다. 경로는 하나씩 적는다.
  ```
  git -C common-repo add asset-index/asset-index.json asset-index/automation.log asset-index/changes/<해시7>.json
  git -C common-repo commit -m "<제목>" -m "<본문>" -- asset-index/asset-index.json asset-index/automation.log asset-index/changes/<해시7>.json
  ```
  - 끝의 `-- <경로>`는 빼지 않는다. 사용자가 stage해 두고 2단계에서 커밋을 거절한 파일이 있어도 정리집 커밋에
    섞이지 않게 한다. `asset-index/` 폴더 전체를 경로로 주지 않는다. (다른 스킬의 파일이 섞일 수 있다.)
  - 메시지: 아래 [커밋 메시지 형식]의 "정리집 커밋" 형식 (제목 + 본문)
  - 정리집 커밋은 `components/`·`backend/`를 바꾸지 않으므로 훅이 대기열에 넣지 않는다.
- 처리한 해시를 대기열 파일에서 지운다. (판단 보류만 나온 커밋도 처리한 것으로 보고 지운다.)
  - 파일 편집 도구로 해당 줄만 지운다. 남은 해시가 없으면 **완전히 빈 파일**로 둔다. (`""`, 공백, 빈 줄을 남기지 않는다.)

### 7. push 확인 (마지막에 한 번)
- push 안 된 커밋을 확인한다: `git -C common-repo log --oneline @{u}..HEAD`
  - upstream이 없다는 오류가 나면 push를 묻지 않고, 결과 보고에 "upstream 미설정으로 push 생략"이라고 적는다.
- push할 커밋이 하나도 없으면 묻지 않고 8단계로 간다.
- 있으면 커밋 목록(`해시 제목` 한 줄씩)을 채팅 본문에 먼저 출력한 뒤 **"위 커밋을 push할까요?"** 를 한 번만 묻는다.
- 승인받으면 `git -C common-repo push`를 한다. (코드 커밋과 정리집 커밋이 함께 올라간다.)
- 거절하면 push하지 않는다. 다음 실행 때 push 안 된 커밋으로 다시 확인된다.

### 8. 결과 보고
- 커밋한 내용 (코드 커밋, 정리집 커밋 각각의 해시)
- 정리집에 추가되거나 갱신된 자산 이름과 종류, 변경 등급
- 판단 보류한 항목과 그 이유
- push 결과
- 이번에 만든 변경 기록 중 `docs`가 아닌 것이 있으면 마지막에 한 줄로 제안한다:
  **"변경 기록 N건(🔴 a / 🟡 b / 🟢 c / ⚪ d)이 생겼습니다. 이어서 관련자 알림(common-asset-notify)을 진행할까요?"**
  승인하면 `common-asset-notify` 스킬을 실행한다. 거절하면 끝낸다. (기록은 남아 있어 나중에 처리할 수 있다.)

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

### 정리집 커밋 (common-repo, asset-index/ 파일)
- 제목: `docs: 공통 자산 정리집 갱신 (<짧은 해시들>)`
- 본문: 정리집에 반영한 결과를 한 줄씩. 추가·갱신·판단 보류가 없는 줄은 쓰지 않는다.
  비호환(🔴)·동작 변경(🟡)은 줄 끝에 `[비호환]`, `[동작 변경]`을 붙인다.

```
docs: 공통 자산 정리집 갱신 (48daac6, 1a2b3c4)

- 추가: Spinner(frontend-component) ← 48daac6
- 갱신: Pagination(frontend-component) onChange 인자를 객체로 변경 ← 1a2b3c4 [비호환]
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

**정리 대상 파일**: `components/`, `backend/` 아래의 소스 파일 (`.tsx`, `.ts`, `.java`, `.xml`).
그 밖의 파일(설정, 스크립트, 문서, 테스트 등)은 정리 대상이 아니므로 무시한다.
(저장소 구조가 다르면 이 폴더를 그 구조에 맞게 바꾸고, post-commit 훅이 감시하는 폴더도 함께 맞춘다.)

**자산 = 기능 하나.** 파일 하나로 된 기능도 있고(Button, DateTimeUtils), 여러 파일로 된 기능도 있다
(Controller + Service + Mapper + XML). 공통팀은 기능 하나를 이루는 파일들을 **함께 커밋한다.**
그래서 함께 커밋된 파일 중 **서로 연결된 파일들을 기능 하나로 묶는다.** 파일 이름 규칙으로 정하지 않는다.

**묶는 순서**
1. **이미 정리된 자산의 파일인가**: 정리집 어떤 항목의 `files`(또는 `path`)에 있으면 그 자산이다.
2. **기존 자산에 새로 붙은 파일인가**: `files`에 없는 새 파일을 기존 자산의 파일이 쓰고 있으면(import, 호출, 구현, XML `namespace`) 그 자산에 붙인다.
   찾는 법: `git -C common-repo grep -n "<새 파일의 클래스·함수 이름>" <해시> -- components/ backend/`
3. **남은 파일끼리 묶는다**: 서로 참조하는 파일들(import, 호출, `implements`, `extends`, XML `namespace` ↔ Mapper)을 한 묶음으로 한다.
   - 한 묶음 = 새 자산 하나. 서로 참조하지 않으면 각각 다른 자산이다. (한 커밋에 기능 두 개가 섞여 있을 수 있다)
   - 묶음 안의 파일이 이미 정리된 **다른 자산**(예: ApiResponse)을 쓰기만 하면 그 자산은 묶지 않고 `related`에 넣는다.
4. **시작 파일을 정한다**: 묶음에서 **개발자가 직접 쓰는 쪽**이다. 보통 묶음 안의 다른 파일이 참조하지 않는 바깥쪽 파일이다.
   (예: Controller, 화면에 넣는 컴포넌트, 주입해서 부르는 클래스, 붙여 쓰는 어노테이션)
   시작 파일이 여러 개일 수 있다. (예: API로도 부르고 Service를 주입해서도 부르는 기능)

**종류 (`type`)**
| 종류 | 언제 | 예 |
|---|---|---|
| `frontend-component` | `components/`의 파일 하나로 된 기능 | Button, Pagination |
| `backend-module` | `backend/`의 파일 하나로 된 기능 | ApiResponse, DateTimeUtils |
| `frontend-feature` | `components/`의 여러 파일로 된 기능 (컴포넌트 + hook + API 호출 등) | 주소 검색 |
| `backend-feature` | `backend/`의 여러 파일로 된 기능 (Controller + Service + Mapper + XML 등) | 공통코드 조회 |

- 미리보기에서 **어떻게 묶었는지**(파일 목록, 시작 파일과 그 이유)를 반드시 보여 준다. 공통팀이 묶음이 맞는지 확인한다.
- 묶음이 애매하면(서로 참조는 없지만 같은 기능 같아 보이는 경우 등) 미리보기에서 `⚠ 묶음 확인 필요`로 묻는다. 지어서 묶지 않는다.

### 파일 상태별 처리

| 상태 | 정리집 처리 | 변경 기록 |
|---|---|---|
| A (추가) | 새 항목을 추가한다. 같은 `name`이 이미 있으면 추가하지 않고 판단 보류로 남긴다. | `new` |
| M (수정) | 이전 소스(`<해시>~1`)와 이후 소스에서 **각각 이 규칙대로** 필드(`props`/`usage`/`api`/`files`/`purpose`/`detail`/`related`)를 뽑아 비교하고, 달라진 필드만 갱신한다. (정리집에 저장된 값과 비교하지 않는다. 예전 형식으로 저장된 항목이라는 이유만으로 고치지 않는다.) 달라진 필드는 이후 소스 기준으로 **통째로 다시 쓴다.** 정리집에 항목이 없던 자산이면 새 항목으로 추가한다. | 비교 결과에 따라 등급 판정 |
| D (삭제) | 항목을 지우지 않고 판단 보류로 남긴다. (삭제 반영 여부는 사람이 결정한다.) | `breaking` (자산 삭제) |
| R (이름 변경/이동) | 추가하지 않고 판단 보류로 남긴다. | `breaking` (이름 변경/이동) |

위 표는 **자산 단위**로 적용한다.
- 파일 하나로 된 자산: 그 파일의 상태를 따른다.
- 여러 파일로 된 자산: **새로 묶인 자산이면 A**, 기존 자산에 속한 파일이 하나라도 바뀌었거나 새 파일이 붙었으면 **M**이다.
  (예: XML 한 파일만 바뀐 커밋 → 그 XML이 속한 자산의 M. 이전·이후 시점의 `files` 전체를 읽어 비교한다)
  - 기존 자산의 시작 파일이 D/R이면 자산의 D/R로 본다. 시작 파일이 아닌 파일만 D면 M이다. (`files`에서 뺀다)

diff에서 바뀌지 않은 기존 항목은 절대 건드리지 않는다.

### 필드 추출

**frontend-component**
- `name`: 컴포넌트 함수/export 이름
- `path`: `common-repo/`를 붙인 전체 경로
- `props`: 컴포넌트가 받는 Props interface/type(예: `TabsProps`)에 정의된 prop 이름 목록.
  prop 안에서 쓰는 보조 타입(예: `items: TabItem[]`의 `TabItem`)의 필드는 `props`에 넣지 않고,
  `detail`의 `[props]`에 `- items[].key: <주석>` 형태로 넣는다.
- `purpose`: 파일 상단 주석의 **첫 문장 하나**. 상단 주석이 없으면 **코드에서 확인한 동작을 한 줄로 요약**한다.
- `detail`: 아래 [detail 작성 형식]으로 정리한다. 쓸 내용이 하나도 없으면 `null`.
- `related`: 아래 [related 작성 규칙]

**backend-module**
- `name`: public 클래스 이름
- `path`: `common-repo/`를 붙인 전체 경로
- `usage`: 다른 코드에서 이 클래스를 쓰는 방법. **public** 생성자·메서드 시그니처를 소스 순서대로 **전부** 쓴다.
  private/protected 생성자·메서드는 넣지 않는다.
- `purpose`: 클래스 상단 Javadoc의 **첫 문장 하나**. Javadoc이 없으면 **코드에서 확인한 역할을 한 줄로 요약**한다.
- `detail`: 아래 [detail 작성 형식]으로 정리한다. 쓸 내용이 하나도 없으면 `null`.
- `related`: 아래 [related 작성 규칙]

**frontend-feature / backend-feature** (여러 파일로 된 기능)
- `name`: 기능 이름. 시작 파일의 이름에서 `Controller`·`Service` 같은 꼬리를 뗀 이름 (예: `CodeController` → `Code`)
- `path`: 시작 파일의 전체 경로 (시작 파일이 여러 개면 개발자가 가장 먼저 쓰는 것)
- `files`: 이 기능을 이루는 파일의 전체 경로 목록. 시작 파일부터 연결 순서대로. **다음에 이 중 하나만 바뀌어도 이 기능의 변경으로 찾는 데 쓴다.**
- `purpose`: 시작 파일 상단 주석의 **첫 문장 하나**. 없으면 **파일 전체에서 확인한 기능을 한 줄로 요약**한다.
- `api`: HTTP로 부르는 엔드포인트가 있으면 한 줄에 하나씩 `"<METHOD> <전체 경로>"` (클래스의 `@RequestMapping` 경로 + 메서드 매핑 경로). 없으면 넣지 않는다.
- `usage`: 코드로 직접 부르는 시작 파일(주입해서 부르는 클래스, export 함수·hook 등)의 public 시그니처 전부. 없으면 넣지 않는다.
- `props`: 화면에 넣는 컴포넌트가 시작 파일이면 그 props. 없으면 넣지 않는다.
- `detail`: 아래 [detail 작성 형식]으로 정리한다. `[동작]`에는 시작 파일만이 아니라 **묶인 모든 파일**에서 확인한 사실을 쓴다.
  (예: 검증은 Controller, 캐시는 Service, 조회 조건·정렬은 XML에 있다)
- `related`: 아래 [related 작성 규칙]

### 묶음 밖의 파일이 필요할 때 (보조)

함께 커밋된 파일과 `files`만으로 동작을 다 알 수 없으면, 그때만 필요한 파일을 더 찾아 읽는다. 저장소 전체를 읽지 않는다.
검색은 항상 **그 커밋 시점**으로 한다: `git -C common-repo grep -n "<패턴>" <해시> -- components/ backend/`
- 묶음의 파일이 쓰는데 커밋에도 `files`에도 없는 파일 (예: 구현체, 부모 클래스, Mapper가 가리키는 XML)
  - 이미 다른 자산이면 `related`에 넣고 들어가지 않는다.
  - 다른 자산이 아니면 읽고, 이 기능의 일부로 보이면 `files`에 넣는다. (미리보기에서 "묶음에 추가함"으로 보여 준다)
- 바뀐 파일이 여러 자산의 `files`에 들어 있으면 (공유 Mapper 등) **모든** 자산이 바뀐 것이다.

**확인하지 못한 연결** — 지어내지 않고 미리보기에 `⚠ 연결 끊김: <무엇> — 확인 필요`로 표시한다. 공통팀이 판단한다.
- 구현체가 여러 개라 어느 것이 쓰이는지 코드로 알 수 없는 경우
- 코드에 호출이 보이지 않고 설정으로 끼어드는 것 (설정 파일로 등록한 AOP·인터셉터·필터)
  - 단, 클래스·메서드에 붙은 어노테이션(`@Transactional`, `@Cacheable`, `@Valid`, `@PreAuthorize` 등)은 보이므로 그 동작을 `[동작]`에 쓴다.
- 저장소 밖 (DB 프로시저·트리거, 다른 서비스, 외부 API)

**공개 결과물에 쓰지 않는 것**: 테이블명, 컬럼명, SQL 원문, 내부 클래스 이름(Impl, Mapper 등). 개발자가 관찰할 수 있는 동작으로 바꿔 쓴다.
(예: `WHERE use_yn = 'Y'` → `사용하지 않는 코드는 조회되지 않는다.`) 원문은 근거 메모에만 둔다.

### detail 작성 형식

`detail`은 한 덩어리 문장으로 이어 붙이지 않는다. 아래 섹션 순서로 **줄을 나눠** 쓴다.
JSON에는 줄바꿈을 `\n`으로 넣은 하나의 문자열로 저장한다. 내용이 없는 섹션은 통째로 뺀다.

| 섹션 | 담는 내용 | 쓰는 법 |
|---|---|---|
| `[설명]` | 상단 주석 중 purpose(첫 문장)를 뺀 나머지 설명 | 문장마다 `- `로 시작하는 한 줄 |
| `[사용 예]` | 주석에 적힌 예시 코드 | 코드를 고치지 않고 줄마다 앞에 공백 2칸 |
| `[주의]` | "주의", "단", "반드시" 등 개발자의 당부 | 항목마다 `- ` 한 줄 |
| `[동작]` | **코드에서 확인한** 사실 중 주석에 없는 것 | 사실마다 `- ` 한 문장 |
| `[props]` (프론트) | prop별 주석, 코드에서 확인한 기본값·선택 여부 | `- <prop>: <설명>` 한 줄씩, interface에 적힌 순서대로 |
| `[API]` (API가 있는 기능) | 엔드포인트별 요청·응답·실패 | 엔드포인트마다 `- <METHOD> <경로>: <설명>` 한 줄, 그 아래 공백 2칸 들여 `요청:`, `응답:`, `실패:` 줄 (해당하는 것만) |
| `[메서드]` (백엔드) | 메서드별 Javadoc, `@param`/`@return`/`@throws`, 코드에서 확인한 예외·null 처리 | `- <메서드명>(<인자명>): <설명>` 한 줄씩, 소스 순서대로 |

- `[API]`의 `요청:`에는 파라미터·본문 필드를 `이름(타입, 필수/선택)`으로 쓴다. 검증 규칙(`@NotBlank`, `@Size` 등)이 있으면 함께 쓴다.
- `[API]`의 `응답:`에는 개발자가 받는 JSON의 모양을 한 줄로 쓴다. (예: `{ success, data: [{ code, name }] }`)
- `[API]`의 `실패:`에는 `조건 → 결과`로 쓴다. (예: `groupId가 없으면 → success=false, "존재하지 않는 코드 그룹입니다."`)
- backend-feature의 `[사용 예]`에는 **API 호출 예**(요청과 응답 JSON)를 넣고, `usage`가 있으면 **Java 호출 예**도 넣는다.

**`[동작]`에 쓰는 것** — 개발자가 이 자산을 쓸 때 알아야 하는데 주석에 없는 사실:
- 렌더링하지 않는 조건, 표시가 바뀌는 조건 (예: `open이 false이면 아무것도 렌더링하지 않는다.`)
- 이벤트가 호출되는 시점과 호출되지 않는 경우 (예: `disabled 탭은 클릭해도 onChange가 호출되지 않는다.`)
- 기본값, 값 보정, 범위 제한
- null·빈 값 처리, 던지는 예외
- 고정된 문구나 요소 (예: `헤더에 "닫기" 버튼이 항상 표시된다.`)
- 파일·DB·외부 호출 같은 부수효과
- (여러 파일로 된 기능) 조회에서 빠지는 데이터, 정렬 순서, 조건에 따라 달라지는 조회 범위 (동적 SQL의 `<if>`)
- (여러 파일로 된 기능) 캐시 (변경이 바로 반영되지 않음), 트랜잭션 범위, 권한·인증 요구

**`[동작]` 쓰는 법**
- 문장만 쓴다. 근거(코드 조각, 줄 번호)는 붙이지 않는다. 근거는 미리보기의 근거 메모에만 둔다.
- 주석에 이미 같은 내용이 있으면 `[동작]`에 다시 쓰지 않는다.
- 주석과 코드가 서로 다르면 **코드 기준**으로 `[동작]`에 쓰고, 미리보기에서 `⚠ 주석과 코드 불일치`로 알린다.
- CSS 클래스명, 내부 변수명, 구현 방식(어떤 훅을 쓰는지 등)처럼 사용하는 쪽과 상관없는 내용은 쓰지 않는다.

**공통 규칙**
- **주석 문구를 그대로 옮긴다.** 띄어쓰기를 바꾸지 않는다. 특히 영문·숫자·기호 뒤에 붙은 조사를 띄우지 않는다.
  - 틀림: `API 에서`, `null 이면`, `items 의 key 는`, `onChange 가`, `index 에`
  - 맞음: `API에서`, `null이면`, `items의 key는`, `onChange가`, `index에`
  - 미리보기를 출력하기 전에 `purpose`·`detail`·로그 줄을 소스 주석과 대조해, 영문 뒤 조사 앞에 공백이 생겼으면 붙인다.
- 사용 예시가 주석에 있으면 반드시 `[사용 예]`에 넣는다. 빠뜨리지 않는다.
- 주석에 사용 예시가 **없으면 만든다.** 탐색 페이지에서 개발자가 가장 많이 보는 부분이다.
  - 실제 시그니처·props만 쓴다. 없는 prop이나 메서드를 쓰지 않는다. 그대로 복사해 쓸 수 있는 코드로 쓴다.
  - 가장 흔한 사용 한 가지를 2~6줄로 쓴다. 필수 prop·인자는 모두 넣고, `[동작]`에서 주의할 점이 있으면 그것이 드러나게 쓴다.
  - 미리보기에서 만든 예시에는 `⚠ 생성 — 확인 필요`를 붙인다. 승인받으면 표시 없이 저장한다. (원칙 3)
  - 프론트 예: `<Modal open={open} title="상세 정보" onClose={() => setOpen(false)}>...</Modal>`
- 같은 문장을 `purpose`와 `detail`에 중복해서 쓰지 않는다.
- `(AI 추론)`, `(사용자 입력)`, `(근거: ...)` 같은 표시는 어떤 필드에도 넣지 않는다. (원칙 3)

저장 예 (Modal, 주석 없는 컴포넌트):

```json
"purpose": "제목과 닫기 버튼이 있는 오버레이 모달 창.",
"props": ["open", "title", "onClose", "children"],
"detail": "[사용 예]\n  <Modal open={open} title=\"상세 정보\" onClose={() => setOpen(false)}>\n    <p>내용</p>\n  </Modal>\n[동작]\n- open이 false이면 아무것도 렌더링하지 않는다.\n- 배경을 클릭하면 onClose가 호출된다. 모달 안쪽 클릭은 닫히지 않는다.\n- 헤더에 \"닫기\" 버튼이 항상 표시된다.\n[props]\n- children: 선택 (없으면 본문이 비어 있다)"
```

### related 작성 규칙
- 이 자산이 **코드에서 직접 참조하는** 다른 공통 자산의 `name` 목록. import, 생성자 주입, 호출, 반환 타입·인자 타입으로만 판단한다.
  - 예: FileController → `["FileStorageService", "FileUploadResult", "ApiResponse"]`
- "함께 쓰면 좋을 것 같다"는 판단으로 넣지 않는다.
- 해당하는 자산이 없으면 `related` 필드를 넣지 않는다.

**공통 메타 필드**
- 새 항목: `addedInCommit`(해시 앞 7자리), `addedAt`(커밋 시각, ISO 8601)
- 갱신한 항목: `addedInCommit`/`addedAt`은 그대로 두고 `updatedInCommit`, `updatedAt`을 추가하거나 덮어쓴다.
- 시각은 작업한 시각이 아니라 **커밋 시각**을 쓴다. 반드시 `git -C common-repo show -s --format=%cI <해시>`의
  출력을 **그대로** 쓴다. (예: `2026-10-08T05:28:35+01:00`) 날짜만 쓰거나 `00:00:00`처럼 시각을 지어내지 않는다.

**변경 이력 (`history`)**
개발자가 탐색 페이지와 MCP에서 "언제, 어떤 등급으로 바뀌었는지"를 바로 볼 수 있게 변경 기록의 요약을 항목에 남긴다.
- 항목을 **추가하거나 갱신할 때마다** `history` 배열 끝에 한 줄을 붙인다. 판단 보류는 항목을 건드리지 않으므로 붙이지 않는다.
- 한 줄 형식: `{ "commit": "<해시7>", "at": "<커밋 시각>", "grade": "<grade>", "summary": "<summary>" }`
  - `at`은 `updatedAt`/`addedAt`과 같은 커밋 시각(`%cI` 그대로), `grade`·`summary`는 같은 커밋의 변경 기록 값을 **그대로** 쓴다.
- 기존 줄은 고치거나 지우지 않는다. 오래된 것부터 쌓는다. (화면에서는 최신순으로 보여 준다)
- `history`가 없는 기존 항목을 갱신하면 `history`를 새로 만들고 이번 줄 하나만 넣는다. 과거 이력을 지어 넣지 않는다.

### 항목 예시

필드 순서: `type`, `name`, `path`, (`files`), `purpose`, (`api`), `props` 또는 `usage`, `detail`, `related`, `addedInCommit`, `addedAt`, (`updatedInCommit`, `updatedAt`), `history`
`files`·`api`·`usage`·`history` 배열은 한 줄에 하나씩 쓴다.

```json
{
  "type": "backend-module",
  "name": "FileController",
  "path": "common-repo/backend/FileController.java",
  "purpose": "공통 파일 업로드/다운로드 API.",
  "usage": [
    "public FileController(FileStorageService fileStorageService)",
    "public ApiResponse<FileUploadResult> upload(MultipartFile file)",
    "public ResponseEntity<Resource> download(String storedFileName)"
  ],
  "detail": null,
  "related": ["FileStorageService", "FileUploadResult", "ApiResponse"],
  "addedInCommit": "2eaa9e4",
  "addedAt": "2026-09-10T15:20:35+09:00",
  "history": [
    { "commit": "2eaa9e4", "at": "2026-09-10T15:20:35+09:00", "grade": "new", "summary": "FileController가 추가되었습니다." }
  ]
}
```

기능 자산 예 (Controller → Service → Mapper → XML로 이루어진 공통코드 조회):

```json
{
  "type": "backend-feature",
  "name": "Code",
  "path": "common-repo/backend/code/CodeController.java",
  "files": [
    "common-repo/backend/code/CodeController.java",
    "common-repo/backend/code/CodeService.java",
    "common-repo/backend/code/CodeServiceImpl.java",
    "common-repo/backend/code/CodeMapper.java",
    "common-repo/backend/code/CodeVO.java",
    "common-repo/backend/code/code_SQL.xml"
  ],
  "purpose": "공통코드 그룹별 코드 목록 조회.",
  "api": [
    "GET /common/code/{groupId}"
  ],
  "usage": [
    "public List<CodeVO> selectCodeList(String groupId)"
  ],
  "detail": "[사용 예]\n  GET /common/code/GENDER\n  → { \"success\": true, \"data\": [{ \"code\": \"M\", \"name\": \"남\" }, { \"code\": \"F\", \"name\": \"여\" }] }\n  List<CodeVO> codes = codeService.selectCodeList(\"GENDER\");\n[동작]\n- 사용하지 않는 코드는 조회되지 않는다.\n- 정렬 순서는 코드별로 지정된 순서를 따른다.\n- 조회 결과는 캐시되어, 코드를 바꿔도 서버를 다시 시작하기 전까지 반영되지 않는다.\n[API]\n- GET /common/code/{groupId}: 코드 그룹의 코드 목록\n  요청: groupId(문자열, 필수)\n  응답: { success, data: [{ code, name }] }\n  실패: 없는 그룹이면 → 빈 목록",
  "related": ["ApiResponse"],
  "addedInCommit": "a1b2c3d",
  "addedAt": "2026-10-15T10:00:00+09:00"
}
```

## 변경 기록 작성 규칙

### 변경 등급
대상 파일마다 이전 코드(`<해시>~1`)와 이후 코드를 비교해 등급을 정한다. 여러 변경이 섞여 있으면 **가장 높은 등급**을 쓴다.

| 등급 | `grade` | 기준 | `action`(개발자가 할 일) |
|---|---|---|---|
| 🔴 비호환 | `breaking` | prop·public 메서드 삭제나 이름 변경, 필수 prop·인자 추가, 타입·반환 타입 변경, 예외를 던지는 조건 변경, 파일 삭제(D)나 이동(R). **API**: 엔드포인트 삭제, 경로·HTTP 메서드 변경, 요청 필드가 필수로 바뀜, 응답 필드 삭제·이름·타입 변경 | 반드시 수정할 내용 |
| 🟡 동작 변경 | `behavior` | 시그니처는 같지만 기본값, 보정, null 처리, 렌더링 조건, 호출 시점 등 동작이 바뀜. **기능 자산**: 조회 조건·정렬, 검증 규칙, 캐시, 권한, 실패 시 응답이 바뀜 (XML·Impl만 바뀐 경우가 대부분 여기) | 확인할 내용 |
| 🟢 호환 추가 | `compatible` | 선택 prop·새 public 메서드 추가 등 기존 사용 코드가 그대로 동작하는 추가. **API**: 새 엔드포인트, 선택 요청 필드, 응답 필드 추가 | 새로 쓸 수 있는 기능 |
| ⚪ 신규 | `new` | 새 자산 (A) | 이 자산이 대신할 수 있는 일 |
| 문서 | `docs` | 주석·서식·내부 구현만 바뀌고 사용하는 쪽에서 보이는 동작은 같음 | `null` |

- 등급이 애매하면 높은 쪽으로 정하고, 미리보기에서 `⚠ 추론 — 확인 필요`로 표시해 공통팀이 정하게 한다.
- 등급은 **시그니처만 보고 정하지 않는다.** 함수 본문의 분기·기본값·조기 return도 이전과 비교한다.
  커밋 메시지나 주석에 없는 동작 변경이 가장 놓치기 쉽고, 개발팀에 가장 알려야 하는 내용이다.
  (예: `if (totalPages <= 1) return null` 추가 → 이전에는 항상 표시되던 것이 숨겨짐 → `details`에 넣는다)
- `summary`와 `action`은 개발자에게 그대로 전달되는 문장이다. 코드에서 확인한 사실로, 한두 문장으로 쓴다.
  `action`에는 가능하면 수정 예시를 한 줄 넣는다.

### 변경 기록 파일 형식 (`asset-index/changes/<해시7>.json`)
- 코드 커밋 하나에 파일 하나. 그 커밋의 대상 파일을 `changes` 배열에 모두 넣는다. (판단 보류한 파일도 넣는다.)
- 대상 파일이 하나도 없는 커밋은 파일을 만들지 않는다.

```json
{
  "commit": "1a2b3c4",
  "committedAt": "2026-10-09T10:00:00+09:00",
  "subject": "feat: Pagination 페이지 크기 선택 추가",
  "changes": [
    {
      "asset": "Pagination",
      "type": "frontend-component",
      "path": "common-repo/components/Pagination.tsx",
      "fileStatus": "M",
      "grade": "breaking",
      "summary": "onChange 인자가 page 숫자에서 { page, pageSize } 객체로 바뀌었습니다.",
      "details": [
        { "what": "onChange 시그니처", "before": "(page: number) => void", "after": "(value: { page: number; pageSize: number }) => void" },
        { "what": "pageSize prop 추가 (선택, 기본 20)", "before": null, "after": "pageSize?: number" }
      ],
      "action": "onChange 핸들러가 객체를 받도록 수정하세요. 예: onChange={({ page }) => setPage(page)}",
      "scanHints": ["onChange"]
    }
  ],
  "notified": false
}
```

- `asset`: 자산 이름. D/R이면 이전 이름.
- `fileStatus`: `A` / `M` / `D` / `R`
- `details`: 바뀐 점마다 하나. 신규(`new`)면 빈 배열 `[]`.
- `scanHints`: `breaking`일 때만 넣는다. 삭제되거나 바뀐 prop·메서드·필드 이름. 영향 대상을 정밀하게 찾는 데 쓴다.
- `affectedApi`: 여러 파일로 된 기능일 때, 영향 받은 엔드포인트(`"<METHOD> <경로>"`)와 직접 부르는 메서드 이름 목록.
  바뀐 파일이 쓰이는 엔드포인트·메서드만 넣는다. (예: XML의 `selectCodeList`만 바뀌었으면 `["GET /common/code/{groupId}", "selectCodeList"]`)
- `changedFiles`: 여러 파일로 된 기능일 때, 이 커밋에서 바뀐 이 자산의 파일 목록 (전체 경로). 공통팀 검토용이다.
- `notified`: 항상 `false`로 만든다. `notified`, `notifiedAt`, `notification`은 `common-asset-notify`만 바꾼다.
- `announcement`는 넣지 않는다. 정리 자료에 포함되면 `common-asset-announce`가 추가한다.

### 로그 형식 (`asset-index/automation.log`, 한 줄씩 추가)

- 파일 편집 도구로 파일 끝에 줄을 추가하고 **UTF-8**로 저장한다. 셸의 `echo`/`>>`/`Add-Content`/`Out-File`로
  쓰지 않는다. (Windows에서 한글이 CP949로 깨진다.)
- 줄 앞뒤에 따옴표를 붙이지 않는다. 화살표는 `→`, `[커밋시각]`은 `%cI` 값을 그대로 쓴다.
- **기존 줄은 절대 고치지 않는다.** 파일 끝에 새 줄만 추가한다. (띄어쓰기 정리도 하지 않는다.)
- 아래 형식의 글자를 그대로 쓴다. `index에`, `index의`는 붙여 쓴다.

- 추가: `[커밋시각] commit <해시7> → index에 <자산명>(<종류>) 추가함 [<grade>]`
- 갱신: `[커밋시각] commit <해시7> → index의 <자산명>(<종류>) 갱신함: <바뀐 필드> [<grade>]`
- 보류: `[커밋시각] commit <해시7> → 판단 보류: <파일 경로> - <이유> [<grade>]`
- 추론이 들어간 내용을 승인받았으면 줄 끝에 ` (추론 포함: <필드>, 승인)`을 붙인다.
- 사용 예를 만들어 승인받았으면 줄 끝에 ` (생성 포함: 사용 예, 승인)`을 붙인다. 둘 다면 `(추론 포함: <필드>, 생성 포함: 사용 예, 승인)`.

## 하지 말 것
- `common-repo` 소스 코드를 수정하지 않는다. (커밋만 한다.)
- 승인 없이 커밋하거나 push하지 않는다.
- 사용자가 stage하지 않은 파일을 `git add`하거나 커밋에 넣지 않는다. (예외: 6단계의 정리집 파일)
- 커밋되지 않은 파일을 정리집에 반영하지 않는다. 작업 트리 파일을 직접 읽어서 정리하지 않는다.
- 어떤 커밋에도 없는 변경을 다른 커밋의 해시로 기록하지 않는다.
- 소스에서 확인되지 않은 내용을 승인 없이 정리집에 적지 않는다.
- 다른 프로젝트 저장소를 읽거나 사용처를 찾지 않는다. (`common-asset-notify`의 일이다.)
