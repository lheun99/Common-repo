# common-repo: 공통 컴포넌트 및 백엔드 모듈 저장소

## 프로젝트 구조

```
common-repo/
├── backend/          # Java/Spring 공통 모듈 (파일 업로드/다운로드 API)
│   ├── ApiResponse.java      # 공통 API 응답 포맷 (성공/실패 통일)
│   ├── FileController.java   # 파일 업로드/다운로드 컨트롤러
│   ├── FileStorageService.java # 로컬 디스크 기반 파일 저장 서비스
│   └── ...
├── asset-index/      # 공통 자산 정리집 (스킬이 갱신)
│   ├── asset-index.json  # 정리집 (MCP 서버·탐색기가 읽음)
│   └── automation.log    # 정리 기록
├── components/       # React 공통 UI 컴포넌트 (.tsx)
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   └── ...
└── .claude/skills/   # IntelliCEN 스킬 정의
    └── common-asset-sync/
        └── SKILL.md
```

## 핵심 워크플로우: 공통 자산 정리 (common-asset-sync)

**사용자 지시**: "공통 자산 정리해줘"

### 전체 흐름

1. **커밋할 파일 확인**: 사용자가 `git add` 로 **stage 해 둔 파일만** 대상 (`git diff --cached --name-status`)
   - stage 안 된 수정 파일·untracked 파일은 무시 (목록에도 넣지 않음)
2. **공통 코드 커밋** (사용자 승인 후):
   - stage된 파일 목록과 커밋 메시지 확인
   - 추가 `git add` 없이 **stage된 그대로** `git commit -m` (`-a`, `git add -A` 금지)
   - 커밋 후 post-commit 훅이 `.git/common-asset-pending.txt` 에 해시 자동 기록
3. **정리 대상 커밋 모으기**: `common-asset-pending.txt` 에서 해시 목록 읽기
4. **정리집 내용 구성 → 미리보기** (사용자 승인 후 반영): 추가/갱신/보류 항목, 로그 줄, 커밋 메시지를 먼저 보여 줌
   - 반영 대상: `asset-index/asset-index.json` (이 저장소 안)
   - 규칙: `.claude/skills/common-asset-sync/SKILL.md`의 "정리집 작성 규칙" 섹션
   - 로그: `asset-index/automation.log`
5. **정리집 커밋**: `asset-index/` 의 두 파일만 커밋 (`git commit ... -- <두 파일>`)
   - 메시지: `docs: 공통 자산 정리집 갱신 (<짧은 해시들>)`
6. **push** (마지막에 한 번 확인): 코드 커밋과 정리집 커밋을 함께 push
7. **결과 보고**: 추가/갱신된 자산, 보류 항목, 커밋 해시

### 자산 판별·필드 추출 규칙

`.claude/skills/common-asset-sync/SKILL.md`의 "정리집 작성 규칙" 섹션을 따른다. (규칙의 원본은 그 파일 하나다.)

### 주의사항

- **커밋된 내용만 정리**: 커밋되지 않은 파일은 정리집에 반영하지 않음. 소스는 `git show <해시>:<경로>` 로 읽음
- `common-repo` 소스 코드를 **수정하지 않음** (커밋만 함)
- 승인 없이 커밋/ push 하지 않음
- `asset-index.json` 은 **UTF-8, 들여쓰기 2 칸**의 올바른 JSON
- 소스에 없는 내용을 지어내지 않음

## 백엔드 파일 저장 서비스 특이점

`FileStorageService` 는 로컬 디스크 기반 파일 저장을 담당:

- **저장 경로**: `app.file.upload-dir` (기본값: `uploads/`)
- **파일명**: 원본 파일명 대신 `UUID + 확장자` 로 저장 (충돌 방지)
- **보안**:
  - `path traversal` 방지: `normalize()` 로 경로 검증
  - `storageRoot` 내부 파일만 접근 허용
- **API 엔드포인트**:
  - `POST /api/files` → 파일 업로드 (`ApiResponse<FileUploadResult>`)
  - `GET /api/files/{storedFileName}` → 파일 다운로드 (`ResponseEntity<Resource>`)

## 스킬 사용

- `common-asset-sync` 스킬: `common-repo` 변경분을 `asset-index/` 의 정리집에 반영
- 정리집을 읽는 도구(MCP 서버, 탐색기)는 별도 저장소 `../common-sync-demo` 에 있음
- 스킬 실행: `.claude/skills/common-asset-sync/SKILL.md` 참조
