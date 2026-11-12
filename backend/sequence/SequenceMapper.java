package com.company.common.sequence;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

@Mapper
public interface SequenceMapper {

    /** 해당 구분·일자의 순번을 1 올린다. 행이 없으면 1로 새로 만든다. */
    int upsertNextNo(@Param("seqType") String seqType, @Param("baseDate") String baseDate);

    /** 해당 구분·일자의 마지막 순번을 조회한다. */
    SequenceVO selectSequence(@Param("seqType") String seqType, @Param("baseDate") String baseDate);
}
