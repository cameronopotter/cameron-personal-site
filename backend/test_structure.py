#!/usr/bin/env python3
"""
Test script to verify the backend structure and key components
"""

import os
import sys
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    backend_dir = Path(__file__).parent
    
    required_files = [
        "requirements.txt",
        "app/main.py",
        "app/core/config.py", 
        "app/core/database.py",
        "app/core/cache.py",
        "app/sample_data.py",
        "app/background_tasks.py",
        "run_dev.py",
        ".env.example"
    ]
    
    print("🔍 Checking file structure...")
    all_exist = True
    
    for file_path in required_files:
        full_path = backend_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False
    
    return all_exist

def test_requirements():
    """Test requirements.txt content"""
    print("\n🔍 Checking requirements.txt...")
    
    backend_dir = Path(__file__).parent
    req_file = backend_dir / "requirements.txt"
    
    if not req_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    content = req_file.read_text()
    
    # Check for minimal dependencies
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "aiosqlite",
        "pydantic",
    ]
    
    # Check for removed packages (should not be present)
    removed_packages = [
        "postgresql",
        "asyncpg", 
        "redis",
        "celery",
        "psycopg2"
    ]
    
    all_good = True
    
    for package in required_packages:
        if package.lower() in content.lower():
            print(f"✅ {package} found")
        else:
            print(f"❌ {package} missing")
            all_good = False
    
    for package in removed_packages:
        if package.lower() in content.lower():
            print(f"⚠️  {package} still present (should be removed)")
    
    return all_good

def test_configuration():
    """Test configuration setup"""
    print("\n🔍 Checking configuration...")
    
    backend_dir = Path(__file__).parent
    config_file = backend_dir / "app" / "core" / "config.py"
    
    if not config_file.exists():
        print("❌ config.py not found")
        return False
    
    content = config_file.read_text()
    
    checks = [
        ("sqlite", "SQLite database configuration"),
        ("aiosqlite", "Async SQLite driver"),
        ("in-memory", "In-memory caching"),
    ]
    
    all_good = True
    for check, description in checks:
        if check.lower() in content.lower():
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - not found")
            all_good = False
    
    # Check that Redis/PostgreSQL aren't mentioned
    deprecated = [
        ("redis://", "Redis URLs should be removed"),
        ("postgresql://", "PostgreSQL URLs should be removed"),
    ]
    
    for check, description in deprecated:
        if check.lower() in content.lower():
            print(f"⚠️  {description}")
    
    return all_good

def test_sample_data():
    """Test sample data system"""
    print("\n🔍 Checking sample data system...")
    
    backend_dir = Path(__file__).parent
    sample_file = backend_dir / "app" / "sample_data.py"
    
    if not sample_file.exists():
        print("❌ sample_data.py not found")
        return False
    
    content = sample_file.read_text()
    
    checks = [
        ("sample_projects", "Sample projects data"),
        ("sample_skills", "Sample skills data"), 
        ("Digital Greenhouse", "Main project included"),
        ("growth_stage", "Growth stages defined"),
        ("init_sample_data", "Initialization function"),
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"✅ {description}")
        else:
            print(f"❌ {description} - not found")
            all_good = False
    
    return all_good

def main():
    """Run all tests"""
    print("🌱 Digital Greenhouse Backend Structure Test")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Requirements", test_requirements), 
        ("Configuration", test_configuration),
        ("Sample Data", test_sample_data),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print(f"\n🎉 All tests passed! The backend structure is ready.")
        print(f"📝 Next steps:")
        print(f"   1. Install dependencies: pip install -r requirements.txt")
        print(f"   2. Run the server: python run_dev.py")
        print(f"   3. Visit http://localhost:8000/docs for API documentation")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())