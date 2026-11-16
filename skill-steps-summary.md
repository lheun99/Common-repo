# 공통 자산 정리 스킬 단계별 수행 요약

## 1. common-asset-sync (커밋 + 정리집 + 변경 기록)

| 단계 | 내용 | 도구 호출 |
|---|---|---|
| 1. 커밋할 파일 확인 | `git diff --cached`, `git status` | 2회 |
| 2. 공통 코드 커밋 | diff 확인 → 미리보기 출력 → 사용자 확인 → `git commit` → 메시지 확인 | 3회 + 질문 1회 |
| 3. 정리 대상 커밋 모으기 | 대기열 파일 읽기, `path_exists`, 커밋 정보 확인 | 4회 |
| 4. 정리집 내용 구성 | 이전/이후 소스 4개 읽기, asset-index.json 읽기 | 5회 |
| 5. 반영 전 미리보기 | 미리보기 출력 → 사용자 확인 | 질문 1회 |
| 6. 정리집 반영과 커밋 | asset-index.json 편집 5회, changes 파일 생성, log 편집, JSON 검증, `git add` + `git commit` | 9회 |
| 7. push 확인 | unpushed 확인 → 사용자 확인 → `git push` | 2회 + 질문 1회 |
| 8. 결과 보고 | 텍스트 출력 | - |

**총 도구 호출: 약 28회, 사용자 확인: 3회**

---

## 2. common-asset-notify (영향도 조사 + 개발자 정리)

| 단계 | 내용 | 도구 호출 |
|---|---|---|
| 1. 처리할 변경 기록 모으기 | `notified: false` grep, projects.json 읽기 | 2회 |
| 2. 사용처 스캔 | 3개 프로젝트 × (ls-files, grep import, grep 사용줄, hash-object, common-repo log) | 12회 |
| 3. 담당자 파악 | blame 5회 (shop-app 2, hr-app 3) + 복사본 log 1회 | 6회 |
| 4. 미리보기 | 미리보기 출력 → 사용자 확인 | 질문 1회 |
| 5. 정리 문서 생성과 커밋 | md 작성, changes json 편집, JSON 검증, `git add` + `git commit` + 메시지 확인 | 5회 |
| 6. push 확인 | unpushed 확인 → 사용자 확인 → `git push` | 2회 + 질문 1회 |
| 7. 결과 보고 | 텍스트 출력 | - |
| 8. 이어가기 질문 | 질문 1회 | 질문 1회 |

**총 도구 호출: 약 28회, 사용자 확인: 2회**

---

## 3. common-asset-dispatch (개발자별 알림 메시지 초안)

| 단계 | 내용 | 도구 호출 |
|---|---|---|
| 1. 처리할 정리 문서 모으기 | notifications/*.md glob, messages/*.json glob | 2회 |
| 2. 정리 문서 해석 | (notify에서 이미 확인한 내용 활용, 추가 호출 없음) | 0회 |
| 3. 수신자 확인과 메시지 만들기 | (notify에서 이미 blame으로 이메일 확인, 추가 호출 없음) | 0회 |
| 4. 미리보기 | 미리보기 출력 → 사용자 확인 | 질문 1회 |
| 5. 파일 생성과 커밋 | json 작성, JSON 검증, `git add` + `git commit` + 메시지 확인 | 4회 |
| 6. push 확인 | unpushed 확인 → 사용자 확인 → `git push` | 2회 + 질문 1회 |
| 7. 결과 보고 | 텍스트 출력 | - |

**총 도구 호출: 약 8회, 사용자 확인: 2회**

---

## 요약

| 스킬 | 도구 호출 | 사용자 확인 | 특징 |
|---|---|---|---|
| sync | ~28회 | 3회 | 소스 읽기·비교가 가장 많음 |
| notify | ~28회 | 2회 | 프로젝트별 스캔(blame·grep)이 가장 많음 |
| dispatch | ~8회 | 2회 | notify에서 이미 확인한 데이터를 재사용해 가장 적음 |

> dispatch가 가장 적은 이유는 notify 단계에서 이미 blame으로 이메일을 확인했고, 정리 문서 내용도 방금 만든 것이어서 추가 탐색이 불필요했기 때문이다.