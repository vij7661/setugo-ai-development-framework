param(
  [string]$Model = "qwen3:4b",
  [string]$MechanismId = "local-reasoner-a",
  [string]$InstructionVersion = "pilot1-canary-v1",
  [string]$OutDir = "$env:TEMP\setugo-pilot1-canary"
)

$ErrorActionPreference = "Stop"
$RunnerDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExperimentRoot = Split-Path -Parent $RunnerDir
$CasePath = Join-Path $ExperimentRoot "cases\pilot\model-visible\EXP-A-001.json"
$MechanismsPath = Join-Path $RunnerDir "mechanisms.local-ollama.example.json"
$EnvelopePath = Join-Path $OutDir "EXP-A-001.envelope.json"
$ResultPath = Join-Path $OutDir "EXP-A-001.ollama-result.json"

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "Checking Ollama..."
$version = & ollama --version
Write-Host $version

$models = & ollama list
if (($models -join "`n") -notmatch [regex]::Escape($Model)) {
  throw "Required local model '$Model' is not installed."
}

Write-Host "Preparing blinded envelope..."
python (Join-Path $RunnerDir "prepare_run.py") `
  --case $CasePath `
  --mechanisms $MechanismsPath `
  --mechanism-id $MechanismId `
  --instruction-version $InstructionVersion `
  --out $EnvelopePath

Write-Host "Running local blinded canary through Ollama..."
python (Join-Path $RunnerDir "run_ollama_canary.py") `
  --envelope $EnvelopePath `
  --model $Model `
  --out $ResultPath

Write-Host "CANARY_RAW_RESULT=$ResultPath"
$result = Get-Content $ResultPath -Raw | ConvertFrom-Json
$result | Select-Object run_id,case_id,case_version,mechanism_id,mechanism_version,provider,status,input_tokens,output_tokens,estimated_cost_usd,latency_ms,evidence_eligible | Format-List
Write-Host "--- RAW MODEL OUTPUT ---"
Write-Host $result.raw_output
