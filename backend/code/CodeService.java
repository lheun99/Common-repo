package com.company.common.code;

import java.util.List;

/**
 * 공통코드 조회 서비스.
 */
public interface CodeService {

    /**
     * @param groupCode 코드 그룹
     * @return 코드 목록
     */
    List<CodeVO> getCodes(String groupCode);

    /**
     * @param groupCode 코드 그룹
     * @param code      코드값
     * @return 코드의 표시 이름
     */
    String getCodeName(String groupCode, String code);
}
