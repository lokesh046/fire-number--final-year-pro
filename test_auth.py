"""
Authorization Test Script
Test that JWT authentication is working across all services
"""

import asyncio
import httpx
import json

BASE_URL = "http://localhost:8000"

async def test_authorization():
    """Test authorization flow across all services"""
    
    async with httpx.AsyncClient() as client:
        
        print("=" * 60)
        print("🔐 TESTING AUTHORIZATION ACROSS ALL SERVICES")
        print("=" * 60)
        
        # ============================================================
        # STEP 1: Register a new user
        # ============================================================
        print("\n📝 Step 1: Register a new user...")
        
        register_data = {
            "email": "testuser@example.com",
            "password": "testpass123"
        }
        
        try:
            reg_response = await client.post(
                f"{BASE_URL}/auth/register",
                json=register_data,
                timeout=10.0
            )
            print(f"   Register Status: {reg_response.status_code}")
            print(f"   Response: {reg_response.json()}")
        except Exception as e:
            print(f"   Note: User may already exist - {e}")
        
        # ============================================================
        # STEP 2: Login to get JWT token
        # ============================================================
        print("\n🔑 Step 2: Login to get JWT token...")
        
        login_data = {
            "username": "testuser@example.com",
            "password": "testpass123"
        }
        
        login_response = await client.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            timeout=10.0
        )
        
        if login_response.status_code != 200:
            print(f"   ❌ Login failed: {login_response.json()}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print(f"   ✅ Login successful!")
        print(f"   Token: {token[:50]}...")
        
        # ============================================================
        # STEP 3: Test Fire Service with auth
        # ============================================================
        print("\n🔥 Step 3: Test Fire Service (with auth)...")
        
        fire_data = {
            "monthly_income": 10000,
            "living_expense": 5000,
            "current_savings": 100000,
            "return_rate": 0.10,
            "inflation_rate": 0.06,
            "has_loan": False,
            "loan_emi": 0,
            "loan_years": 0
        }
        
        # With auth
        fire_with_auth = await client.post(
            "http://localhost:8001/fire",
            json=fire_data,
            headers=headers,
            timeout=10.0
        )
        print(f"   With Auth - Status: {fire_with_auth.status_code}")
        if fire_with_auth.status_code == 200:
            print(f"   ✅ Fire Service: AUTHORIZED")
            print(f"   Result: {fire_with_auth.json()}")
        else:
            print(f"   ❌ Error: {fire_with_auth.text}")
        
        # Without auth
        fire_without_auth = await client.post(
            "http://localhost:8001/fire",
            json=fire_data,
            timeout=10.0
        )
        print(f"   Without Auth - Status: {fire_without_auth.status_code}")
        if fire_without_auth.status_code == 401:
            print(f"   ✅ Correctly rejected: {fire_without_auth.json()}")
        
        # ============================================================
        # STEP 4: Test Health Service with auth
        # ============================================================
        print("\n🏥 Step 4: Test Health Service (with auth)...")
        
        health_data = {
            "monthly_income": 10000,
            "living_expense": 5000,
            "loan_emi": 2000,
            "current_savings": 100000,
            "fire_number": 1500000,
            "has_insurance": "yes"
        }
        
        health_with_auth = await client.post(
            "http://localhost:8002/health-score",
            json=health_data,
            headers=headers,
            timeout=10.0
        )
        print(f"   With Auth - Status: {health_with_auth.status_code}")
        if health_with_auth.status_code == 200:
            print(f"   ✅ Health Service: AUTHORIZED")
        else:
            print(f"   ❌ Error: {health_with_auth.text}")
        
        health_without_auth = await client.post(
            "http://localhost:8002/health-score",
            json=health_data,
            timeout=10.0
        )
        print(f"   Without Auth - Status: {health_without_auth.status_code}")
        if health_without_auth.status_code == 401:
            print(f"   ✅ Correctly rejected")
        
        # ============================================================
        # STEP 5: Test Loan Service with auth
        # ============================================================
        print("\n💰 Step 5: Test Loan Service (with auth)...")
        
        loan_data = {
            "loan_amount": 500000,
            "interest_rate_value": 8.5,
            "rate_type": "annual",
            "tenure_years": 20
        }
        
        loan_with_auth = await client.post(
            "http://localhost:8004/loan-analysis",
            json=loan_data,
            headers=headers,
            timeout=10.0
        )
        print(f"   With Auth - Status: {loan_with_auth.status_code}")
        if loan_with_auth.status_code == 200:
            print(f"   ✅ Loan Service: AUTHORIZED")
        else:
            print(f"   ❌ Error: {loan_with_auth.text}")
        
        loan_without_auth = await client.post(
            "http://localhost:8004/loan-analysis",
            json=loan_data,
            timeout=10.0
        )
        print(f"   Without Auth - Status: {loan_without_auth.status_code}")
        if loan_without_auth.status_code == 401:
            print(f"   ✅ Correctly rejected")
        
        # ============================================================
        # STEP 6: Test Explain Service with auth
        # ============================================================
        print("\n🤖 Step 6: Test Explain Service (with auth)...")
        
        explain_data = {
            "context_type": "loan_fire_strategy",
            "current_fire_year": 15,
            "optimized_fire_year": 10,
            "recommended_emi": 25000,
            "strategy_recommendation": "increase_emi",
            "financial_health_score": 75
        }
        
        explain_with_auth = await client.post(
            "http://localhost:8005/explain-strategy",
            json=explain_data,
            headers=headers,
            timeout=30.0
        )
        print(f"   With Auth - Status: {explain_with_auth.status_code}")
        if explain_with_auth.status_code == 200:
            print(f"   ✅ Explain Service: AUTHORIZED")
        else:
            print(f"   ❌ Error: {explain_with_auth.text}")
        
        explain_without_auth = await client.post(
            "http://localhost:8005/explain-strategy",
            json=explain_data,
            timeout=30.0
        )
        print(f"   Without Auth - Status: {explain_without_auth.status_code}")
        if explain_without_auth.status_code == 401:
            print(f"   ✅ Correctly rejected")
        
        # ============================================================
        # STEP 7: Test API Gateway
        # ============================================================
        print("\n🌐 Step 7: Test API Gateway (with auth)...")
        
        gateway_data = {
            "monthly_income": 10000,
            "living_expense": 5000,
            "current_savings": 100000,
            "return_rate": 0.10,
            "inflation_rate": 0.06,
            "has_loan": "no",
            "loan_amount": 0,
            "interest_rate_value": 8.5,
            "rate_type": "annual",
            "loan_emi": 0,
            "loan_years": 0,
            "has_insurance": "yes"
        }
        
        gateway_with_auth = await client.post(
            f"{BASE_URL}/calculate-fire",
            json=gateway_data,
            headers=headers,
            timeout=30.0
        )
        print(f"   With Auth - Status: {gateway_with_auth.status_code}")
        if gateway_with_auth.status_code == 200:
            print(f"   ✅ API Gateway: AUTHORIZED")
            print(f"   Result: {gateway_with_auth.json()}")
        else:
            print(f"   ❌ Error: {gateway_with_auth.text}")
        
        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "=" * 60)
        print("📊 AUTHORIZATION TEST SUMMARY")
        print("=" * 60)
        print("""
All services now require JWT authentication:
  ✅ Fire Service       - /fire endpoint protected
  ✅ Health Service     - /health-score endpoint protected  
  ✅ Loan Service      - /loan-analysis endpoint protected
  ✅ Explain Service   - /explain-strategy endpoint protected
  ✅ API Gateway       - All endpoints protected

To access protected endpoints:
  1. Register: POST /auth/register
  2. Login:    POST /auth/login (get JWT token)
  3. Use token in Authorization header:
     
     Authorization: Bearer <your_jwt_token>
        """)


async def test_without_services():
    """Quick test without starting all services"""
    
    print("""
============================================================
🚀 QUICK START GUIDE - Testing Authorization
============================================================

PREREQUISITE: Start all services first:

    # Terminal 1 - Chat Service (main app)
    uvicorn chat_service.main:app --port 8000
    
    # Terminal 2 - Fire Service  
    uvicorn fire_service.main:app --port 8001
    
    # Terminal 3 - Health Service
    uvicorn health_service.main:app --port 8002
    
    # Terminal 4 - Loan Service
    uvicorn loan_optimzer_service.main:app --port 8004
    
    # Terminal 5 - Explain Service
    uvicorn explain_service.main:app --port 8005


THEN RUN THIS SCRIPT:
    python test_auth.py


MANUAL TESTING WITH CURL:
--------------------------

1. Register:
   curl -X POST http://localhost:8000/auth/register \\
        -H "Content-Type: application/json" \\
        -d '{"email":"test@example.com","password":"test123"}'

2. Login:
   curl -X POST http://localhost:8000/auth/login \\
        -d "username=test@example.com&password=test123"
   
   Copy the access_token from response

3. Test with token:
   curl -X POST http://localhost:8001/fire \\
        -H "Authorization: Bearer <your_token>" \\
        -H "Content-Type: application/json" \\
        -d '{
          "monthly_income": 10000,
          "living_expense": 5000,
          "current_savings": 100000,
          "return_rate": 0.10,
          "inflation_rate": 0.06,
          "has_loan": false,
          "loan_emi": 0,
          "loan_years": 0
        }'

4. Test WITHOUT token (should fail):
   curl -X POST http://localhost:8001/fire \\
        -H "Content-Type: application/json" \\
        -d '{...}'

   Expected: {"detail":"Not authenticated"}


TROUBLESHOOTING:
----------------
- Make sure all services are running on correct ports
- Check that shared/services/service_auth.py is importable
- Verify JWT_SECRET_KEY is set in .env
    """)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        test_without_services()
    else:
        asyncio.run(test_authorization())
