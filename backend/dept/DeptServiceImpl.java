package com.company.common.dept;

import java.util.List;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@Transactional(readOnly = true)
public class DeptServiceImpl implements DeptService {

    private final DeptMapper deptMapper;

    public DeptServiceImpl(DeptMapper deptMapper) {
        this.deptMapper = deptMapper;
    }

    @Override
    public DeptVO getDept(String deptCode) {
        if (deptCode == null || deptCode.isBlank()) {
            throw new IllegalArgumentException("deptCode는 필수입니다.");
        }
        return deptMapper.selectDept(deptCode);
    }

    @Override
    public String getDeptName(String deptCode) {
        DeptVO dept = getDept(deptCode);
        return (dept != null) ? dept.getDeptName() : "";
    }

    @Override
    public List<DeptVO> getChildDepts(String parentDeptCode) {
        if (parentDeptCode == null || parentDeptCode.isBlank()) {
            throw new IllegalArgumentException("parentDeptCode는 필수입니다.");
        }
        return deptMapper.selectChildList(parentDeptCode);
    }
}
