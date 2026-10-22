package com.company.common.holiday;

import java.time.LocalDate;

/**
 * 공휴일 한 건.
 */
public class HolidayVO {

    /** 공휴일 날짜 */
    private LocalDate holidayDate;

    /** 공휴일 이름 (예: 설날, 추석) */
    private String holidayName;

    /** 대체공휴일 여부 */
    private boolean substitute;

    public LocalDate getHolidayDate() {
        return holidayDate;
    }

    public void setHolidayDate(LocalDate holidayDate) {
        this.holidayDate = holidayDate;
    }

    public String getHolidayName() {
        return holidayName;
    }

    public void setHolidayName(String holidayName) {
        this.holidayName = holidayName;
    }

    public boolean isSubstitute() {
        return substitute;
    }

    public void setSubstitute(boolean substitute) {
        this.substitute = substitute;
    }
}
