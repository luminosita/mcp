"""
Example unit tests demonstrating fixture usage patterns.

These tests serve as examples for developers and validate conftest.py fixtures.
"""

from unittest.mock import Mock

import pytest

# ====================
# Sample Data Fixture Examples
# ====================


@pytest.mark.unit
def test_should_use_sample_user_data_fixture(sample_user_data):
    """Test demonstrating sample_user_data fixture usage."""
    # Arrange - fixture provides sample data
    assert "email" in sample_user_data
    assert "username" in sample_user_data

    # Act - modify data for test case
    sample_user_data["email"] = "modified@example.com"

    # Assert - verify modifications
    assert sample_user_data["email"] == "modified@example.com"
    assert sample_user_data["username"] == "testuser"


@pytest.mark.unit
def test_should_use_sample_tool_request_fixture(sample_tool_request):
    """Test demonstrating sample_tool_request fixture usage."""
    # Arrange
    assert sample_tool_request["tool_name"] == "search_jira"

    # Act
    parameters = sample_tool_request["parameters"]

    # Assert
    assert "query" in parameters
    assert parameters["max_results"] == 10


@pytest.mark.unit
def test_should_use_sample_tool_response_fixture(sample_tool_response):
    """Test demonstrating sample_tool_response fixture usage."""
    # Arrange
    assert sample_tool_response["status"] == "success"

    # Act
    result = sample_tool_response["result"]

    # Assert
    assert "issues" in result
    assert len(result["issues"]) == 2
    assert result["issues"][0]["key"] == "TEST-1"


# ====================
# Factory Fixture Examples
# ====================


@pytest.mark.unit
def test_should_create_multiple_users_with_factory(user_factory):
    """Test demonstrating user_factory fixture usage."""
    # Arrange & Act - create multiple users with different data
    user1 = user_factory(id=1, email="user1@example.com", username="user1")
    user2 = user_factory(id=2, email="user2@example.com", username="user2")
    user3 = user_factory(id=3, email="user3@example.com", username="user3")

    # Assert - verify each user has unique data
    assert user1["id"] != user2["id"] != user3["id"]
    assert user1["email"] != user2["email"] != user3["email"]
    assert user1["username"] != user2["username"] != user3["username"]


@pytest.mark.unit
def test_should_use_factory_with_defaults(user_factory):
    """Test demonstrating user_factory default values."""
    # Arrange & Act - create user with defaults
    user = user_factory()

    # Assert - verify default values
    assert user["id"] == 1
    assert user["email"] == "test@example.com"
    assert user["username"] == "testuser"
    assert user["is_active"] is True


@pytest.mark.unit
def test_should_use_factory_with_partial_overrides(user_factory):
    """Test demonstrating user_factory with partial parameter overrides."""
    # Arrange & Act - override only specific fields
    user = user_factory(email="custom@example.com", full_name="Custom User")

    # Assert - verify overrides applied, defaults preserved
    assert user["email"] == "custom@example.com"
    assert user["full_name"] == "Custom User"
    assert user["id"] == 1  # default
    assert user["username"] == "testuser"  # default


# ====================
# Mock Service Fixture Examples
# ====================


@pytest.mark.unit
def test_should_use_mock_http_client_fixture(mock_http_client):
    """Test demonstrating mock_http_client fixture usage."""
    # Arrange - configure mock response
    mock_http_client.get.return_value.json.return_value = {"data": "test_value"}
    mock_http_client.get.return_value.status_code = 200

    # Act - simulate HTTP call
    response = mock_http_client.get("https://api.example.com/data")

    # Assert - verify mock behavior
    assert response.status_code == 200
    assert response.json() == {"data": "test_value"}
    mock_http_client.get.assert_called_once_with("https://api.example.com/data")


@pytest.mark.unit
def test_should_use_mock_jira_client_fixture(mock_jira_client):
    """Test demonstrating mock_jira_client fixture usage."""
    # Arrange - mock_jira_client comes pre-configured with common methods
    assert mock_jira_client.create_issue is not None
    assert mock_jira_client.get_issue is not None

    # Act - call pre-configured mocked method
    issue = mock_jira_client.create_issue(fields={"summary": "Test issue"})

    # Assert - verify pre-configured return value
    assert issue["id"] == "PROJ-123"
    assert issue["key"] == "PROJ-123"
    mock_jira_client.create_issue.assert_called_once()


@pytest.mark.unit
def test_should_use_mock_ci_cd_client_fixture(mock_ci_cd_client):
    """Test demonstrating mock_ci_cd_client fixture usage."""
    # Arrange - mock_ci_cd_client comes pre-configured
    assert mock_ci_cd_client.trigger_workflow is not None

    # Act - trigger workflow
    run = mock_ci_cd_client.trigger_workflow(workflow_id="ci.yml", ref="main")

    # Assert - verify pre-configured return value
    assert run["run_id"] == 123
    mock_ci_cd_client.trigger_workflow.assert_called_once_with(workflow_id="ci.yml", ref="main")


@pytest.mark.unit
def test_should_customize_mock_jira_client_response(mock_jira_client):
    """Test demonstrating how to customize pre-configured mock responses."""
    # Arrange - override default mock response
    custom_issue = {"id": "CUSTOM-456", "key": "CUSTOM-456", "fields": {"summary": "Custom"}}
    mock_jira_client.create_issue.return_value = custom_issue

    # Act - call with custom response
    issue = mock_jira_client.create_issue(fields={"summary": "Custom issue"})

    # Assert - verify custom response
    assert issue["id"] == "CUSTOM-456"
    assert issue["key"] == "CUSTOM-456"


# ====================
# Database Mock Fixture Examples
# ====================


@pytest.mark.unit
def test_should_use_db_session_fixture(db_session):
    """Test demonstrating db_session fixture usage."""
    # Arrange - configure mock database query chain
    mock_user = {"id": 1, "email": "user@example.com"}
    db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Act - simulate database query
    result = db_session.query(Mock).filter(Mock).first()

    # Assert - verify query executed and result matches
    assert result == mock_user
    assert result["email"] == "user@example.com"


# ====================
# Parametrized Test Examples
# ====================


@pytest.mark.unit
@pytest.mark.parametrize(
    "user_id,expected_active",
    [
        (1, True),  # Active user
        (2, False),  # Inactive user
        (3, True),  # Another active user
    ],
)
def test_should_create_users_with_different_active_status(user_factory, user_id, expected_active):
    """Test demonstrating parametrized tests with factory fixture."""
    # Arrange & Act
    user = user_factory(id=user_id, is_active=expected_active)

    # Assert
    assert user["id"] == user_id
    assert user["is_active"] == expected_active


@pytest.mark.unit
@pytest.mark.parametrize(
    "email,expected_valid",
    [
        ("valid@example.com", True),
        ("another.valid@test.org", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("user@", False),
    ],
)
def test_should_validate_email_formats(user_factory, email, expected_valid):
    """Test demonstrating parametrized email validation."""
    # Arrange & Act
    user = user_factory(email=email)

    # Assert - simple validation (in real code, use email validator)
    has_at_symbol = "@" in user["email"]
    has_domain = "." in user["email"].split("@")[-1] if has_at_symbol else False

    if expected_valid:
        assert has_at_symbol and has_domain
    # Note: This is a simplified example; real tests would use actual validation logic
