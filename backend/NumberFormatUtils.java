package com.company.common.util;

import java.text.DecimalFormat;

/**
 * 숫자 표시 형식 유틸 클래스.
 *
 * 금액·수량을 화면에 보여 줄 때 회사 표준(천 단위 쉼표)으로 통일한다.
 *
 * 사용 예시:
 *   String s = NumberFormatUtils.formatAmount(1234567);  // 1,234,567
 *   String t = NumberFormatUtils.formatAmount(null);     // 0
 */
public final class NumberFormatUtils {
    private static final String PATTERN = "#,##0";

    private NumberFormatUtils() {
    }

    /**
     * @param amount 금액 또는 수량
     * @return 천 단위 쉼표가 들어간 문자열 (null이면 "0")
     */
    public static String formatAmount(Number amount) {
        if (amount == null) {
            return "0";
        }
        return new DecimalFormat(PATTERN).format(amount);
    }
}
