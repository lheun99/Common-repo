package com.company.common.holiday;

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class HolidayServiceImpl implements HolidayService {

    private static final int MAX_SEARCH_DAYS = 60;

    private final HolidayMapper holidayMapper;

    public HolidayServiceImpl(HolidayMapper holidayMapper) {
        this.holidayMapper = holidayMapper;
    }

    @Override
    @Cacheable(value = "holidays", key = "#year")
    public List<HolidayVO> getHolidays(int year) {
        return holidayMapper.selectHolidayList(year);
    }

    @Override
    public boolean isHoliday(LocalDate date) {
        if (date == null) {
            throw new IllegalArgumentException("date는 필수입니다.");
        }
        DayOfWeek day = date.getDayOfWeek();
        if (day == DayOfWeek.SATURDAY || day == DayOfWeek.SUNDAY) {
            return true;
        }
        return holidayMapper.selectHolidayCount(date) > 0;
    }

    @Override
    public LocalDate nextBusinessDay(LocalDate date) {
        LocalDate candidate = date.plusDays(1);
        for (int i = 0; i < MAX_SEARCH_DAYS; i++) {
            if (!isHoliday(candidate)) {
                return candidate;
            }
            candidate = candidate.plusDays(1);
        }
        throw new IllegalStateException("영업일을 찾을 수 없습니다: " + date);
    }
}
