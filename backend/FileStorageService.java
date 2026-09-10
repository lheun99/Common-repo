package com.company.common.file;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.core.io.UrlResource;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.net.MalformedURLException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

/**
 * 로컬 디스크 기반 공통 파일 저장/조회 서비스.
 *
 * 업로드된 파일은 원본 파일명 대신 UUID 기반 파일명으로 저장한다 — 파일명 충돌과
 * 경로 조작(path traversal)을 막기 위함. 원본 파일명은 FileUploadResult에만 담아
 * 반환하고, 실제 다운로드는 항상 storedFileName으로만 조회한다.
 */
@Service
public class FileStorageService {

    private final Path storageRoot;

    public FileStorageService(@Value("${app.file.upload-dir:uploads}") String uploadDir) {
        this.storageRoot = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(storageRoot);
        } catch (IOException e) {
            throw new IllegalStateException("업로드 디렉터리를 생성할 수 없습니다: " + storageRoot, e);
        }
    }

    /**
     * @param file 업로드할 파일 (비어있으면 IllegalArgumentException)
     * @return 저장 결과 (원본/저장 파일명, 크기)
     */
    public FileUploadResult store(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("업로드할 파일이 비어 있습니다.");
        }

        String originalFileName = StringUtils.cleanPath(
                file.getOriginalFilename() == null ? "" : file.getOriginalFilename());
        String extension = "";
        int dotIndex = originalFileName.lastIndexOf('.');
        if (dotIndex >= 0) {
            extension = originalFileName.substring(dotIndex);
        }
        String storedFileName = UUID.randomUUID() + extension;

        try {
            Path target = storageRoot.resolve(storedFileName).normalize();
            Files.copy(file.getInputStream(), target);
            return new FileUploadResult(originalFileName, storedFileName, file.getSize());
        } catch (IOException e) {
            throw new IllegalStateException("파일 저장에 실패했습니다: " + originalFileName, e);
        }
    }

    /**
     * @param storedFileName store()가 반환한 저장 파일명
     * @return 다운로드용 Resource (파일이 없으면 IllegalArgumentException)
     */
    public Resource loadAsResource(String storedFileName) {
        try {
            Path target = storageRoot.resolve(storedFileName).normalize();
            if (!target.startsWith(storageRoot)) {
                throw new IllegalArgumentException("잘못된 파일 경로입니다: " + storedFileName);
            }
            Resource resource = new UrlResource(target.toUri());
            if (!resource.exists() || !resource.isReadable()) {
                throw new IllegalArgumentException("파일을 찾을 수 없습니다: " + storedFileName);
            }
            return resource;
        } catch (MalformedURLException e) {
            throw new IllegalArgumentException("파일을 찾을 수 없습니다: " + storedFileName, e);
        }
    }
}
