package com.company.common.holiday;

import java.time.LocalDate;
import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface HolidayMapper {

    List<HolidayVO> selectHolidayList(@Param("year") Integer year);

    int selectHolidayCount(@Param("date") LocalDate date);
}
