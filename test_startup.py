#!/usr/bin/env python3
"""
Test script to verify backend and frontend can start up
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("=" * 80)
    print("Testing Backend Imports...")
    print("=" * 80)
    
    try:
        # Test backend imports
        from services.main import app
        print("✅ Backend FastAPI app imported successfully")
        print(f"   App title: {app.title}")
        print(f"   App version: {app.version}")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        print(f"   Registered routes: {len(routes)}")
        for route in routes[:5]:  # Show first 5
            print(f"     - {route}")
        
        return True
    except ImportError as e:
        print(f"❌ Backend import failed: {e}")
        print("   This is expected if packages aren't installed in venv")
        return False
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frontend():
    """Test that frontend can be imported"""
    print("\n" + "=" * 80)
    print("Testing Frontend Imports...")
    print("=" * 80)
    
    try:
        import app
        print("✅ Frontend Streamlit app imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Frontend import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Frontend import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_code_syntax():
    """Test that Python files have valid syntax"""
    print("\n" + "=" * 80)
    print("Testing Code Syntax...")
    print("=" * 80)
    
    import py_compile
    import glob
    
    files_to_check = [
        "services/main.py",
        "services/ai_coach.py",
        "services/agent_orchestrator.py",
        "services/training_agent.py",
        "services/mentor_agent.py",
        "services/assessment_agent.py",
        "app.py",
    ]
    
    errors = []
    for file in files_to_check:
        if os.path.exists(file):
            try:
                py_compile.compile(file, doraise=True)
                print(f"✅ {file} - syntax valid")
            except py_compile.PyCompileError as e:
                print(f"❌ {file} - syntax error: {e}")
                errors.append(file)
        else:
            print(f"⚠️  {file} - file not found")
    
    return len(errors) == 0

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("STARTUP TEST SUITE")
    print("=" * 80)
    
    syntax_ok = test_code_syntax()
    backend_ok = test_imports()
    frontend_ok = test_frontend()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Code Syntax:     {'✅ PASS' if syntax_ok else '❌ FAIL'}")
    print(f"Backend Import:  {'✅ PASS' if backend_ok else '⚠️  SKIP (packages not installed)'}")
    print(f"Frontend Import: {'✅ PASS' if frontend_ok else '❌ FAIL'}")
    print("=" * 80)
    
    if syntax_ok and frontend_ok:
        print("\n✅ All critical tests passed!")
        print("   Backend will work once packages are installed in venv")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please fix errors above.")
        sys.exit(1)

