package com.company.common.dept;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface DeptMapper {

    DeptVO selectDept(@Param("deptCode") String deptCode);

    List<DeptVO> selectChildList(@Param("parentDeptCode") String parentDeptCode);
}
