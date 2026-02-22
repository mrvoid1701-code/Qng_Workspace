param(
    [Parameter(Mandatory = $true)]
    [string]$Title,

    [ValidateSet("page", "claim", "derivation", "model")]
    [string]$Type = "page"
)

$templateMap = @{
    page = "templates/page-note-template.md"
    claim = "templates/claim-template.md"
    derivation = "templates/derivation-template.md"
    model = "templates/model-test-template.md"
}

$outDirMap = @{
    page = "01_notes"
    claim = "02_claims"
    derivation = "03_math/derivations"
    model = "04_models"
}

$templatePath = $templateMap[$Type]
$outDir = $outDirMap[$Type]

if (-not (Test-Path -LiteralPath $templatePath)) {
    throw "Template not found: $templatePath"
}

if (-not (Test-Path -LiteralPath $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

$date = Get-Date -Format "yyyy-MM-dd"
$slug = $Title.ToLower() -replace "[^a-z0-9]+", "-" -replace "^-|-$", ""
if ([string]::IsNullOrWhiteSpace($slug)) {
    $slug = "note"
}

$filename = "$date-$slug.md"
$targetPath = Join-Path $outDir $filename

$content = Get-Content -LiteralPath $templatePath -Raw
$content = $content.Replace("{{TITLE}}", $Title).Replace("{{DATE}}", $date)

Set-Content -LiteralPath $targetPath -Value $content -Encoding utf8
Write-Output "Created: $targetPath"

