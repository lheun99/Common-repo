package com.company.common.util;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

/**
 * 공통 날짜/시간 변환 유틸 클래스.
 *
 * 화면과 API에서 주고받는 날짜 문자열 형식을 회사 표준(yyyy-MM-dd, yyyy-MM-dd HH:mm:ss)으로 통일한다.
 * 각 서비스에서 DateTimeFormatter를 따로 만들지 말고 이 클래스를 사용한다.
 *
 * 사용 예시:
 *   LocalDate d = DateTimeUtils.parseDate("2026-10-08");
 *   String s = DateTimeUtils.formatDateTime(LocalDateTime.now());
 *
 * 주의: 모든 메서드는 서버 기본 시간대 기준이다. 시간대 변환이 필요하면 호출부에서 처리한다.
 */
public final class DateTimeUtils {
    private static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    private static final DateTimeFormatter DATE_TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private DateTimeUtils() {
    }

    /**
     * @param text yyyy-MM-dd 형식의 날짜 문자열
     * @return 변환된 LocalDate
     * @throws IllegalArgumentException 형식이 맞지 않거나 null인 경우
     */
    public static LocalDate parseDate(String text) {
        if (text == null) {
            throw new IllegalArgumentException("날짜 문자열이 비어 있습니다.");
        }
        try {
            return LocalDate.parse(text.trim(), DATE);
        } catch (DateTimeParseException e) {
            throw new IllegalArgumentException("날짜 형식이 올바르지 않습니다: " + text, e);
        }
    }

    /**
     * @param date 변환할 날짜
     * @return yyyy-MM-dd 형식 문자열 (date가 null이면 빈 문자열)
     */
    public static String formatDate(LocalDate date) {
        return date == null ? "" : date.format(DATE);
    }

    /**
     * @param dateTime 변환할 일시
     * @return yyyy-MM-dd HH:mm:ss 형식 문자열 (dateTime이 null이면 빈 문자열)
     */
    public static String formatDateTime(LocalDateTime dateTime) {
        return dateTime == null ? "" : dateTime.format(DATE_TIME);
    }

    /**
     * 기간 검색 조건 검증용. 시작일이 종료일보다 늦으면 false.
     * 단, 둘 중 하나라도 null이면 기간 조건이 없는 것으로 보고 true를 반환한다.
     */
    public static boolean isValidRange(LocalDate from, LocalDate to) {
        return from == null || to == null || !from.isAfter(to);
    }
}
