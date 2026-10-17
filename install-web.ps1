[CmdletBinding()]
param(
    [string]$Branch = "main",
    [string]$Dir = "",
    [switch]$Force,
    [string[]]$Frameworks = @("codex"),
    [string]$Repo = "JiamingShi-JsPhys/Js_Agent-Skills",
    [ValidateSet("user", "project")]
    [string]$Scope = "user",
    [string[]]$Skill = @("*")
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
}
catch {
}

$FrameworkLabels = @{
    claude    = "Claude Code"
    codex     = "OpenAI Codex"
    dsh       = "DeepSeek Harness"
    workbuddy = "WorkBuddy"
}

$UserRoots = @{
    claude    = ".claude\skills"
    codex     = ".codex\skills"
    dsh       = ".dsh\skills"
    workbuddy = ".workbuddy\skills"
}

$ProjectRoots = @{
    claude    = ".claude\skills"
    codex     = ".agents\skills"
    dsh       = ".dsh\skills"
    workbuddy = ".workbuddy\skills"
}

$InstallManifest = @{
    "Js_conflict-detector"          = @("SKILL.md", "skill.json", "src", "config/examples")
    "Js_document-evolution-tracker" = @("SKILL.md", "skill.json", "src", "config/examples")
    "Js_formula-validator"          = @("SKILL.md", "skill.json", "scripts")
    "Js_longitudinal-analysis"      = @("SKILL.md", "skill.json", "src", "R", "config/examples")
    "Js_multi-dim-manager"          = @("SKILL.md", "skill.json", "scripts", "config.example.yaml")
    "Js_task-organizer"             = @("SKILL.md", "skill.json", "scripts")
}

function Resolve-TargetRoot {
    param([string]$Framework, [string]$Scope, [string]$ProjectDir)
    if ($Scope -eq "user") {
        return (Join-Path $HOME $UserRoots[$Framework])
    }
    return (Join-Path $ProjectDir $ProjectRoots[$Framework])
}

$badFw = $Frameworks | Where-Object { -not $FrameworkLabels.ContainsKey($_) }
if ($badFw) {
    throw "Unknown framework(s): $($badFw -join ', '). Choose from: $($FrameworkLabels.Keys -join ', ')"
}

if ($Scope -eq "project") {
    if ([string]::IsNullOrWhiteSpace($Dir)) {
        $Dir = (Get-Location).Path
    }
    if (-not (Test-Path -LiteralPath $Dir)) {
        throw "Task folder not found: $Dir"
    }
}

$token = [guid]::NewGuid().ToString("N")
$archive = Join-Path $env:TEMP "Js_Agent-Skills-$token.zip"
$expand = Join-Path $env:TEMP "Js_Agent-Skills-$token"

try {
    $url = "https://codeload.github.com/$Repo/zip/refs/heads/$Branch"
    Write-Host "Js_Agent-Skills web installer"
    Write-Host "  source  : $Repo @ $Branch"
    Write-Host "  scope   : $Scope$(if ($Scope -eq 'project') { " -> $Dir" })"
    Write-Host "  targets : $(($Frameworks | ForEach-Object { $FrameworkLabels[$_] }) -join ', ')"
    Write-Host ""
    Write-Host "Downloading repository archive ..."
    
    Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing
    
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    [System.IO.Compression.ZipFile]::ExtractToDirectory($archive, $expand)
    
    $root = Get-ChildItem -Path $expand -Directory | Select-Object -First 1
    if (-not $root) {
        throw "Archive did not contain a repository folder: $archive"
    }

    $allSkills = Get-ChildItem -Path $root.FullName -Directory |
        Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") } |
        Select-Object -ExpandProperty Name
        
    if (-not $allSkills) {
        throw "No skill (folder with SKILL.md) found in $Repo @ $Branch"
    }
    
    if ($Skill -contains "*" -or $Skill -contains "all") {
        $skills = $allSkills
    }
    else {
        $skills = @()
        foreach ($name in $Skill) {
            if ($allSkills -contains $name) {
                $skills += $name
            }
            else {
                throw "Skill '$name' not found. Available: $($allSkills -join ', ')"
            }
        }
    }
    
    Write-Host "  skills  : $($skills -join ', ')"
    Write-Host ""

    $installed = 0
    $skipped = 0
    $failed = @()
    
    foreach ($name in $skills) {
        $src = Join-Path $root.FullName $name
        foreach ($fw in $Frameworks) {
            $label = $FrameworkLabels[$fw]
            $targetRoot = Resolve-TargetRoot -Framework $fw -Scope $Scope -ProjectDir $Dir
            $dst = Join-Path $targetRoot $name
            
            if (Test-Path -LiteralPath $dst) {
                if ($Force) {
                    Remove-Item -LiteralPath $dst -Recurse -Force
                }
                else {
                    Write-Host ("  SKIP  {0,-24} {1,-14} already exists (use -Force)" -f $name, $label)
                    $skipped++
                    continue
                }
            }
            
            New-Item -ItemType Directory -Path $targetRoot -Force | Out-Null
            New-Item -ItemType Directory -Path $dst -Force | Out-Null
            
            $keep = $InstallManifest[$name]
            $installOk = $true
            
            if ($keep) {
                foreach ($rel in $keep) {
                    $item = Join-Path $src $rel
                    if (-not (Test-Path -LiteralPath $item)) {
                        Write-Host ("  FAIL  {0,-24} {1,-14} manifest entry missing: {2}" -f $name, $label, $rel)
                        $installOk = $false
                        continue
                    }
                    Copy-Item -LiteralPath $item -Destination (Join-Path $dst $rel) -Recurse -Force
                }
            }
            else {
                Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
            }
            
            if ($installOk -and (Test-Path -LiteralPath (Join-Path $dst "SKILL.md"))) {
                Write-Host ("  OK    {0,-24} {1,-14} {2}" -f $name, $label, $dst)
                $installed++
            }
            else {
                Write-Host ("  FAIL  {0,-24} {1,-14} verification failed" -f $name, $label)
                $failed += "$name -> $label"
            }
        }
    }

    Write-Host ""
    if ($failed.Count -gt 0) {
        Write-Host "Installation finished with errors:" -ForegroundColor Red
        $failed | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        exit 1
    }
    
    Write-Host "Installation complete: $installed skill install(s), $skipped skipped."
    if ($Scope -eq "project") {
        Write-Host "Only this task folder can see the skill(s): $Dir"
    }
    else {
        Write-Host "Every project of the selected framework(s) can use the skill(s)."
    }
    exit 0
}
finally {
    Remove-Item -LiteralPath $expand -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $archive -Force -ErrorAction SilentlyContinue
}
