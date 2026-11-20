package com.company.common.dept;

/**
 * 부서 한 건.
 */
public class DeptVO {

    /** 부서 코드 (예: D100) */
    private String deptCode;

    /** 부서 이름 (예: 영업1팀) */
    private String name;

    /** 상위 부서 코드. 최상위 부서는 null */
    private String parentDeptCode;

    /** 같은 상위 부서 안에서의 정렬 순서 */
    private int sortOrder;

    public String getDeptCode() {
        return deptCode;
    }

    public void setDeptCode(String deptCode) {
        this.deptCode = deptCode;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getParentDeptCode() {
        return parentDeptCode;
    }

    public void setParentDeptCode(String parentDeptCode) {
        this.parentDeptCode = parentDeptCode;
    }

    public int getSortOrder() {
        return sortOrder;
    }

    public void setSortOrder(int sortOrder) {
        this.sortOrder = sortOrder;
    }
}
