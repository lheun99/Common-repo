package com.company.common.sequence;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.regex.Pattern;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class SequenceServiceImpl implements SequenceService {

    private static final Pattern PREFIX_PATTERN = Pattern.compile("^[A-Z]{2,10}$");
    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyyMMdd");

    private final SequenceMapper sequenceMapper;

    public SequenceServiceImpl(SequenceMapper sequenceMapper) {
        this.sequenceMapper = sequenceMapper;
    }

    @Override
    public String issueNumber(String prefix) {
        return issueNumber(prefix, LocalDate.now().format(DATE_FORMAT));
    }

    @Override
    @Transactional
    public String issueNumber(String prefix, String baseDate) {
        if (prefix == null || !PREFIX_PATTERN.matcher(prefix).matches()) {
            throw new IllegalArgumentException("prefix는 영문 대문자 2~10자여야 합니다.");
        }
        if (baseDate == null || !baseDate.matches("\d{8}")) {
            throw new IllegalArgumentException("baseDate는 yyyyMMdd 형식이어야 합니다.");
        }
        sequenceMapper.upsertNextNo(prefix, baseDate);
        SequenceVO seq = sequenceMapper.selectSequence(prefix, baseDate);
        return String.format("%s-%s-%04d", prefix, baseDate, seq.getLastNo());
    }
}
