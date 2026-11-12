package com.company.common.sequence;

import com.company.common.response.ApiResponse;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 문서번호 채번 API.
 *
 * 화면에서 저장 전에 번호를 미리 받아야 할 때 사용한다.
 * 서버 코드에서는 SequenceService를 주입해서 직접 호출한다.
 */
@RestController
@RequestMapping("/api/sequences")
public class SequenceController {

    private final SequenceService sequenceService;

    public SequenceController(SequenceService sequenceService) {
        this.sequenceService = sequenceService;
    }

    /**
     * 다음 번호를 발급한다. 호출할 때마다 번호가 하나씩 올라가며 되돌릴 수 없다.
     *
     * @param prefix 번호 구분 (예: ORD)
     */
    @PostMapping("/{prefix}/next")
    public ApiResponse<String> next(@PathVariable String prefix) {
        return ApiResponse.success(sequenceService.nextNumber(prefix));
    }
}
