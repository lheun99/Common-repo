package com.company.common.holiday;

import java.time.LocalDate;
import java.util.List;

/**
 * 공휴일·영업일 계산 서비스.
 */
public interface HolidayService {

    /**
     * @param year 조회할 연도
     * @return 해당 연도의 공휴일 목록 (날짜 오름차순)
     */
    List<HolidayVO> getHolidays(int year);

    /**
     * @param date 확인할 날짜
     * @return 쉬는 날이면 true
     */
    boolean isHoliday(LocalDate date);

    /**
     * 기준일로부터 days 영업일 뒤의 날짜를 구한다. 기준일 당일은 세지 않는다.
     *
     * @param date 기준일
     * @param days 더할 영업일 수 (1 이상)
     * @return days 영업일 뒤의 날짜
     */
    LocalDate addBusinessDays(LocalDate date, int days);
}
