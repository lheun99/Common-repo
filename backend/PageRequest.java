package com.company.common.paging;

/**
 * 공통 페이지 요청 파라미터를 검증하고 기본값을 채워주는 유틸 클래스.
 *
 * 컨트롤러에서 매번 page/size 파라미터를 직접 검증하지 말고 이 클래스를 통해 생성한다.
 * page는 1부터 시작하며, 0 이하로 들어오면 1로 보정한다.
 * size는 최소 1, 최대 100으로 제한한다 — DB 부하 방지를 위해 100을 넘는 값은 강제로 100으로 잘린다.
 *
 * 사용 예시:
 *   PageRequest pr = PageRequest.of(requestPage, requestSize);
 *   int offset = pr.getOffset();
 *
 * 주의: size에 음수를 넣으면 예외를 던지지 않고 기본값 20으로 대체한다. 호출부에서 별도 검증이
 * 필요 없다.
 */
public class PageRequest {
    private static final int DEFAULT_SIZE = 20;
    private static final int MAX_SIZE = 100;

    private final int page;
    private final int size;

    private PageRequest(int page, int size) {
        this.page = page;
        this.size = size;
    }

    /**
     * @param page 요청받은 페이지 번호 (1-base)
     * @param size 요청받은 페이지 크기
     * @return 검증·보정이 끝난 PageRequest
     */
    public static PageRequest of(int page, int size) {
        int safePage = page < 1 ? 1 : page;
        int safeSize = size <= 0 ? DEFAULT_SIZE : Math.min(size, MAX_SIZE);
        return new PageRequest(safePage, safeSize);
    }

    /** DB 조회용 OFFSET 값 (page는 1-base라 -1 보정한다) */
    public int getOffset() {
        return (page - 1) * size;
    }

    public int getPage() {
        return page;
    }

    public int getSize() {
        return size;
    }
}
