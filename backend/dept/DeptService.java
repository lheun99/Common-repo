package com.company.common.dept;

import java.util.List;

/**
 * 부서 조회 서비스.
 */
public interface DeptService {

    /**
     * @param deptCode 부서 코드
     * @return 부서 정보. 없으면 null
     */
    DeptVO getDept(String deptCode);

    /**
     * @param deptCode 부서 코드
     * @return 부서 이름. 없으면 빈 문자열
     */
    String getDeptName(String deptCode);

    /**
     * @param parentDeptCode 상위 부서 코드
     * @return 바로 아래 하위 부서 목록
     */
    List<DeptVO> getChildDepts(String parentDeptCode);
}
