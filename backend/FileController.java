package com.company.common.file;

import com.company.common.response.ApiResponse;
import org.springframework.core.io.Resource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

/**
 * 공통 파일 업로드/다운로드 API.
 */
@RestController
@RequestMapping("/api/files")
public class FileController {

    private final FileStorageService fileStorageService;

    public FileController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    @PostMapping
    public ApiResponse<FileUploadResult> upload(@RequestParam("file") MultipartFile file) {
        return ApiResponse.success(fileStorageService.store(file));
    }

    @GetMapping("/{storedFileName}")
    public ResponseEntity<Resource> download(@PathVariable String storedFileName) {
        Resource resource = fileStorageService.loadAsResource(storedFileName);
        return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_OCTET_STREAM)
                .header(HttpHeaders.CONTENT_DISPOSITION,
                        ContentDisposition.attachment().filename(storedFileName).build().toString())
                .body(resource);
    }
}
