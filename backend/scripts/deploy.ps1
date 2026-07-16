# MemoryDay Backend Deployment Script for Windows
# This script automates the deployment process for Windows environments

param(
    [string]$Action = "deploy",
    [string]$ProjectDir = "C:\MemoryDay",
    [switch]$Help
)

# Configuration
$ProjectName = "memoryday"
$BackendDir = "$ProjectDir\backend"
$LogDir = "$ProjectDir\logs"

# Logging functions
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR" { "Red" }
        default { "Blue" }
    }
    
    Write-Host "[$timestamp] [$Level] $Message" -ForegroundColor $color
}

# Function to check requirements
function Test-Requirements {
    Write-Log "Checking system requirements..."
    
    # Check Python
    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Log "Python is not installed. Please install Python 3.8 or higher." -Level "ERROR"
        return $false
    }
    
    # Check pip
    if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
        Write-Log "pip is not installed. Please install pip." -Level "ERROR"
        return $false
    }
    
    Write-Log "System requirements check passed." -Level "SUCCESS"
    return $true
}

# Function to setup project directory
function Initialize-ProjectDirectory {
    Write-Log "Setting up project directory..."
    
    # Create directories
    if (-not (Test-Path $ProjectDir)) {
        New-Item -ItemType Directory -Path $ProjectDir -Force | Out-Null
    }
    
    if (-not (Test-Path $LogDir)) {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
    }
    
    # Copy project files
    if (Test-Path $BackendDir) {
        Write-Log "Project directory already exists. Updating..."
        # For now, we'll assume files are already there
    } else {
        Write-Log "Copying project files..."
        # Copy current directory to target
        Copy-Item -Path ".\*" -Destination $BackendDir -Recurse -Force
    }
    
    Write-Log "Project directory setup completed." -Level "SUCCESS"
}

# Function to setup Python environment
function Initialize-PythonEnvironment {
    Write-Log "Setting up Python environment..."
    
    Set-Location $BackendDir
    
    # Create virtual environment
    $venvPath = "$BackendDir\venv"
    if (-not (Test-Path $venvPath)) {
        python -m venv $venvPath
        Write-Log "Virtual environment created." -Level "SUCCESS"
    } else {
        Write-Log "Virtual environment already exists."
    }
    
    # Install dependencies
    & "$venvPath\Scripts\pip.exe" install --upgrade pip
    & "$venvPath\Scripts\pip.exe" install -r requirements.txt
    
    Write-Log "Python dependencies installed." -Level "SUCCESS"
}

# Function to setup environment configuration
function Initialize-Environment {
    Write-Log "Setting up environment configuration..."
    
    Set-Location $BackendDir
    
    if (-not (Test-Path ".env")) {
        if (Test-Path ".env.example") {
            Copy-Item ".env.example" ".env"
            Write-Log "Please edit .env file with your actual configuration." -Level "WARNING"
            Write-Host "Press any key to continue after editing .env file..." -ForegroundColor Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        } else {
            Write-Log ".env.example file not found. Please create a .env file manually." -Level "ERROR"
            return $false
        }
    } else {
        Write-Log ".env file already exists."
    }
    
    Write-Log "Environment configuration setup completed." -Level "SUCCESS"
    return $true
}

# Function to setup database
function Initialize-Database {
    Write-Log "Setting up database..."
    
    Set-Location $BackendDir
    $venvPath = "$BackendDir\venv"
    
    # Run migrations
    & "$venvPath\Scripts\python.exe" manage.py makemigrations
    & "$venvPath\Scripts\python.exe" manage.py migrate
    
    # Ask about creating superuser
    $createSuperuser = Read-Host "Do you want to create a superuser? (y/n)"
    if ($createSuperuser -eq "y" -or $createSuperuser -eq "Y") {
        & "$venvPath\Scripts\python.exe" manage.py createsuperuser
    }
    
    # Collect static files
    & "$venvPath\Scripts\python.exe" manage.py collectstatic --noinput
    
    Write-Log "Database setup completed." -Level "SUCCESS"
}

# Function to create Windows service
function Initialize-WindowsService {
    Write-Log "Setting up Windows service..."
    
    $serviceName = "MemoryDayBackend"
    $venvPath = "$BackendDir\venv"
    
    # Check if service already exists
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    
    if ($service) {
        Write-Log "Service already exists. Stopping and removing..."
        Stop-Service -Name $serviceName -Force
        sc.exe delete $serviceName
    }
    
    # Create service using NSSM (Non-Sucking Service Manager)
    # First check if NSSM is available
    if (-not (Get-Command nssm -ErrorAction SilentlyContinue)) {
        Write-Log "NSSM not found. Installing NSSM..." -Level "WARNING"
        
        # Download and install NSSM
        $nssmUrl = "https://nssm.cc/release/nssm-2.24.zip"
        $nssmZip = "$env:TEMP\nssm.zip"
        $nssmDir = "$env:TEMP\nssm"
        
        Invoke-WebRequest -Uri $nssmUrl -OutFile $nssmZip
        Expand-Archive -Path $nssmZip -DestinationPath $nssmDir -Force
        
        # Copy NSSM to system32
        $nssmExe = Get-ChildItem -Path $nssmDir -Recurse -Filter "nssm.exe" | Select-Object -First 1
        Copy-Item -Path $nssmExe.FullName -Destination "C:\Windows\System32\nssm.exe" -Force
        
        Remove-Item $nssmZip -Force
        Remove-Item $nssmDir -Recurse -Force
    }
    
    # Create service using NSSM
    nssm install $serviceName "$venvPath\Scripts\python.exe"
    nssm set $serviceName AppParameters "$BackendDir\start_server.py"
    nssm set $serviceName AppDirectory "$BackendDir"
    nssm set $serviceName DisplayName "MemoryDay Backend Service"
    nssm set $serviceName Description "MemoryDay Django Backend Application"
    nssm set $serviceName Start SERVICE_AUTO_START
    nssm set $serviceName AppStdout "$LogDir\service.log"
    nssm set $serviceName AppStderr "$LogDir\service-error.log"
    
    Write-Log "Windows service setup completed." -Level "SUCCESS"
}

# Function to start services
function Start-Services {
    Write-Log "Starting services..."
    
    $serviceName = "MemoryDayBackend"
    
    Start-Service -Name $serviceName
    Start-Sleep -Seconds 3
    
    $service = Get-Service -Name $serviceName
    if ($service.Status -eq "Running") {
        Write-Log "Service started successfully." -Level "SUCCESS"
    } else {
        Write-Log "Failed to start service." -Level "ERROR"
        return $false
    }
    
    return $true
}

# Function to verify deployment
function Test-Deployment {
    Write-Log "Verifying deployment..."
    
    Start-Sleep -Seconds 5
    
    # Check service status
    $service = Get-Service -Name "MemoryDayBackend" -ErrorAction SilentlyContinue
    if ($service -and $service.Status -eq "Running") {
        Write-Log "Service is running." -Level "SUCCESS"
    } else {
        Write-Log "Service is not running." -Level "ERROR"
        return $false
    }
    
    # Test API endpoint
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Log "API health check passed." -Level "SUCCESS"
        } else {
            Write-Log "API health check failed." -Level "ERROR"
            return $false
        }
    } catch {
        Write-Log "API health check failed: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
    
    # Test COS configuration
    Set-Location $BackendDir
    $venvPath = "$BackendDir\venv"
    & "$venvPath\Scripts\python.exe" manage.py cos_status
    
    Write-Log "Deployment verification completed." -Level "SUCCESS"
    return $true
}

# Main deployment function
function Invoke-Deployment {
    Write-Log "Starting MemoryDay backend deployment..."
    
    if (-not (Test-Requirements)) {
        return
    }
    
    Initialize-ProjectDirectory
    Initialize-PythonEnvironment
    
    if (-not (Initialize-Environment)) {
        return
    }
    
    Initialize-Database
    Initialize-WindowsService
    
    if (Start-Services) {
        Test-Deployment
    }
    
    Write-Log "MemoryDay backend deployment completed!" -Level "SUCCESS"
    Write-Log "Access your application at: http://localhost:8000"
}

# Function to show usage
function Show-Usage {
    Write-Host "MemoryDay Backend Deployment Script for Windows"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [parameters]"
    Write-Host ""
    Write-Host "Parameters:"
    Write-Host "  -Action <string>    Action to perform (deploy, update, restart, status, logs)"
    Write-Host "  -ProjectDir <path>  Project directory (default: C:\MemoryDay)"
    Write-Host "  -Help               Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1 -Action deploy"
    Write-Host "  .\deploy.ps1 -Action update"
    Write-Host "  .\deploy.ps1 -Action status"
    Write-Host ""
}

# Main script execution
if ($Help) {
    Show-Usage
    exit 0
}

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Log "This script requires administrator privileges. Please run as Administrator." -Level "ERROR"
    exit 1
}

# Execute based on action
switch ($Action.ToLower()) {
    "deploy" {
        Invoke-Deployment
    }
    "update" {
        Write-Log "Updating existing deployment..."
        Initialize-ProjectDirectory
        Initialize-PythonEnvironment
        Initialize-Database
        Start-Services
        Test-Deployment
    }
    "restart" {
        Restart-Service -Name "MemoryDayBackend" -Force
        Write-Log "Service restarted." -Level "SUCCESS"
    }
    "status" {
        Get-Service -Name "MemoryDayBackend"
    }
    "logs" {
        if (Test-Path "$LogDir\service.log") {
            Get-Content "$LogDir\service.log" -Wait
        } else {
            Write-Log "Log file not found." -Level "ERROR"
        }
    }
    default {
        Write-Log "Unknown action: $Action" -Level "ERROR"
        Show-Usage
        exit 1
    }
}