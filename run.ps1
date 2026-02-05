# 获取用户输入
$defaultFile = "src/main.py"
$targetFile = Read-Host "请输入要运行的 Python 文件路径 (直接回车默认运行 $defaultFile)"

# 如果输入为空，使用默认参数
if ([string]::IsNullOrWhiteSpace($targetFile)) {
    $targetFile = $defaultFile
}

# 检查文件是否存在
if (-not (Test-Path $targetFile)) {
    Write-Host "[错误] 找不到文件: $targetFile" -ForegroundColor Red
    Read-Host "按下回车键退出..."
    exit
}

# 检查虚拟环境
$pythonPath = ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonPath)) {
    Write-Host "[错误] 找不到虚拟环境 (.venv\Scripts\python.exe)" -ForegroundColor Red
    Read-Host "按下回车键退出..."
    exit
}

# 运行程序
Write-Host "[运行] 正在启动 $targetFile ..." -ForegroundColor Cyan
& $pythonPath $targetFile

if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] 程序异常退出，错误代码: $LASTEXITCODE" -ForegroundColor Red
}

Read-Host "按下回车键退出..."
