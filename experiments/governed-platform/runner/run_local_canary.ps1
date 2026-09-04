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

function Resolve-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) {
    return @($python.Source)
  }

  $py = Get-Command py -ErrorAction SilentlyContinue
  if ($py) {
    return @($py.Source, "-3")
  }

  throw "Python 3 was not found on PATH. Install Python 3 or make the 'python' or 'py' launcher available, then rerun this script."
}

function Invoke-PythonFile {
  param(
    [Parameter(Mandatory=$true)][string]$ScriptPath,
    [Parameter(ValueFromRemainingArguments=$true)][string[]]$Arguments
  )

  $cmd = Resolve-PythonCommand
  $exe = $cmd[0]
  $prefix = @()
  if ($cmd.Count -gt 1) {
    $prefix = $cmd[1..($cmd.Count - 1)]
  }

  & $exe @prefix $ScriptPath @Arguments
  if ($LASTEXITCODE -ne 0) {
    throw "Python command failed with exit code $LASTEXITCODE: $ScriptPath"
  }
}

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "Checking Ollama..."
$version = & ollama --version
Write-Host $version

$models = & ollama list
if (($models -join "`n") -notmatch [regex]::Escape($Model)) {
  throw "Required local model '$Model' is not installed."
}

Write-Host "Checking Python..."
$pythonCmd = Resolve-PythonCommand
Write-Host ("Python launcher: " + ($pythonCmd -join " "))

Write-Host "Preparing blinded envelope..."
Invoke-PythonFile (Join-Path $RunnerDir "prepare_run.py") `
  --case $CasePath `
  --mechanisms $MechanismsPath `
  --mechanism-id $MechanismId `
  --instruction-version $InstructionVersion `
  --out $EnvelopePath

Write-Host "Running local blinded canary through Ollama..."
Invoke-PythonFile (Join-Path $RunnerDir "run_ollama_canary.py") `
  --envelope $EnvelopePath `
  --model $Model `
  --out $ResultPath

Write-Host "CANARY_RAW_RESULT=$ResultPath"
$result = Get-Content $ResultPath -Raw | ConvertFrom-Json
$result | Select-Object run_id,case_id,case_version,mechanism_id,mechanism_version,provider,status,input_tokens,output_tokens,estimated_cost_usd,latency_ms,evidence_eligible | Format-List
Write-Host "--- RAW MODEL OUTPUT ---"
Write-Host $result.raw_output
