param(
    [string]$Remote = "origin",
    [string]$Branch = "main"
)

# Ensure we're in a git repo
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    Write-Error "Not inside a git repository. Run this from your repo root."
    exit 1
}

Write-Output "Fetching from $Remote..."
git fetch $Remote

Write-Output "Pulling $Remote/$Branch..."
$pull = git pull $Remote $Branch
Write-Output $pull

if ($LASTEXITCODE -ne 0) {
    Write-Error "git pull failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Output "Pull complete."
