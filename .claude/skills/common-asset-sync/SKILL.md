---
name: common-asset-sync
description: 공통팀이 "공통 자산 정리해줘"라고 하면 사용. common-repo 변경분을 커밋하고, 커밋 내용과 소스를 읽어 common-sync-demo의 공통 자산 정리집(asset-index.json)을 갱신한 뒤 정리집도 커밋한다. 사람이 직접 커밋해서 밀려 있는 커밋도 함께 정리한다.
---

# 공통 자산 정리 (커밋 + 정리집 갱신)

## 경로

- 공통 코드 저장소: `common-repo` (이 스킬이 들어 있는 저장소)
- 정리집 저장소: `common-repo/../common-sync-demo`
  - 정리집: `asset-index.json`
  - 추출 규칙: `index-agent-prompt.md` ← **자산 판별·필드 추출 규칙은 반드시 이 파일을 읽고 따른다**
  - 로그: `logs/automation.log`
- 밀린 커밋 대기열: `common-repo/.git/common-asset-pending.txt`
  (post-commit 훅이 커밋 해시를 한 줄씩 적어 둔다. 사람이 직접 커밋한 것도 여기에 쌓인다.)

## 순서

### 1. 변경 사항 확인
- `git -C common-repo status`와 `git -C common-repo diff`로 변경된 파일을 확인한다.
- 변경 사항이 **없으면** 2단계를 건너뛰고 3단계(밀린 커밋 정리)로 간다.

### 2. 공통 코드 커밋 (사용자 확인 후)
- 변경 내용을 보고 커밋 메시지를 작성한다. (예: `feat: Pagination 컴포넌트 추가`)
- 사용자에게 아래를 보여 주고 **"이대로 커밋할까요? push까지 할까요?"** 를 묻는다.
  - 포함할 파일 목록
  - 커밋 메시지
- 승인받으면 해당 파일만 `git add` 후 커밋한다. (`git add -A`로 관계없는 파일을 섞지 않는다.)
- 커밋하면 post-commit 훅이 해시를 대기열에 자동으로 추가한다.

### 3. 정리 대상 커밋 모으기
- 대기열 파일의 해시 목록을 읽는다. (파일이 없거나 비어 있으면 정리할 것이 없다고 보고하고 끝낸다.)
- 이미 `asset-index.json`의 `addedInCommit`에 있는 해시는 건너뛴다.

### 4. 정리집 갱신
커밋마다 다음을 수행한다.
- `git -C common-repo show --stat <해시>`, `git -C common-repo diff-tree --no-commit-id --name-status -r <해시>`로 바뀐 파일을 확인한다.
- 대상 파일의 **실제 소스**(`git -C common-repo show <해시>:<경로>`)를 읽는다.
- `index-agent-prompt.md` 규칙대로 항목을 추가하거나 갱신하고, `logs/automation.log`에 기록한다.
- `asset-index.json`은 **UTF-8**, 들여쓰기 2칸의 올바른 JSON으로 저장한다.

### 5. 정리집 커밋
- `common-sync-demo`에서 `asset-index.json`과 `logs/automation.log`만 커밋한다.
  - 메시지: `docs: 공통 자산 정리집 갱신 (<짧은 해시들>)`
- 2단계에서 push 승인을 받았다면 두 저장소 모두 push한다.
- 처리한 해시를 대기열 파일에서 지운다.

### 6. 결과 보고
- 커밋한 내용 (두 저장소 각각의 해시)
- 정리집에 추가되거나 갱신된 자산 이름과 종류
- 판단 보류한 항목과 그 이유

## 하지 말 것
- `common-repo` 소스 코드를 수정하지 않는다. (커밋만 한다.)
- 승인 없이 커밋하거나 push하지 않는다.
- 소스에 없는 내용을 지어내서 정리집에 적지 않는다.
