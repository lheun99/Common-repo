package com.company.common.sequence;

/**
 * 문서번호 채번 서비스.
 *
 * 주문번호, 결재번호처럼 "구분 + 날짜 + 일련번호" 형태의 번호를 발급할 때 사용한다.
 * 같은 구분·같은 날짜 안에서 번호는 중복 없이 1부터 순서대로 발급된다.
 *
 * 사용 예시:
 *   String no = sequenceService.nextNumber("ORD");  // ORD-20261112-0001
 */
public interface SequenceService {

    /**
     * 오늘 날짜 기준으로 다음 번호를 발급한다.
     *
     * @param prefix 번호 앞에 붙는 구분 (영문 대문자 2~10자, 예: ORD)
     * @return 발급된 번호 (예: ORD-20261112-0001)
     * @throws IllegalArgumentException prefix 형식이 맞지 않는 경우
     */
    String nextNumber(String prefix);

    /**
     * 지정한 일자 기준으로 다음 번호를 발급한다. (과거 일자 보정 등에 사용)
     *
     * @param prefix   번호 앞에 붙는 구분
     * @param baseDate 기준 일자 (yyyyMMdd)
     * @return 발급된 번호
     */
    String nextNumber(String prefix, String baseDate);
}
