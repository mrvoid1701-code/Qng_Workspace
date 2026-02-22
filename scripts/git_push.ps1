param(
    [string]$Remote = "origin",
    [string]$Branch = "main",
    [string]$Message = "Update workspace files"
)

# Ensure we're in a git repo
if (-not (git rev-parse --is-inside-work-tree 2>$null)) {
    Write-Error "Not inside a git repository. Run this from your repo root."
    exit 1
}

Write-Output "Staging all changes..."
git add --all

# Check for staged changes
$status = git status --porcelain
if (-not $status) {
    Write-Output "No changes to commit. Proceeding to push."
} else {
    Write-Output "Committing: $Message"
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
        Write-Error "git commit failed with exit code $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}

Write-Output "Pushing to $Remote/$Branch..."
git push $Remote $Branch
if ($LASTEXITCODE -ne 0) {
    Write-Error "git push failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Output "Push complete."
