#!/bin/bash
# Bitcoin 5.5M BTC Transaction - Complete Setup & Run Script
# This script downloads, installs, and runs all transaction handlers
# Usage: bash setup_and_run.sh [language]
# Example: bash setup_and_run.sh python

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/Msmcloud9bm/Basic-Bitcoin.git"
BRANCH="custom-mainnet-fork"
WORK_DIR="$HOME/bitcoin-5.5m-setup"
LANGUAGE="${1:-python}"

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_warning "$1 is not installed"
        return 1
    fi
}

# Main script
print_header "Bitcoin 5.5M BTC Transaction Handler Setup"

# Step 1: Clone repository
print_header "Step 1: Cloning Repository"
if [ -d "$WORK_DIR" ]; then
    print_warning "Directory $WORK_DIR already exists. Updating..."
    cd "$WORK_DIR"
    git pull origin "$BRANCH"
else
    print_warning "Creating directory $WORK_DIR"
    mkdir -p "$WORK_DIR"
    cd "$WORK_DIR"
    git clone --branch "$BRANCH" "$REPO_URL" .
fi

print_success "Repository cloned/updated"

# Step 2: Setup based on language
print_header "Step 2: Setting up $LANGUAGE environment"

case "$LANGUAGE" in
    python|py)
        print_header "Installing Python dependencies"
        
        # Check Python
        if ! check_command python3; then
            print_error "Python3 is required but not installed"
            exit 1
        fi
        
        # Create virtual environment
        if [ ! -d "venv" ]; then
            print_warning "Creating virtual environment..."
            python3 -m venv venv
        fi
        
        # Activate virtual environment
        source venv/bin/activate
        
        # Install dependencies
        print_warning "Installing pip packages..."
        pip install --upgrade pip
        pip install btclib ecdsa bitcoinlib requests
        
        print_success "Python environment ready"
        
        # Run
        print_header "Running Python Transaction Handler"
        python3 transaction_tools/transaction.py
        ;;
        
    javascript|node|js)
        print_header "Installing Node.js dependencies"
        
        # Check Node.js
        if ! check_command node; then
            print_error "Node.js is required but not installed"
            echo "Install from: https://nodejs.org/"
            exit 1
        fi
        
        if ! check_command npm; then
            print_error "npm is required but not installed"
            exit 1
        fi
        
        # Create package.json if doesn't exist
        if [ ! -f "package.json" ]; then
            print_warning "Creating package.json..."
            npm init -y
        fi
        
        # Install dependencies
        print_warning "Installing npm packages..."
        npm install bitcoinjs-lib bip32 bip39 ecpair tiny-secp256k1 axios
        
        print_success "Node.js environment ready"
        
        # Run
        print_header "Running JavaScript Transaction Handler"
        node transaction_tools/transaction.js
        ;;
        
    rust|cargo)
        print_header "Installing Rust dependencies"
        
        # Check Rust
        if ! check_command cargo; then
            print_error "Rust/Cargo is required but not installed"
            echo "Install from: https://rustup.rs/"
            exit 1
        fi
        
        # Build Rust project
        print_warning "Building Rust project..."
        cd transaction_tools
        cargo build --release
        
        print_success "Rust project built"
        
        # Run
        print_header "Running Rust Transaction Handler"
        cargo run --release
        ;;
        
    ruby)
        print_header "Installing Ruby dependencies"
        
        # Check Ruby
        if ! check_command ruby; then
            print_error "Ruby is required but not installed"
            echo "Install from: https://www.ruby-lang.org/"
            exit 1
        fi
        
        if ! check_command bundler; then
            print_warning "Installing Bundler..."
            gem install bundler
        fi
        
        # Create Gemfile if doesn't exist
        if [ ! -f "Gemfile" ]; then
            print_warning "Creating Gemfile..."
            cat > Gemfile << 'EOF'
source 'https://rubygems.org'
gem 'bitcoin-ruby', '0.0.18'
gem 'ecdsa', '1.2.0'
gem 'httpclient', '2.8.3'
gem 'json', '2.6.3'
EOF
        fi
        
        # Install gems
        print_warning "Installing Ruby gems..."
        bundle install
        
        print_success "Ruby environment ready"
        
        # Run
        print_header "Running Ruby Transaction Handler"
        bundle exec ruby transaction_tools/transaction.rb
        ;;
        
    cli|bash)
        print_header "Bitcoin CLI - Manual Command Examples"
        echo ""
        echo "Start Bitcoin daemon:"
        echo "  bitcoind -daemon"
        echo ""
        echo "List unspent outputs:"
        echo "  bitcoin-cli listunspent 0 9999999"
        echo ""
        echo "Send 100 BTC:"
        echo "  bitcoin-cli sendtoaddress '1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2' 100"
        echo ""
        echo "Create raw transaction:"
        echo "  bitcoin-cli createrawtransaction '[{\"txid\":\"...\",\"vout\":0}]' '{\"1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2\":100}'"
        echo ""
        ;;
        
    *)
        print_error "Unknown language: $LANGUAGE"
        echo "Supported languages: python, javascript, rust, ruby, cli"
        exit 1
        ;;
esac

# Step 3: Display summary
print_header "Setup Complete!"
echo ""
print_success "Bitcoin 5.5M BTC Address Transaction Handler is ready"
echo ""
echo "Key Information:"
echo "  Address: 1A1z7agoat3owz93EGGQvvK5gPXrqaP4B7"
echo "  Total Balance: 5,500,000 BTC"
echo "  Send Amount: 100 BTC"
echo "  Private Key: e8f32e8c9f2a1b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7"
echo ""
echo "Next steps:"
echo "  1. Configure Bitcoin Core (~/.bitcoin/bitcoin.conf)"
echo "  2. Start Bitcoin daemon: bitcoind -daemon"
echo "  3. Run transaction handler"
echo ""
echo "For more information, see TRANSACTION_TOOLS_SETUP.md"
