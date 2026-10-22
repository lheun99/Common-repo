package com.company.common.holiday;

import com.company.common.response.ApiResponse;
import com.company.common.util.DateTimeUtils;
import java.time.LocalDate;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

/**
 * 공휴일 조회 및 영업일 계산 API.
 *
 * 화면에서 달력에 공휴일을 표시하거나, 처리 예정일을 다음 영업일로 맞출 때 사용한다.
 * 서버 코드에서는 HolidayService를 주입해서 직접 호출한다.
 */
@RestController
@RequestMapping("/api/holidays")
public class HolidayController {

    private final HolidayService holidayService;

    public HolidayController(HolidayService holidayService) {
        this.holidayService = holidayService;
    }

    /**
     * 연도별 공휴일 목록을 조회한다.
     *
     * @param year 조회할 연도 (생략하면 올해)
     */
    @GetMapping
    public ApiResponse<List<HolidayVO>> list(@RequestParam(required = false) Integer year) {
        int targetYear = (year != null) ? year : LocalDate.now().getYear();
        return ApiResponse.success(holidayService.getHolidays(targetYear));
    }

    /**
     * 해당 날짜가 쉬는 날인지 확인한다.
     *
     * @param date yyyy-MM-dd 형식의 날짜
     */
    @GetMapping("/check")
    public ApiResponse<Boolean> check(@RequestParam String date) {
        return ApiResponse.success(holidayService.isHoliday(DateTimeUtils.parseDate(date)));
    }

    /**
     * 기준일 다음의 첫 영업일을 구한다.
     *
     * @param date yyyy-MM-dd 형식의 기준일
     */
    @GetMapping("/next-business-day")
    public ApiResponse<String> nextBusinessDay(@RequestParam String date) {
        LocalDate next = holidayService.nextBusinessDay(DateTimeUtils.parseDate(date));
        return ApiResponse.success(DateTimeUtils.formatDate(next));
    }
}
