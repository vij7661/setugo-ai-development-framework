param(
    [string]$Model = "openai/gpt-oss-20b",
    [string]$MechanismId = "remote-reasoner-a",
    [string]$InstructionVersion = "pilot1-canary-v1",
    [string]$OutDir = "$env:TEMP\setugo-pilot1-groq-canary"
)

$ErrorActionPreference = "Stop"
$RunnerDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExperimentDir = Split-Path -Parent $RunnerDir

function Resolve-PythonCommand {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        return [pscustomobject]@{ Exe = $python.Source; Prefix = @() }
    }
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        return [pscustomobject]@{ Exe = $py.Source; Prefix = @("-3") }
    }
    throw "Python 3 was not found on PATH."
}

function Invoke-PythonFile {
    param([string]$Script, [string[]]$Arguments)
    $cmd = Resolve-PythonCommand
    & $cmd.Exe @($cmd.Prefix) $Script @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code ${LASTEXITCODE}: $Script"
    }
}

if (-not $env:GROQ_API_KEY) {
    throw "GROQ_API_KEY is not available in this PowerShell session. Close and reopen the terminal after setx, or set it for this session before running."
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$casePath = Join-Path $ExperimentDir "cases\pilot\model-visible\EXP-A-001.json"
$mechanismsPath = Join-Path $RunnerDir "mechanisms.remote-free.example.json"
$envelopePath = Join-Path $OutDir "EXP-A-001.envelope.json"
$resultPath = Join-Path $OutDir "EXP-A-001.groq.raw-result.json"

Write-Host "Checking Python..."
$pythonCmd = Resolve-PythonCommand
Write-Host "Python launcher: $($pythonCmd.Exe)"
Write-Host "Preparing blinded envelope..."
Invoke-PythonFile (Join-Path $RunnerDir "prepare_run.py") @(
    "--case", $casePath,
    "--mechanisms", $mechanismsPath,
    "--mechanism-id", $MechanismId,
    "--instruction-version", $InstructionVersion,
    "--out", $envelopePath
)

Write-Host "Running blinded remote canary through Groq..."
Invoke-PythonFile (Join-Path $RunnerDir "run_remote_canary.py") @(
    "--envelope", $envelopePath,
    "--provider", "groq",
    "--base-url", "https://api.groq.com/openai/v1",
    "--model", $Model,
    "--api-key-env", "GROQ_API_KEY",
    "--timeout-seconds", "120",
    "--out", $resultPath
)

Write-Host "Canary result: $resultPath"
$result = Get-Content $resultPath -Raw | ConvertFrom-Json
$result | Select-Object run_id, case_id, case_version, mechanism_id, mechanism_version, provider, status, input_tokens, output_tokens, estimated_cost_usd, latency_ms, evidence_eligible | Format-List
Write-Host "Raw model output:"
Write-Host $result.raw_output
