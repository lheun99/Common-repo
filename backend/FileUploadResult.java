package com.company.common.file;

/**
 * 파일 업로드 결과로 반환되는 정보.
 *
 * storedFileName은 다운로드 API(GET /api/files/{storedFileName}) 호출 시 그대로 사용한다.
 */
public class FileUploadResult {
    private final String originalFileName;
    private final String storedFileName;
    private final long size;

    public FileUploadResult(String originalFileName, String storedFileName, long size) {
        this.originalFileName = originalFileName;
        this.storedFileName = storedFileName;
        this.size = size;
    }

    public String getOriginalFileName() {
        return originalFileName;
    }

    public String getStoredFileName() {
        return storedFileName;
    }

    public long getSize() {
        return size;
    }
}
