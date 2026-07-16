#!/bin/bash

# MemoryDay Backend Deployment Script
# This script automates the deployment process for traditional server environments

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_NAME="memoryday"
PROJECT_DIR="/opt/${PROJECT_NAME}"
BACKEND_DIR="${PROJECT_DIR}/backend"
VENV_DIR="${BACKEND_DIR}/venv"
LOG_DIR="/var/log/${PROJECT_NAME}"
SERVICE_NAME="${PROJECT_NAME}"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    log_error "This script should not be run as root. Use a regular user with sudo privileges."
    exit 1
fi

# Function to check system requirements
check_requirements() {
    log_info "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    # Check MySQL/PostgreSQL client
    if ! command -v mysql &> /dev/null && ! command -v psql &> /dev/null; then
        log_warning "Neither MySQL nor PostgreSQL client is installed. Database operations may fail."
    fi
    
    log_success "System requirements check passed."
}

# Function to setup project directory
setup_project_dir() {
    log_info "Setting up project directory..."
    
    # Create directories
    sudo mkdir -p "${PROJECT_DIR}" "${LOG_DIR}"
    sudo chown -R $(whoami):$(whoami) "${PROJECT_DIR}"
    sudo chown -R $(whoami):$(whoami) "${LOG_DIR}"
    
    # Clone or copy project files
    if [[ -d "${BACKEND_DIR}" ]]; then
        log_info "Project directory already exists. Updating..."
        cd "${BACKEND_DIR}"
        git pull origin main
    else
        log_info "Copying project files..."
        # Copy current directory to target (for testing)
        cp -r . "${BACKEND_DIR}"/ || {
            log_error "Failed to copy project files. Ensure you're running from the backend directory."
            exit 1
        }
    fi
    
    log_success "Project directory setup completed."
}

# Function to setup Python virtual environment
setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    cd "${BACKEND_DIR}"
    
    if [[ ! -d "${VENV_DIR}" ]]; then
        python3 -m venv "${VENV_DIR}"
        log_success "Virtual environment created."
    else
        log_info "Virtual environment already exists."
    fi
    
    # Activate venv and install dependencies
    source "${VENV_DIR}/bin/activate"
    pip install --upgrade pip
    pip install -r requirements.txt
    
    log_success "Python dependencies installed."
}

# Function to setup environment configuration
setup_environment() {
    log_info "Setting up environment configuration..."
    
    cd "${BACKEND_DIR}"
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            cp .env.example .env
            log_warning "Please edit .env file with your actual configuration before continuing."
            read -p "Press Enter to continue after editing .env file..."
        else
            log_error ".env.example file not found. Please create a .env file manually."
            exit 1
        fi
    else
        log_info ".env file already exists."
    fi
    
    log_success "Environment configuration setup completed."
}

# Function to setup database
setup_database() {
    log_info "Setting up database..."
    
    cd "${BACKEND_DIR}"
    source "${VENV_DIR}/bin/activate"
    
    # Run migrations
    python manage.py makemigrations
    python manage.py migrate
    
    # Create superuser if needed
    read -p "Do you want to create a superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python manage.py createsuperuser
    fi
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    log_success "Database setup completed."
}

# Function to setup systemd service
setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    # Create systemd service file
    sudo tee "/etc/systemd/system/${SERVICE_NAME}.service" > /dev/null <<EOF
[Unit]
Description=MemoryDay Django Application
After=network.target

[Service]
Type=simple
User=$(whoami)
Group=$(whoami)
WorkingDirectory=${BACKEND_DIR}
ExecStart=${VENV_DIR}/bin/gunicorn memoryday_backend.wsgi:application -c gunicorn.conf.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure
RestartSec=5s

# Security
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=${BACKEND_DIR} ${LOG_DIR}

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${SERVICE_NAME}

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}.service"
    
    log_success "Systemd service setup completed."
}

# Function to start services
start_services() {
    log_info "Starting services..."
    
    sudo systemctl start "${SERVICE_NAME}.service"
    sudo systemctl status "${SERVICE_NAME}.service" --no-pager
    
    log_success "Services started successfully."
}

# Function to verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Wait a bit for service to start
    sleep 5
    
    # Check service status
    if systemctl is-active --quiet "${SERVICE_NAME}.service"; then
        log_success "Service is running."
    else
        log_error "Service is not running. Check logs with: sudo journalctl -u ${SERVICE_NAME}.service"
        exit 1
    fi
    
    # Test API endpoint
    if curl -f http://localhost:8000/api/health/ > /dev/null 2>&1; then
        log_success "API health check passed."
    else
        log_error "API health check failed."
        exit 1
    fi
    
    # Test COS configuration
    cd "${BACKEND_DIR}"
    source "${VENV_DIR}/bin/activate"
    python manage.py cos_status
    
    log_success "Deployment verification completed."
}

# Main deployment function
deploy() {
    log_info "Starting MemoryDay backend deployment..."
    
    check_requirements
    setup_project_dir
    setup_venv
    setup_environment
    setup_database
    setup_systemd_service
    start_services
    verify_deployment
    
    log_success "MemoryDay backend deployment completed successfully!"
    log_info "Access your application at: http://your-server-ip:8000"
    log_info "View logs with: sudo journalctl -u ${SERVICE_NAME}.service -f"
}

# Function to show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy       Full deployment (default)"
    echo "  update       Update existing deployment"
    echo "  restart      Restart services"
    echo "  status       Show service status"
    echo "  logs         Show service logs"
    echo "  help         Show this help message"
    echo ""
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "update")
        log_info "Updating existing deployment..."
        setup_project_dir
        setup_venv
        setup_database
        start_services
        verify_deployment
        ;;
    "restart")
        sudo systemctl restart "${SERVICE_NAME}.service"
        log_success "Service restarted."
        ;;
    "status")
        sudo systemctl status "${SERVICE_NAME}.service" --no-pager
        ;;
    "logs")
        sudo journalctl -u "${SERVICE_NAME}.service" -f
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        log_error "Unknown command: $1"
        usage
        exit 1
        ;;
esac