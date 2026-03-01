param(
    [string]$RegisterPath = "02_claims/claims-register.md",
    [string]$OutputDir = "02_claims/claims"
)

if (-not (Test-Path -LiteralPath $RegisterPath)) {
    throw "Register file not found: $RegisterPath"
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$lines = Get-Content -LiteralPath $RegisterPath
$rows = @()

foreach ($line in $lines) {
    if ($line -match '^\|\s*QNG-C-\d{3}\s*\|') {
        $parts = $line -split '\|'
        if ($parts.Count -lt 8) {
            continue
        }

        $row = [PSCustomObject]@{
            ClaimID = $parts[1].Trim()
            Statement = $parts[2].Trim()
            Status = $parts[3].Trim()
            Confidence = $parts[4].Trim()
            SourcePages = $parts[5].Trim()
            RelatedDerivation = $parts[6].Trim()
        }
        $rows += $row
    }
}

foreach ($row in $rows) {
    $path = Join-Path $OutputDir ($row.ClaimID + ".md")
    $content = @(
        "# $($row.ClaimID)"
        ""
        "- Status: $($row.Status)"
        "- Confidence: $($row.Confidence)"
        "- Source page(s): $($row.SourcePages)"
        "- Related derivation: $($row.RelatedDerivation)"
        "- Register source: 02_claims/claims-register.md"
        ""
        "## Claim Statement"
        ""
        "$($row.Statement)"
        ""
        "## Assumptions"
        ""
        "- TODO"
        ""
        "## Mathematical Form"
        ""
        "- TODO"
        ""
        "## Potential Falsifier"
        ""
        "- TODO"
        ""
        "## Evidence / Notes"
        ""
        "- TODO"
        ""
        "## Next Action"
        ""
        "- TODO"
        ""
    )
    Set-Content -LiteralPath $path -Value $content -Encoding utf8
}

$indexLines = @(
    "# Claim Files Index"
    ""
    "| Claim ID | File | Status | Confidence | Source page(s) |"
    "| --- | --- | --- | --- | --- |"
)

foreach ($row in $rows) {
    $indexLines += "| $($row.ClaimID) | 02_claims/claims/$($row.ClaimID).md | $($row.Status) | $($row.Confidence) | $($row.SourcePages) |"
}

Set-Content -LiteralPath "02_claims/claim-files-index.md" -Value $indexLines -Encoding utf8

Write-Output ("Generated claim files: " + $rows.Count)
Write-Output "Index: 02_claims/claim-files-index.md"
