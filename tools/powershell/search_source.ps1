param(
    [Parameter(Mandatory = $true)]
    [string]$Pattern
)

if (-not (Test-Path -LiteralPath "01_notes/source_text.md")) {
    throw "Missing file: 01_notes/source_text.md. Run extract_pdf_text.py first."
}

rg -n --text --ignore-case --line-number --context 1 -- "$Pattern" "01_notes/source_text.md"
