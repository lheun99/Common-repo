# common-repo: 공통 컴포넌트 및 백엔드 모듈 저장소

## 프로젝트 구조

```
common-repo/
├── backend/          # Java/Spring 공통 모듈 (파일 업로드/다운로드 API)
│   ├── ApiResponse.java      # 공통 API 응답 포맷 (성공/실패 통일)
│   ├── FileController.java   # 파일 업로드/다운로드 컨트롤러
│   ├── FileStorageService.java # 로컬 디스크 기반 파일 저장 서비스
│   └── ...
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

1. **변경 사항 확인**: `git status` 로 `common-repo` 변경 파일 확인
2. **공통 코드 커밋** (사용자 승인 후):
   - 변경 파일 목록과 커밋 메시지 확인
   - `git add -A` 대신 **변경 파일만 선택적 추가** (`git add <파일>`)
   - 커밋 후 post-commit 훅이 `.git/common-asset-pending.txt` 에 해시 자동 기록
3. **정리 대상 커밋 모으기**: `common-asset-pending.txt` 에서 해시 목록 읽기
4. **정리집 갱신**: `common-sync-demo/asset-index.json` 업데이트
   - 대상 저장소: `../common-sync-demo`
   - 규칙 파일: `../common-sync-demo/index-agent-prompt.md`
   - 로그: `../common-sync-demo/logs/automation.log`
5. **정리집 커밋**: `common-sync-demo` 에서 `asset-index.json` 과 `logs/` 만 커밋
   - 메시지: `docs: 공통 자산 정리집 갱신 (<짧은 해시들>)`
6. **결과 보고**: 추가/갱신된 자산, 보류 항목, 커밋 해시

### 자산 판별 규칙

- **대상 디렉터리**: `components/` 또는 `backend/` 만 처리
- **Type 분류**:
  - `components/*.tsx` → `frontend-component`
  - `backend/*.java` → `backend-module`
- **자산명**: 파일명 (확장자 제거)
- **Props/메서드**:
  - Frontend: `interface XxxProps` 의 속성
  - Backend: `public` 메서드
- **Purpose**: JSDoc (`/** ... */`) 또는 Javadoc 에서 첫 줄 추출

### 주의사항

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

- `common-asset-sync` 스킬: `common-repo` 변경분을 `common-sync-demo` 의 정리집에 반영
- 스킬 실행: `.claude/skills/common-asset-sync/SKILL.md` 참조
