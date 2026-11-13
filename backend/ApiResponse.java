package com.company.common.response;

/**
 * 공통 API 응답 포맷 (성공/실패를 통일된 형태로 감싼다)
 */
public class ApiResponse<T> {
    private final boolean success;
    private final T data;
    private final String message;
    private final String code;

    private ApiResponse(boolean success, T data, String message, String code) {
        this.success = success;
        this.data = data;
        this.message = message;
        this.code = code;
    }

    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(true, data, null, null);
    }

    public static <T> ApiResponse<T> fail(String message) {
        return new ApiResponse<>(false, null, message, null);
    }

    /** 오류 코드를 함께 내려줄 때 쓴다. (예: fail("E1001", "주문을 찾을 수 없습니다")) */
    public static <T> ApiResponse<T> fail(String code, String message) {
        return new ApiResponse<>(false, null, message, code);
    }

    public boolean isSuccess() {
        return success;
    }

    public T getData() {
        return data;
    }

    public String getMessage() {
        return message;
    }

    /** 오류 코드 (fail(message)로 만든 응답이나 성공 응답은 null) */
    public String getCode() {
        return code;
    }
}
