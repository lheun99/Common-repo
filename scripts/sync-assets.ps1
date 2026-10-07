param(
    [Parameter(Mandatory=$true)]
    [string]$CommitHash,
    
    [Parameter(Mandatory=$true)]
    [string]$RepoRoot,
    
    [Parameter(Mandatory=$false)]
    [string]$CommonSyncDemo = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$PromptFile = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$DiffOutput = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$CommitMessage = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$CommitDate = $null,
    
    [Parameter(Mandatory=$false)]
    [string]$LogDir = $null
)

# common-sync-demo 경로 설정
if ($CommonSyncDemo) {
    $CommonSyncDemoPath = $CommonSyncDemo
} else {
    $CommonSyncDemoPath = Join-Path $RepoRoot "..\common-sync-demo"
}
$AssetIndexPath = Join-Path $CommonSyncDemoPath "asset-index.json"
$LogDirPath = Join-Path $CommonSyncDemoPath "logs"

# 로그 디렉터리 생성
if ($LogDirPath -and -not (Test-Path $LogDirPath)) {
    New-Item -ItemType Directory -Path $LogDirPath -Force | Out-Null
}

# AI 지시서 파일 경로
if (-not $PromptFile) {
    $PromptFile = Join-Path $CommonSyncDemoPath "index-agent-prompt.md"
}

# 커밋 정보 수집 (인자가 없으면 Git 에서 조회)
if (-not $CommitMessage) {
    $CommitMessage = git -C $RepoRoot log -1 --format=%s $CommitHash
}
if (-not $CommitDate) {
    $CommitDate = git -C $RepoRoot log -1 --format=%aI $CommitHash
}
if (-not $DiffOutput) {
    $DiffOutput = git -C $RepoRoot diff-tree --no-commit-id --name-status -r $CommitHash
}

Write-Host "=== Asset Index Sync (AI-Powered) ===" -ForegroundColor Cyan
Write-Host "Commit: $CommitHash"
Write-Host "Message: $CommitMessage"
Write-Host "Date: $CommitDate"
Write-Host "Prompt: $PromptFile"
Write-Host ""

# AI 지시서 읽기
$PromptContent = ""
if (Test-Path $PromptFile) {
    $PromptContent = Get-Content -Path $PromptFile -Raw -Encoding UTF8
    Write-Host "Loaded AI prompt from: $PromptFile"
} else {
    Write-Host "Warning: Prompt file not found. Using default rules." -ForegroundColor Yellow
}

# 기존 asset-index.json 읽기
$ExistingIndex = $null
if (Test-Path $AssetIndexPath) {
    $ExistingContent = Get-Content -Path $AssetIndexPath -Raw -Encoding UTF8
    $ExistingIndex = $ExistingContent | ConvertFrom-Json
    Write-Host "Existing assets: $($ExistingIndex.assets.Count)"
} else {
    $ExistingIndex = @{ assets = @() }
    Write-Host "No existing asset index found."
}

# 변경된 파일 분석
$NewAssets = @()
$UpdatedAssetNames = @()

$DiffOutput | ForEach-Object {
    if ($_ -match '^(A|M)\s+(.+)$') {
        $status = $Matches[1]
        $filePath = $Matches[2]
        
        # components/ 또는 backend/ 디렉토리만 처리
        if ($filePath -notmatch '^components/|^backend/') {
            return
        }
        
        # 파일명 추출
        $fileName = Split-Path -Leaf $filePath
        $name = [System.IO.Path]::GetFileNameWithoutExtension($fileName)
        
        # Type 결정
        if ($filePath -match '^components/') {
            $type = "frontend-component"
        } else {
            $type = "backend-module"
        }
        
        $relativePath = "common-repo/" + $filePath
        
        # 파일 내용 읽기
        $fullPath = Join-Path $RepoRoot $filePath
        $fileContent = $null
        if (Test-Path $fullPath) {
            try {
                $fileContent = Get-Content -Path $fullPath -Raw -Encoding UTF8
            } catch {
                try {
                    $bytes = [System.IO.File]::ReadAllBytes($fullPath)
                    $fileContent = [System.Text.Encoding]::GetEncoding(949).GetString($bytes)
                } catch {
                    $fileContent = ""
                }
            }
        }
        
        # AI 지시서에 따른 자산 추출
        $purpose = "자동 생성된 자산"
        $propsOrUsage = @()
        $detail = $null
        
        if ($fileContent) {
            if ($type -eq "frontend-component") {
                # JSDoc 주석에서 purpose 추출
                $jsdocMatch = $fileContent | Select-String -Pattern '/\*\*[\s\S]*?\*/' -AllMatches
                if ($jsdocMatch) {
                    $jsdoc = $jsdocMatch[0].Matches[0].Value
                    $purposeMatch = $jsdoc | Select-String -Pattern '\*\s+(.+)' -AllMatches
                    if ($purposeMatch) {
                        $purpose = $purposeMatch[0].Matches[0].Groups[1].Value.Trim()
                    }
                    # detail: 모든 주석 모음
                    $detail = $jsdoc -replace '/\*\*|\*/', '' -replace '\*\s?', ''
                }
                
                # Props 추출
                $interfaceMatch = $fileContent | Select-String -Pattern 'interface\s+\w+[\s\S]*?\{[\s\S]*?\}' -AllMatches
                if ($interfaceMatch) {
                    $interface = $interfaceMatch[0].Matches[0].Value
                    $props = $interface | Select-String -Pattern '\w+:\s*\w+' | ForEach-Object {
                        ($_ | Select-String -Pattern '\w+(?=:)').Value
                    }
                    if ($props) { $propsOrUsage = $props }
                }
            } else {
                # Javadoc 주석에서 purpose 추출
                $javadocMatch = $fileContent | Select-String -Pattern '/\*\*[\s\S]*?\*/' -AllMatches
                if ($javadocMatch) {
                    $javadoc = $javadocMatch[0].Matches[0].Value
                    $purposeMatch = $javadoc | Select-String -Pattern '\*\s+(.+)' -AllMatches
                    if ($purposeMatch) {
                        $purpose = $purposeMatch[0].Matches[0].Groups[1].Value.Trim()
                    }
                    # detail: 모든 주석 모음
                    $detail = $javadoc -replace '/\*\*|\*/', '' -replace '\*\s?', ''
                }
                
                # Public 메서드 추출
                $publicMethods = $fileContent | Select-String -Pattern 'public\s+\w+\s+\w+\s*\([^)]*\)' | ForEach-Object {
                    $_.Matches[0].Value
                }
                if ($publicMethods) { $propsOrUsage = $publicMethods }
            }
        }
        
        # Asset 객체 생성
        $asset = [PSCustomObject]@{
            type = $type
            name = $name
            path = $relativePath
            purpose = $purpose
            props = $propsOrUsage
            detail = $detail
            addedInCommit = $CommitHash
            addedAt = $CommitDate
        }
        
        $NewAssets += $asset
        $UpdatedAssetNames += $name
        Write-Host "  - Analyzed: $name ($type)" -ForegroundColor Green
    }
}

# 기존 자산 업데이트
$FinalAssets = @()

# 업데이트된 자산 추가
foreach ($name in $UpdatedAssetNames) {
    $newAsset = $NewAssets | Where-Object { $_.name -eq $name }
    if ($newAsset) {
        $FinalAssets += $newAsset
    }
}

# 기존 자산 중 업데이트되지 않은 것 추가
foreach ($existingAsset in $ExistingIndex.assets) {
    if ($UpdatedAssetNames -notcontains $existingAsset.name) {
        $FinalAssets += $existingAsset
    }
}

# JSON 생성 및 저장
Write-Host "FinalAssets type: $($FinalAssets.GetType().Name)" -ForegroundColor Gray
Write-Host "FinalAssets count: $($FinalAssets.Count)" -ForegroundColor Gray

if ($FinalAssets -and $FinalAssets.Count -gt 0) {
    $OutputIndex = @{ assets = $FinalAssets }
    $JsonOutput = $OutputIndex | ConvertTo-Json -Depth 10
    
    Write-Host "JSON output length: $($JsonOutput.Length)" -ForegroundColor Gray
    
    if ($JsonOutput -and $JsonOutput.Length -gt 0) {
        try {
            # UTF-8 인코딩으로 파일 저장 (BOM 없음)
            $Utf8Encoding = New-Object System.Text.UTF8Encoding $false
            [System.IO.File]::WriteAllText($AssetIndexPath, $JsonOutput, $Utf8Encoding)
            Write-Host "Saved asset index to: $AssetIndexPath" -ForegroundColor Green
        } catch {
            Write-Host "Error saving file: $_" -ForegroundColor Red
        }
    } else {
        Write-Host "Warning: JSON output is empty" -ForegroundColor Yellow
    }
} else {
    Write-Host "Warning: FinalAssets is empty or null" -ForegroundColor Yellow
}

# 로그 기록
if ($LogDirPath) {
    $LogFilePath = Join-Path $LogDirPath "automation.log"
    # 한글 인코딩 처리
    $LogEntry = "[$CommitDate] commit $CommitHash → index 에 $($UpdatedAssetNames.Count) 개 자산 추가함 (AI 자동)"
    # UTF-8 BOM 없이 로그 기록
    $Utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::AppendAllText($LogFilePath, $LogEntry + "`n", $Utf8NoBom)
    Write-Host "Logged to: $LogFilePath"
}

Write-Host ""
Write-Host "=== Sync Complete ===" -ForegroundColor Cyan
Write-Host "Files processed: $($NewAssets.Count)"
Write-Host "Total assets: $($FinalAssets.Count)"
Write-Host "Output: $AssetIndexPath"
