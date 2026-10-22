package com.company.common.code;

/**
 * 공통코드 한 건.
 */
public class CodeVO {

    /** 코드값 (예: M, F) */
    private String code;

    /** 표시 이름 (예: 남, 여) */
    private String codeName;

    /** 정렬 순서 */
    private int sortOrder;

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getCodeName() {
        return codeName;
    }

    public void setCodeName(String codeName) {
        this.codeName = codeName;
    }

    public int getSortOrder() {
        return sortOrder;
    }

    public void setSortOrder(int sortOrder) {
        this.sortOrder = sortOrder;
    }
}
