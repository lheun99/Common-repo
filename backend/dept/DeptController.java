package com.company.common.dept;

import com.company.common.response.ApiResponse;
import java.util.List;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 부서 조회 API.
 *
 * 화면에서 부서 이름이나 조직도를 보여 줄 때 사용한다.
 * 서버 코드에서는 DeptService를 주입해서 직접 호출한다.
 */
@RestController
@RequestMapping("/api/depts")
public class DeptController {

    private final DeptService deptService;

    public DeptController(DeptService deptService) {
        this.deptService = deptService;
    }

    /**
     * 부서 한 건을 조회한다.
     *
     * @param deptCode 부서 코드 (예: D100)
     */
    @GetMapping("/{deptCode}")
    public ApiResponse<DeptVO> get(@PathVariable String deptCode) {
        return ApiResponse.success(deptService.getDept(deptCode));
    }

    /**
     * 바로 아래 하위 부서 목록을 조회한다. 폐지된 부서는 제외한다.
     *
     * @param deptCode 상위 부서 코드
     */
    @GetMapping("/{deptCode}/children")
    public ApiResponse<List<DeptVO>> children(@PathVariable String deptCode) {
        return ApiResponse.success(deptService.getChildDepts(deptCode));
    }
}
