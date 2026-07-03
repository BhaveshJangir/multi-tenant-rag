import pytest

pytestmark = pytest.mark.asyncio

async def test_create_tenant(client):
    response = await client.post("/api/v1/users/tenants?name=TestTenant")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestTenant"
    assert "id" in data
    return data["id"]

async def test_register_user(client):
    # First create a tenant
    tenant_resp = await client.post("/api/v1/users/tenants?name=TenantForUser")
    tenant_id = tenant_resp.json()["id"]

    # Register user
    user_data = {
        "email": "test@example.com",
        "password": "password123",
        "role": "Admin",
        "tenant_id": tenant_id
    }
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["role"] == "Admin"

async def test_login_user(client):
    # Create tenant
    tenant_resp = await client.post("/api/v1/users/tenants?name=TenantForLogin")
    tenant_id = tenant_resp.json()["id"]

    # Register user
    user_data = {
        "email": "login@example.com",
        "password": "password123",
        "role": "Employee",
        "tenant_id": tenant_id
    }
    await client.post("/api/v1/auth/register", json=user_data)

    # Login
    login_data = {
        "username": "login@example.com",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
