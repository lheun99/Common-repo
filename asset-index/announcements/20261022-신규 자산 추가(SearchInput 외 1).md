# 공통 자산 변경 정리
2026-10-22 · 공통팀
범위: 2026-10-15 ~ 2026-10-22 (커밋 2개)

> 설명 메모: 10월 15일부터 22일까지 추가된 신규 공통 자산 2건을 정리했습니다.

---

## 한눈에 보기

| 구분 | 자산 | 내용 | 할 일 |
|---|---|---|---|
| [신규] | SearchInput | 검색어 입력창 컴포넌트 추가 | 도입 검토 |
| [신규] | Holiday | 공휴일 조회·영업일 계산 API 추가 | 도입 검토 |

> 설명 메모: 이번 기간에는 비호환·동작 변경이 없고, 신규 자산 2건만 추가되었습니다.

---

## [신규] SearchInput — 검색어 입력창 (목록 화면 상단 검색용)

- Enter 키를 누르거나 '검색' 버튼을 누르면 검색이 실행됩니다.
- 검색어가 공백만이면 onSearch가 호출되지 않습니다.
- 입력값이 있고 disabled가 아니면 '지우기' 버튼이 표시됩니다.

사용 예
```tsx
<SearchInput
  value={keyword}
  onChange={setKeyword}
  onSearch={(k) => searchList(k)}
  placeholder="사용자명 검색"
/>
```

> 설명 메모: 목록 화면 상단의 검색어 입력창으로 도입을 검토해 보세요.

---

## [신규] Holiday — 공휴일 조회 및 영업일 계산 API

- 화면에서 달력에 공휴일을 표시하거나, 처리 예정일을 다음 영업일로 맞출 때 사용합니다.
- 서버 코드에서는 HolidayService를 주입해서 직접 호출합니다.
- 공휴일 목록은 연도별로 캐시되므로, 데이터가 바뀌어도 캐시 해제·서버 재시작 전까지 반영되지 않습니다.

사용 예
```
GET /api/holidays?year=2026
→ { "success": true, "data": [ { "holidayDate": "2026-01-01", "holidayName": "설날", "substituteYn": "N" } ] }

List<HolidayVO> holidays = holidayService.getHolidays(2026);
boolean off = holidayService.isHoliday(LocalDate.of(2026, 1, 1));
LocalDate next = holidayService.nextBusinessDay(LocalDate.of(2026, 1, 1));
```

**API**: GET /api/holidays · GET /api/holidays/check · GET /api/holidays/next-business-day
**함께 쓰는 자산**: ApiResponse, DateTimeUtils
**영향 프로젝트**: shop-app 2곳, admin-app 1곳, hr-app 1곳

> 설명 메모: 연도별 공휴일 조회, 쉬는 날 여부 확인, 다음 영업일 구하기를 사용할 수 있습니다.

---

## 마무리

- 자세한 내용은 공통 자산 탐색 페이지에서 확인할 수 있습니다.
- 개별 수정 요청은 담당자에게 따로 알림이 갔습니다.
- 문의: 공통팀

> 설명 메모: 도입 검토나 문의는 공통팀으로 해 주세요.