package com.company.common.sequence;

/**
 * 채번 기준 한 건.
 */
public class SequenceVO {

    /** 채번 대상 구분 (예: ORDER, APPROVAL) */
    private String seqType;

    /** 채번 기준 일자 (yyyyMMdd) */
    private String baseDate;

    /** 현재까지 발급된 마지막 순번 */
    private int lastNo;

    public String getSeqType() {
        return seqType;
    }

    public void setSeqType(String seqType) {
        this.seqType = seqType;
    }

    public String getBaseDate() {
        return baseDate;
    }

    public void setBaseDate(String baseDate) {
        this.baseDate = baseDate;
    }

    public int getLastNo() {
        return lastNo;
    }

    public void setLastNo(int lastNo) {
        this.lastNo = lastNo;
    }
}
