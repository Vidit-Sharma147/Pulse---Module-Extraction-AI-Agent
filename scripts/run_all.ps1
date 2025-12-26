Param(
    [ValidateSet("All","Setup","Smoke","Samples","UI","API","DockerBuild","DockerUI","DockerAPI")]
    [string]$Task = "All",
    [int]$MaxPages = 6,
    [int]$PerDomainLimit = 5
)

function Write-Header($text) {
    Write-Host "`n==== $text ====\n" -ForegroundColor Cyan
}

function Setup-Env {
    Write-Header "Setting up virtual environment + dependencies"
    if (-not (Test-Path ".venv")) {
        python -m venv .venv
    }
    . .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

function Run-Smoke {
    Write-Header "Running smoke test (WordPress docs)"
    . .venv\Scripts\Activate.ps1
    python module_extractor.py --urls https://wordpress.org/documentation/ --max-pages $MaxPages --per-domain-limit $PerDomainLimit
}

function Run-Samples {
    Write-Header "Running samples test (2 URLs, saving output)"
    . .venv\Scripts\Activate.ps1
    # Save small-limit combined output to samples\two_sites_small.json
    python tests/save_small_samples.py
    # Also print to console with current limits
    python tests/run_samples.py --max-pages $MaxPages --per-domain-limit $PerDomainLimit
}

function Run-UI {
    Write-Header "Starting Streamlit UI (new window)"
    . .venv\Scripts\Activate.ps1
    Start-Process -FilePath "powershell" -ArgumentList ".venv\\Scripts\\Activate.ps1; streamlit run streamlit_app.py" -WindowStyle Normal
}

function Run-API {
    Write-Header "Starting FastAPI server (new window)"
    . .venv\Scripts\Activate.ps1
    Start-Process -FilePath "powershell" -ArgumentList ".venv\\Scripts\\Activate.ps1; uvicorn fastapi_app:app --host 0.0.0.0 --port 8000" -WindowStyle Normal
}

function Docker-Build {
    Write-Header "Building Docker image"
    docker build -t pulse-extractor .
}

function Docker-Run-UI {
    Write-Header "Running Docker (Streamlit UI on :8501)"
    docker run -p 8501:8501 pulse-extractor
}

function Docker-Run-API {
    Write-Header "Running Docker (FastAPI on :8000)"
    docker run -p 8000:8000 --entrypoint uvicorn pulse-extractor fastapi_app:app --host 0.0.0.0 --port 8000
}

switch ($Task) {
    "Setup" { Setup-Env }
    "Smoke" { Setup-Env; Run-Smoke }
    "Samples" { Setup-Env; Run-Samples }
    "UI" { Setup-Env; Run-UI }
    "API" { Setup-Env; Run-API }
    "DockerBuild" { Docker-Build }
    "DockerUI" { Docker-Build; Docker-Run-UI }
    "DockerAPI" { Docker-Build; Docker-Run-API }
    Default { Setup-Env; Run-Smoke; Run-Samples; Write-Host "`nDone. Use Task=UI or Task=API to launch services." -ForegroundColor Green }
}
