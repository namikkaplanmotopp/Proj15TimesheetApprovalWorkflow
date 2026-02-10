#!/usr/bin/env python3
"""
Simple smoke test to verify the timesheet-api structure is correct.
This does NOT require dependencies to be installed.
"""

import os
import sys

def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} - MISSING")
        return False

def main():
    print("=" * 60)
    print("Timesheet API - Structure Verification")
    print("=" * 60)
    print()
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    all_ok = True
    
    # Core files
    print("Core Files:")
    all_ok &= check_file_exists("main.py")
    all_ok &= check_file_exists("schemas.py")
    all_ok &= check_file_exists("enums.py")
    all_ok &= check_file_exists("requirements.txt")
    all_ok &= check_file_exists("README.md")
    all_ok &= check_file_exists(".gitignore")
    print()
    
    # Database
    print("Database Module:")
    all_ok &= check_file_exists("db/__init__.py")
    all_ok &= check_file_exists("db/database.py")
    all_ok &= check_file_exists("db/models.py")
    all_ok &= check_file_exists("db/db_user.py")
    all_ok &= check_file_exists("db/db_project.py")
    all_ok &= check_file_exists("db/db_timesheet_entry.py")
    print()
    
    # Auth
    print("Auth Module:")
    all_ok &= check_file_exists("auth/__init__.py")
    all_ok &= check_file_exists("auth/hash.py")
    all_ok &= check_file_exists("auth/oauth2.py")
    all_ok &= check_file_exists("auth/authentication.py")
    print()
    
    # Routers
    print("Router Module:")
    all_ok &= check_file_exists("router/__init__.py")
    all_ok &= check_file_exists("router/health.py")
    all_ok &= check_file_exists("router/user.py")
    all_ok &= check_file_exists("router/project.py")
    all_ok &= check_file_exists("router/timesheet_entry.py")
    all_ok &= check_file_exists("router/seed.py")
    print()
    
    # Tests
    print("Tests Module:")
    all_ok &= check_file_exists("tests/__init__.py")
    all_ok &= check_file_exists("tests/conftest.py")
    all_ok &= check_file_exists("tests/test_timesheet_entry.py")
    print()
    
    # User Story
    print("Assessment:")
    all_ok &= check_file_exists("PROJ-015_TIMESHEET_APPROVAL.md")
    print()
    
    # Syntax check
    print("=" * 60)
    print("Syntax Verification:")
    print("=" * 60)
    import py_compile
    
    files_to_check = [
        "main.py",
        "schemas.py",
        "enums.py",
        "db/models.py",
        "db/database.py",
        "auth/oauth2.py",
        "router/user.py",
    ]
    
    for filepath in files_to_check:
        try:
            py_compile.compile(filepath, doraise=True)
            print(f"✅ {filepath} - syntax OK")
        except py_compile.PyCompileError as e:
            print(f"❌ {filepath} - SYNTAX ERROR")
            print(f"   {e}")
            all_ok = False
    
    print()
    print("=" * 60)
    if all_ok:
        print("✅ ALL CHECKS PASSED")
        print()
        print("Next steps:")
        print("1. pip install -r requirements.txt")
        print("2. python main.py")
        print("3. Visit http://127.0.0.1:8000/docs")
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
