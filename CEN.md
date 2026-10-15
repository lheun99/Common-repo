# common-repo: 공통 컴포넌트 및 백엔드 모듈 저장소

## 프로젝트 구조

```
common-repo/
├── backend/          # Java/Spring 공통 모듈 (파일 업로드/다운로드 API)
│   ├── ApiResponse.java      # 공통 API 응답 포맷 (성공/실패 통일)
│   ├── FileController.java   # 파일 업로드/다운로드 컨트롤러
│   ├── FileStorageService.java # 로컬 디스크 기반 파일 저장 서비스
│   └── ...
├── asset-index/      # 공통 자산 정리 결과물 (스킬이 갱신)
│   ├── asset-index.json  # 공통 자산 정리집 (MCP 서버·탐색 페이지가 읽음)
│   ├── automation.log    # 정리 기록
│   ├── projects.json     # 영향도 스캔 대상 프로젝트 목록 (공통팀이 관리)
│   ├── changes/          # 변경 기록 (커밋별 변경 등급·요약·할 일)
│   ├── notifications/    # 관련자 알림 (나중에 PMS로 보낼 내용)
│   └── announcements/    # 전파 자료 원고 (매뉴얼)
├── components/       # React 공통 UI 컴포넌트 (.tsx)
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   └── ...
└── .claude/skills/   # IntelliCEN 스킬 정의
    ├── common-asset-sync/      # 공통 자산 정리
    ├── common-asset-notify/    # 영향도 확인 및 관련자 알림
    └── common-asset-announce/  # 전파 자료(매뉴얼) 작성
```

## 공통 자산 스킬

세 스킬은 `asset-index/changes/`의 변경 기록을 중심으로 이어진다. 절차와 규칙의 원본은 각 스킬의 SKILL.md 하나다.
이 문서에는 개요만 적는다. 실행할 때는 반드시 해당 SKILL.md를 읽고 그대로 따른다.

| 스킬 | 요청 예 | 하는 일 | 결과물 |
|---|---|---|---|
| `common-asset-sync` | "공통 자산 정리해줘" | stage된 변경 커밋 → 소스 분석 → 정리집 갱신 → 변경 등급 판정 | `asset-index.json`, `changes/*.json` |
| `common-asset-notify` | "공통 변경 알림 보내줘", "Pagination 쓰는 곳 찾아줘" | `projects.json`의 프로젝트 소스를 스캔해 사용처·담당자 파악 | `notifications/*.json` |
| `common-asset-announce` | "전파 자료 만들어줘" | 아직 전파하지 않은 변경을 모아 공지·발표 원고 작성 | `announcements/*.md` |

### 공통 주의사항

- **커밋된 내용만 다룬다.** 소스는 `git show <해시>:<경로>`로 읽는다.
- `common-repo` 소스 코드와 다른 프로젝트 저장소를 **수정하지 않는다.**
- 승인 없이 커밋하거나 push하지 않는다. 반영 전에는 항상 미리보기를 채팅 본문에 먼저 보여 준다.
- 정리집·알림·원고 등 **공개되는 결과물에는 `(AI 추론)` 같은 표시를 넣지 않는다.** 그런 표시는 미리보기에서만 쓴다.
- JSON 파일은 UTF-8, 들여쓰기 2칸의 올바른 JSON으로 저장한다.

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

## 관련 저장소

- 정리집을 읽는 도구(MCP 서버, 탐색 페이지)는 별도 저장소 `../common-sync-demo`에 있다.
- 영향도 스캔 대상 프로젝트는 `asset-index/projects.json`에 등록한다.
