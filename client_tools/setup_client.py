#!/usr/bin/env python3
"""
Client Setup Script for TechGuides External Case Creation
Run this script on the client machine to install required dependencies.
"""

import subprocess
import sys
import os
import urllib.request
import zipfile
import platform

def install_package(package):
    """Install a Python package using pip."""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_package(package):
    """Check if a package is already installed."""
    try:
        __import__(package)
        print(f"✅ {package} is already installed")
        return True
    except ImportError:
        print(f"⚠️  {package} is not installed")
        return False

def download_edge_driver():
    """Download Edge WebDriver if not present."""
    driver_path = "msedgedriver.exe"
    
    if os.path.exists(driver_path):
        print(f"✅ Edge WebDriver already exists at {driver_path}")
        return True
    
    print("Downloading Edge WebDriver...")
    print("ℹ️  Auto-download not implemented. Please download manually:")
    print("   1. Go to: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
    print("   2. Download the version matching your Edge browser")
    print("   3. Extract msedgedriver.exe to this directory")
    print("   4. Re-run this setup script")
    
    return False

def test_selenium():
    """Test that Selenium works with Edge."""
    try:
        print("Testing Selenium with Edge...")
        from selenium import webdriver
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.edge.service import Service
        
        # Check for driver
        driver_path = "msedgedriver.exe"
        if not os.path.exists(driver_path):
            print("❌ msedgedriver.exe not found")
            return False
        
        # Test driver initialization (headless)
        edge_options = Options()
        edge_options.add_argument("--headless")
        edge_options.add_argument("--disable-gpu")
        edge_options.add_argument("--no-sandbox")
        
        service = Service(driver_path)
        driver = webdriver.Edge(service=service, options=edge_options)
        
        # Quick test
        driver.get("about:blank")
        driver.quit()
        
        print("✅ Selenium + Edge WebDriver test passed")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        return False

def check_client_tools():
    """Check that required client tools exist."""
    required_files = [
        "case_creator.py",
        "techguides_client_service.py",
        "simple_case_viewer.py"
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} missing")
            all_present = False
    
    return all_present

def main():
    """Main setup function."""
    print("TechGuides External Case Creation - Client Setup")
    print("=" * 55)
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print()
    
    # Step 1: Check Python packages
    print("Step 1: Checking Python packages...")
    packages = {
        'selenium': 'selenium',
        'requests': 'requests',
        'tkinter': 'tkinter',
        'PIL': 'pillow',
        'pystray': 'pystray'
    }
    
    packages_to_install = []
    for import_name, package_name in packages.items():
        if not check_package(import_name):
            packages_to_install.append(package_name)
    
    # Install missing packages
    if packages_to_install:
        print(f"\nInstalling missing packages: {', '.join(packages_to_install)}")
        for package in packages_to_install:
            install_package(package)
    else:
        print("✅ All required packages are installed")
    
    print()
    
    # Step 2: Check Edge WebDriver
    print("Step 2: Checking Edge WebDriver...")
    driver_ready = download_edge_driver()
    print()
    
    # Step 3: Check client tools files
    print("Step 3: Checking client tools files...")
    tools_ready = check_client_tools()
    print()
    
    # Step 4: Test Selenium if everything is ready
    if driver_ready and tools_ready:
        print("Step 4: Testing Selenium...")
        selenium_ready = test_selenium()
        print()
    else:
        selenium_ready = False
        print("Step 4: Skipping Selenium test (missing dependencies)")
        print()
    
    # Summary
    print("=" * 55)
    print("SETUP SUMMARY")
    print("=" * 55)
    
    all_ready = driver_ready and tools_ready and selenium_ready
    
    if all_ready:
        print("🎉 Setup completed successfully!")
        print("\nYour client machine is ready for external case creation.")
        print("\nNext steps:")
        print("1. Start the TechGuides Client Service")
        print("2. Connect to your TechGuides server")
        print("3. Go to Case Management and click 'Create External'")
    else:
        print("⚠️  Setup incomplete. Please resolve the following:")
        if not driver_ready:
            print("- Download and install Edge WebDriver")
        if not tools_ready:
            print("- Copy missing client tools files")
        if not selenium_ready:
            print("- Fix Selenium configuration issues")
        
        print("\nRefer to EXTERNAL_CASE_SETUP.md for detailed instructions.")

if __name__ == "__main__":
    main()
