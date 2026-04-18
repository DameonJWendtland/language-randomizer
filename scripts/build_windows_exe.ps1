param(
    [switch]$IncludeSemanticModel
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$buildRoot = Join-Path $repoRoot "build\pyinstaller"
$specRoot = Join-Path $buildRoot "spec"
$distDir = Join-Path $repoRoot "dist"
$bundleDir = Join-Path $distDir "LanguageRandomizer"
$zipSuffix = if ($IncludeSemanticModel) { "-semantic" } else { "" }
$zipPath = Join-Path $distDir ("LanguageRandomizer-windows" + $zipSuffix + ".zip")
$mainScript = Join-Path $repoRoot "main.py"
$iconPath = Join-Path $repoRoot "language_randomizer\assets\translating.ico"
$semanticModelDir = Join-Path $repoRoot "build\semantic-model"
$semanticPackages = @(
    "sentence_transformers",
    "transformers",
    "torch",
    "tokenizers",
    "safetensors",
    "huggingface_hub",
    "sklearn",
    "scipy",
    "sympy",
    "mpmath",
    "joblib",
    "threadpoolctl"
)

Push-Location $repoRoot
try {
    New-Item -ItemType Directory -Path $buildRoot -Force | Out-Null
    New-Item -ItemType Directory -Path $specRoot -Force | Out-Null

    $pyInstallerArgs = @(
        "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--name", "LanguageRandomizer",
        "--specpath", $specRoot,
        "--workpath", $buildRoot,
        "--distpath", $distDir,
        "--icon", $iconPath,
        "--collect-all", "ttkthemes",
        "--collect-data", "language_randomizer"
    )

    if ($IncludeSemanticModel) {
        $hasSentenceTransformers = (
            python -c "import importlib.util; print('yes' if importlib.util.find_spec('sentence_transformers') else 'no')"
        ).Trim() -eq "yes"

        if (-not $hasSentenceTransformers) {
            throw "Semantic model build requested, but sentence-transformers is not installed."
        }

        if (Test-Path $semanticModelDir) {
            Remove-Item -LiteralPath $semanticModelDir -Recurse -Force
        }

        @"
from pathlib import Path
from sentence_transformers import SentenceTransformer

target = Path(r"$semanticModelDir")
target.mkdir(parents=True, exist_ok=True)
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
model.save(str(target))
"@ | python -

        if ($LASTEXITCODE -ne 0) {
            throw "Semantic model bundling failed with exit code $LASTEXITCODE."
        }

        foreach ($packageName in $semanticPackages) {
            $packageExists = (
                python -c "import importlib.util; print('yes' if importlib.util.find_spec('$packageName') else 'no')"
            ).Trim() -eq "yes"
            if ($packageExists) {
                $pyInstallerArgs += @("--collect-all", $packageName)
            }
        }

        $pyInstallerArgs += @("--add-data", "$semanticModelDir;language_randomizer\\semantic_model")
    }
    else {
        Write-Host "Skipping bundled semantic model for a smaller and faster package."
    }

    $pyInstallerArgs += $mainScript
    python @pyInstallerArgs

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed with exit code $LASTEXITCODE."
    }

    $legacySpec = Join-Path $repoRoot "LanguageRandomizer.spec"
    if (Test-Path $legacySpec) {
        Remove-Item -LiteralPath $legacySpec -Force
    }

    if (Test-Path $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    Compress-Archive -Path $bundleDir -DestinationPath $zipPath

    Write-Host ""
    Write-Host "Build complete:"
    Write-Host "  Mode: $(if ($IncludeSemanticModel) { 'Semantic/full' } else { 'Lite' })"
    Write-Host "  EXE: $bundleDir\\LanguageRandomizer.exe"
    Write-Host "  ZIP: $zipPath"
}
finally {
    Pop-Location
}
