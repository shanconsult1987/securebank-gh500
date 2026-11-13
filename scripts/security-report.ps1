
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Owner,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$Repository,

    [string]$OutputDirectory = ".\artifacts"
)

$ErrorActionPreference = "Stop"

# --------------------------------------------------
# 1. Validate GitHub authentication
# --------------------------------------------------

$Token = $env:GITHUB_TOKEN

if ([string]::IsNullOrWhiteSpace($Token)) {
    throw "GITHUB_TOKEN is not set. Configure it before running this script."
}

# --------------------------------------------------
# 2. Configure GitHub API headers
# --------------------------------------------------

$Headers = @{
    Authorization = "Bearer $Token"
    Accept = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

$BaseUrl = "https://api.github.com/repos/$Owner/$Repository"

# --------------------------------------------------
# 3. Generic GitHub API pagination function
# --------------------------------------------------

function Get-GitHubPages {

    param(
        [Parameter(Mandatory = $true)]
        [string]$Endpoint
    )

    $Results = @()

    $Url = "$BaseUrl/$Endpoint?per_page=100"

    do {

        Write-Host "Retrieving: $Endpoint"

        try {

            $Response = Invoke-WebRequest `
                -Uri $Url `
                -Headers $Headers `
                -Method Get `
                -ErrorAction Stop

            $Data = $Response.Content | ConvertFrom-Json

            if ($Data -is [System.Array]) {
                $Results += @($Data)
            }
            elseif ($null -ne $Data) {
                $Results += $Data
            }

            # Follow GitHub's pagination Link header.
            $NextLink = $null

            if ($Response.Headers.ContainsKey("Link")) {

                $LinkHeader = [string]$Response.Headers["Link"]

                foreach ($Part in ($LinkHeader -split ",")) {

                    if ($Part -match '<([^>]+)>;\s*rel="next"') {
                        $NextLink = $Matches[1]
                        break
                    }

                }
            }

            $Url = $NextLink

        }
        catch {

            $StatusCode = $null

            if ($_.Exception.Response) {
                $StatusCode = [int]$_.Exception.Response.StatusCode
            }

            throw "GitHub API request failed for '$Endpoint'. HTTP status: $StatusCode. Details: $($_.Exception.Message)"
        }

    } while (-not [string]::IsNullOrWhiteSpace($Url))

    return ,$Results
}

# --------------------------------------------------
# 4. Retrieve all three security alert categories
# --------------------------------------------------

Write-Host ""
Write-Host "====================================="
Write-Host " SECUREBANK GITHUB SECURITY REPORT"
Write-Host "====================================="

$Dependabot = @(
    Get-GitHubPages "dependabot/alerts?state=open"
)

$CodeScanning = @(
    Get-GitHubPages "code-scanning/alerts?state=open"
)

$SecretScanning = @(
    Get-GitHubPages "secret-scanning/alerts?state=open"
)

# --------------------------------------------------
# 5. Build consolidated report
# --------------------------------------------------

$Report = [PSCustomObject]@{

    Repository = "$Owner/$Repository"

    GeneratedAt = (
        Get-Date
    ).ToUniversalTime().ToString("o")

    Summary = [PSCustomObject]@{

        Dependabot = $Dependabot.Count

        CodeScanning = $CodeScanning.Count

        SecretScanning = $SecretScanning.Count

        TotalAlerts = (
            $Dependabot.Count +
            $CodeScanning.Count +
            $SecretScanning.Count
        )
    }

    DependabotAlerts = $Dependabot

    CodeScanningAlerts = $CodeScanning

    SecretScanningAlerts = $SecretScanning
}

# --------------------------------------------------
# 6. Create output directory
# --------------------------------------------------

$Root = Get-Location

$FullOutputDirectory = Join-Path `
    $Root `
    $OutputDirectory

New-Item `
    -ItemType Directory `
    -Path $FullOutputDirectory `
    -Force | Out-Null

# --------------------------------------------------
# 7. Export timestamped JSON
# --------------------------------------------------

$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

$OutputFile = Join-Path `
    $FullOutputDirectory `
    "security-report-$Timestamp.json"

$Report |
    ConvertTo-Json -Depth 50 |
    Set-Content -Path $OutputFile -Encoding utf8

# --------------------------------------------------
# 8. Display summary
# --------------------------------------------------

Write-Host ""
Write-Host "========= SECURITY SUMMARY ========="

Write-Host "Repository      : $Owner/$Repository"

Write-Host "Dependabot      : $($Dependabot.Count)"

Write-Host "Code Scanning   : $($CodeScanning.Count)"

Write-Host "Secret Scanning : $($SecretScanning.Count)"

Write-Host "Total Alerts    : $($Report.Summary.TotalAlerts)"

Write-Host "===================================="

Write-Host ""
Write-Host "Report generated successfully:"
Write-Host $OutputFile
