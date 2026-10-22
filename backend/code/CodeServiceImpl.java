package com.company.common.code;

import java.util.List;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class CodeServiceImpl implements CodeService {

    private final CodeMapper codeMapper;

    public CodeServiceImpl(CodeMapper codeMapper) {
        this.codeMapper = codeMapper;
    }

    @Override
    @Cacheable(value = "commonCodes", key = "#groupCode")
    public List<CodeVO> getCodes(String groupCode) {
        if (groupCode == null || groupCode.isBlank()) {
            throw new IllegalArgumentException("groupCode는 필수입니다.");
        }
        return codeMapper.selectCodeList(groupCode.toUpperCase());
    }

    @Override
    public String getCodeName(String groupCode, String code) {
        String name = codeMapper.selectCodeName(groupCode.toUpperCase(), code);
        return (name != null) ? name : code;
    }
}
