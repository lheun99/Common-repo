package com.company.common.code;

import java.util.List;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface CodeMapper {

    List<CodeVO> selectCodeList(@Param("groupCode") String groupCode);

    String selectCodeName(@Param("groupCode") String groupCode, @Param("code") String code);
}
