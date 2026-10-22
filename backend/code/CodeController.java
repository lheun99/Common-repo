package com.company.common.code;

import com.company.common.response.ApiResponse;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 공통코드 조회 API.
 *
 * 화면의 선택 박스 목록이나 상태값 표시 이름을 공통코드에서 가져올 때 사용한다.
 * 서버 코드에서는 CodeService를 주입해서 직접 호출한다.
 */
@RestController
@RequestMapping("/api/codes")
public class CodeController {

    private final CodeService codeService;

    public CodeController(CodeService codeService) {
        this.codeService = codeService;
    }

    /**
     * 코드 그룹의 코드 목록을 조회한다.
     *
     * @param groupCode 코드 그룹 (예: GENDER, ORDER_STATUS)
     */
    @GetMapping("/{groupCode}")
    public ApiResponse<List<CodeVO>> list(@PathVariable String groupCode) {
        return ApiResponse.success(codeService.getCodes(groupCode));
    }

    /**
     * 코드의 표시 이름을 조회한다.
     *
     * @param groupCode 코드 그룹
     * @param code      코드값
     */
    @GetMapping("/{groupCode}/{code}/name")
    public ApiResponse<String> name(@PathVariable String groupCode, @PathVariable String code) {
        return ApiResponse.success(codeService.getCodeName(groupCode, code));
    }
}
