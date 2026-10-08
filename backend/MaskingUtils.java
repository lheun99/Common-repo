package com.company.common.util;

/**
 * 개인정보 마스킹 유틸 클래스.
 *
 * 화면 표시나 로그 출력 시 이름·휴대폰 번호·이메일·주민등록번호가 그대로 노출되지 않도록 일부를 *로 가린다.
 * 마스킹 규칙은 개인정보 보호 지침(2026-09 개정)을 따른다.
 *
 * 사용 예시:
 *   String name = MaskingUtils.maskName("홍길동");          // 홍*동
 *   String phone = MaskingUtils.maskPhone("010-1234-5678"); // 010-****-5678
 *
 * 주의: 마스킹된 값은 원래 값으로 되돌릴 수 없다. DB에는 반드시 원본(암호화된 값)을 저장하고, 마스킹은 출력 직전에만 한다.
 */
public final class MaskingUtils {
    private static final char MASK = '*';

    private MaskingUtils() {
    }

    /**
     * 이름의 가운데 글자를 가린다. 두 글자 이름은 마지막 글자를 가린다.
     *
     * @param name 원본 이름
     * @return 마스킹된 이름 (name이 null이거나 비어 있으면 그대로 반환)
     */
    public static String maskName(String name) {
        if (name == null || name.length() < 2) {
            return name;
        }
        if (name.length() == 2) {
            return name.charAt(0) + String.valueOf(MASK);
        }
        return name.charAt(0) + repeat(name.length() - 2) + name.charAt(name.length() - 1);
    }

    /**
     * 휴대폰 번호의 가운데 자리를 가린다.
     *
     * @param phone 하이픈(-)이 포함된 휴대폰 번호 (예: 010-1234-5678)
     * @return 마스킹된 번호 (예: 010-****-5678)
     * @throws IllegalArgumentException 하이픈으로 나눈 결과가 3부분이 아닌 경우
     */
    public static String maskPhone(String phone) {
        String[] parts = phone.split("-");
        if (parts.length != 3) {
            throw new IllegalArgumentException("휴대폰 번호 형식이 올바르지 않습니다: " + phone);
        }
        return parts[0] + "-" + repeat(parts[1].length()) + "-" + parts[2];
    }

    /**
     * 이메일 아이디의 앞 2글자만 남기고 가린다. 도메인은 가리지 않는다.
     *
     * @param email 원본 이메일
     * @return 마스킹된 이메일 (예: ho****@company.com). @가 없으면 그대로 반환
     */
    public static String maskEmail(String email) {
        int at = email == null ? -1 : email.indexOf('@');
        if (at < 0) {
            return email;
        }
        String id = email.substring(0, at);
        int keep = Math.min(2, id.length());
        return id.substring(0, keep) + repeat(id.length() - keep) + email.substring(at);
    }

    /**
     * 주민등록번호 뒷자리를 첫 글자만 남기고 가린다.
     * 단, 하이픈 없이 13자리로 들어오면 앞 6자리 뒤에 하이픈을 넣어 반환한다.
     *
     * @param rrn 주민등록번호 (예: 900101-1234567 또는 9001011234567)
     * @return 마스킹된 주민등록번호 (예: 900101-1******)
     */
    public static String maskRrn(String rrn) {
        String digits = rrn.replace("-", "");
        return digits.substring(0, 6) + "-" + digits.charAt(6) + repeat(6);
    }

    private static String repeat(int count) {
        return String.valueOf(MASK).repeat(Math.max(0, count));
    }
}
