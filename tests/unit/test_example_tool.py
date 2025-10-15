"""
Unit tests for example_tool module demonstrating testing patterns.

This test module serves as living documentation for testing MCP tools. It demonstrates:
- Unit testing with mocked dependencies
- Pydantic validation testing (valid/invalid inputs, edge cases)
- Error handling testing (validation errors, business logic errors)
- Async testing patterns with pytest-asyncio
- AAA (Arrange-Act-Assert) test structure
- Descriptive test names following convention: test_should_behavior_when_condition

WHY COMPREHENSIVE TESTS:
These tests demonstrate all patterns developers need to write high-quality tests for
new MCP tools. Reference this file when implementing tests for new tools.
"""

from unittest.mock import Mock, PropertyMock

import pytest
from pydantic import ValidationError

from mcp_server.core.exceptions import BusinessLogicError
from mcp_server.tools.example_tool import (
    GreetingInput,
    GreetingOutput,
    GreetingStyle,
    generate_greeting,
)

# ====================
# Pydantic Validation Tests - Valid Inputs
# ====================


@pytest.mark.unit
def test_should_accept_valid_greeting_input_with_defaults(sample_greeting_input):
    """
    Test Pydantic accepts valid input with default style.

    WHY TEST THIS: Validates that basic input structure works and defaults are applied.
    PATTERN: Test happy path with minimal required fields.
    """
    # Arrange
    input_data = sample_greeting_input

    # Act
    params = GreetingInput(**input_data)

    # Assert
    assert params.name == "Alice"
    assert params.style == GreetingStyle.CASUAL
    assert params.message is None


@pytest.mark.unit
def test_should_accept_valid_greeting_input_with_custom_message(
    sample_greeting_input_with_message,
):
    """
    Test Pydantic accepts valid input with all optional fields.

    WHY TEST THIS: Validates that optional fields work correctly.
    PATTERN: Test happy path with all fields populated.
    """
    # Arrange
    input_data = sample_greeting_input_with_message

    # Act
    params = GreetingInput(**input_data)

    # Assert
    assert params.name == "Bob"
    assert params.style == GreetingStyle.FORMAL
    assert params.message == "Hope you have a wonderful day"


@pytest.mark.unit
@pytest.mark.parametrize(
    "style_value,expected_enum",
    [
        ("formal", GreetingStyle.FORMAL),
        ("casual", GreetingStyle.CASUAL),
        ("enthusiastic", GreetingStyle.ENTHUSIASTIC),
    ],
)
def test_should_accept_all_valid_greeting_styles(style_value, expected_enum):
    """
    Test Pydantic accepts all valid GreetingStyle enum values.

    WHY TEST THIS: Validates enum mapping works for all supported values.
    PATTERN: Use parametrize to test all valid enum values efficiently.
    """
    # Arrange
    input_data = {"name": "Alice", "style": style_value}

    # Act
    params = GreetingInput(**input_data)

    # Assert
    assert params.style == expected_enum


@pytest.mark.unit
def test_should_accept_name_with_hyphens_and_spaces():
    """
    Test Pydantic accepts names with valid characters (letters, spaces, hyphens).

    WHY TEST THIS: Validates custom validator allows expected character set.
    PATTERN: Test edge case with all allowed special characters.
    """
    # Arrange
    input_data = {"name": "Mary-Jane Smith", "style": "casual"}

    # Act
    params = GreetingInput(**input_data)

    # Assert
    assert params.name == "Mary-Jane Smith"


# ====================
# Pydantic Validation Tests - Invalid Inputs
# ====================


@pytest.mark.unit
def test_should_reject_empty_name():
    """
    Test Pydantic rejects empty name string.

    WHY TEST THIS: Validates min_length constraint enforced.
    PATTERN: Test constraint violation raises ValidationError with specific message.
    """
    # Arrange
    input_data = {"name": "", "style": "casual"}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GreetingInput(**input_data)

    # Verify error message mentions the validation failure
    assert "String should have at least 1 character" in str(exc_info.value)


@pytest.mark.unit
def test_should_reject_name_exceeding_max_length():
    """
    Test Pydantic rejects name exceeding max_length constraint.

    WHY TEST THIS: Validates max_length constraint enforced.
    PATTERN: Test boundary violation with oversized input.
    """
    # Arrange
    long_name = "A" * 101  # Max is 100
    input_data = {"name": long_name, "style": "casual"}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GreetingInput(**input_data)

    # Verify error message mentions length constraint
    assert "String should have at most 100 characters" in str(exc_info.value)


@pytest.mark.unit
def test_should_reject_name_with_invalid_characters():
    """
    Test Pydantic rejects name containing invalid characters (numbers, symbols).

    WHY TEST THIS: Validates custom validator enforces character set restriction.
    PATTERN: Test custom validator with invalid input.
    """
    # Arrange
    input_data = {"name": "Alice123!", "style": "casual"}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GreetingInput(**input_data)

    # Verify error message mentions character restriction
    assert "Name must contain only letters, spaces, and hyphens" in str(exc_info.value)


@pytest.mark.unit
def test_should_reject_invalid_greeting_style():
    """
    Test Pydantic rejects invalid GreetingStyle enum value.

    WHY TEST THIS: Validates enum constraint enforced.
    PATTERN: Test enum validation with invalid value.
    """
    # Arrange
    input_data = {"name": "Alice", "style": "invalid_style"}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GreetingInput(**input_data)

    # Verify error message mentions enum constraint
    error_msg = str(exc_info.value)
    assert "Input should be 'formal', 'casual' or 'enthusiastic'" in error_msg


@pytest.mark.unit
def test_should_reject_message_exceeding_max_length():
    """
    Test Pydantic rejects message exceeding max_length constraint.

    WHY TEST THIS: Validates max_length constraint on optional field.
    PATTERN: Test constraint on optional field when provided.
    """
    # Arrange
    long_message = "A" * 501  # Max is 500
    input_data = {"name": "Alice", "style": "casual", "message": long_message}

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        GreetingInput(**input_data)

    # Verify error message mentions length constraint
    assert "String should have at most 500 characters" in str(exc_info.value)


@pytest.mark.unit
def test_should_strip_whitespace_from_name():
    """
    Test custom validator strips leading/trailing whitespace from name.

    WHY TEST THIS: Validates custom validator normalization behavior.
    PATTERN: Test that validator transforms input as expected.
    """
    # Arrange
    input_data = {"name": "  Alice  ", "style": "casual"}

    # Act
    params = GreetingInput(**input_data)

    # Assert - whitespace should be stripped
    assert params.name == "Alice"


# ====================
# Unit Tests - Business Logic with Mocked Dependencies
# ====================


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_generate_casual_greeting_successfully(
    sample_greeting_input, mock_settings, mock_logger
):
    """
    Test generate_greeting creates casual greeting with mocked dependencies.

    WHY TEST THIS: Validates core business logic works correctly with casual style.
    PATTERN: AAA structure with mocked dependencies for isolation.
    WHY ASYNC: Tool function is async, so test must be async with @pytest.mark.asyncio.
    """
    # Arrange
    params = GreetingInput(**sample_greeting_input)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert isinstance(result, GreetingOutput)
    assert result.greeting == "Hey, Alice!"
    assert result.style_used == "casual"
    assert result.character_count == len("Hey, Alice!")
    assert result.metadata["app_name"] == "TestApp"
    assert result.metadata["app_version"] == "1.0.0"
    assert result.metadata["style"] == "casual"

    # Verify logging occurred
    mock_logger.info.assert_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_generate_formal_greeting_successfully(mock_settings, mock_logger):
    """
    Test generate_greeting creates formal greeting.

    WHY TEST THIS: Validates different greeting style produces different output.
    PATTERN: Test variation in business logic based on input parameter.
    """
    # Arrange
    params = GreetingInput(name="Robert", style=GreetingStyle.FORMAL)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert result.greeting == "Good day, Robert!"
    assert result.style_used == "formal"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_generate_enthusiastic_greeting_successfully(mock_settings, mock_logger):
    """
    Test generate_greeting creates enthusiastic greeting.

    WHY TEST THIS: Validates all greeting styles work correctly.
    PATTERN: Test all branches in business logic.
    """
    # Arrange
    params = GreetingInput(name="Emma", style=GreetingStyle.ENTHUSIASTIC)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert result.greeting == "Hello there, Emma!"
    assert result.style_used == "enthusiastic"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_append_custom_message_when_provided(
    sample_greeting_input_with_message, mock_settings, mock_logger
):
    """
    Test generate_greeting appends custom message to greeting.

    WHY TEST THIS: Validates optional message parameter functionality.
    PATTERN: Test conditional logic (message present vs absent).
    """
    # Arrange
    params = GreetingInput(**sample_greeting_input_with_message)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert "Hope you have a wonderful day" in result.greeting
    assert result.greeting == "Good day, Bob! Hope you have a wonderful day"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_include_settings_in_metadata(
    sample_greeting_input, mock_settings, mock_logger
):
    """
    Test generate_greeting includes settings data in response metadata.

    WHY TEST THIS: Validates dependency injection works correctly.
    PATTERN: Verify injected dependencies used in business logic.
    """
    # Arrange
    params = GreetingInput(**sample_greeting_input)
    mock_settings.app_name = "CustomApp"
    mock_settings.app_version = "2.3.4"

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert - metadata should reflect injected settings
    assert result.metadata["app_name"] == "CustomApp"
    assert result.metadata["app_version"] == "2.3.4"


# ====================
# Error Handling Tests - Business Logic Errors
# ====================


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_raise_business_error_when_greeting_exceeds_max_length(
    mock_settings, mock_logger
):
    """
    Test generate_greeting raises BusinessLogicError when greeting exceeds max length.

    WHY TEST THIS: Validates business rule enforcement (max greeting length).
    PATTERN: Test error path with expected exception and error details.
    """
    # Arrange - create input that will exceed max length (600 chars)
    # "Hey, <long_name>! <message>" needs to exceed 600 chars
    # Greeting prefix "Hey, " = 5, name 100, "! " = 2, message needs to be > 493
    long_name = "A" * 100  # Max name length
    long_message = "A" * 494  # This will make total > 600
    params = GreetingInput(name=long_name, style=GreetingStyle.CASUAL, message=long_message)

    # Act & Assert
    with pytest.raises(BusinessLogicError) as exc_info:
        await generate_greeting(params, mock_settings, mock_logger)

    # Verify error details
    error = exc_info.value
    assert "exceeds maximum length" in str(error)
    assert error.details["name"] == long_name

    # Verify error logging occurred
    mock_logger.error.assert_called()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_log_info_on_successful_greeting_generation(
    sample_greeting_input, mock_settings, mock_logger
):
    """
    Test generate_greeting logs info messages during successful execution.

    WHY TEST THIS: Validates logging behavior for observability.
    PATTERN: Verify logging calls made with expected messages.
    """
    # Arrange
    params = GreetingInput(**sample_greeting_input)

    # Act
    await generate_greeting(params, mock_settings, mock_logger)

    # Assert - verify logging calls made
    assert mock_logger.info.call_count == 2  # One at start, one at end
    call_args_list = mock_logger.info.call_args_list

    # Verify first log contains input parameters
    first_log = str(call_args_list[0])
    assert "name=Alice" in first_log
    assert "style=casual" in first_log

    # Verify second log contains success message
    second_log = str(call_args_list[1])
    assert "Greeting generated successfully" in second_log


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_log_error_on_business_logic_failure(mock_settings, mock_logger):
    """
    Test generate_greeting logs error message on business logic failure.

    WHY TEST THIS: Validates error logging for troubleshooting.
    PATTERN: Verify error logging occurs when exception raised.
    """
    # Arrange - setup to trigger business error (greeting exceeds max length)
    long_name = "A" * 100
    long_message = "A" * 494
    params = GreetingInput(name=long_name, style=GreetingStyle.CASUAL, message=long_message)

    # Act
    with pytest.raises(BusinessLogicError):
        await generate_greeting(params, mock_settings, mock_logger)

    # Assert - verify error logging occurred
    mock_logger.error.assert_called_once()
    error_log = str(mock_logger.error.call_args)
    assert "Business logic error" in error_log


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_wrap_unexpected_exceptions_in_business_logic_error(
    sample_greeting_input, mock_logger
):
    """
    Test generate_greeting wraps unexpected exceptions in BusinessLogicError.

    WHY TEST THIS: Validates error handling for unexpected failures.
    PATTERN: Test exception wrapping for unknown errors.
    """
    # Arrange
    params = GreetingInput(**sample_greeting_input)
    # Mock settings that will cause an exception when accessed for app_name
    mock_settings = Mock()
    # Setting app_name and app_version as properties that will raise exceptions
    type(mock_settings).app_name = PropertyMock(side_effect=RuntimeError("Settings error"))
    type(mock_settings).app_version = PropertyMock(side_effect=RuntimeError("Settings error"))

    # Act & Assert
    with pytest.raises(BusinessLogicError) as exc_info:
        await generate_greeting(params, mock_settings, mock_logger)

    # Verify error was wrapped
    error = exc_info.value
    assert "Failed to generate greeting due to unexpected error" in str(error)
    # The error details will contain information about the underlying exception
    assert "error" in error.details

    # Verify exception logging occurred
    mock_logger.exception.assert_called_once()


# ====================
# Edge Case Tests
# ====================


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_accept_name_with_hyphens_and_spaces_with_letters(mock_settings, mock_logger):
    """
    Test generate_greeting accepts name with hyphens, spaces, and letters.

    WHY TEST THIS: Validates custom validator accepts valid mixed input.
    PATTERN: Test that validator allows all valid character combinations.
    """
    # Arrange - name with letters, spaces, and hyphens (all valid)
    params = GreetingInput(name="Mary - Jane Smith", style=GreetingStyle.CASUAL)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert "Mary - Jane Smith" in result.greeting
    assert result.character_count > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_handle_single_character_name(mock_settings, mock_logger):
    """
    Test generate_greeting handles minimum length name (1 character).

    WHY TEST THIS: Validates boundary condition (min_length=1).
    PATTERN: Test boundary value at minimum constraint.
    """
    # Arrange
    params = GreetingInput(name="A", style=GreetingStyle.CASUAL)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert result.greeting == "Hey, A!"
    assert result.character_count == len("Hey, A!")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_handle_maximum_length_name(mock_settings, mock_logger):
    """
    Test generate_greeting handles maximum length name (100 characters).

    WHY TEST THIS: Validates boundary condition (max_length=100).
    PATTERN: Test boundary value at maximum constraint.
    """
    # Arrange
    max_name = "A" * 100  # Exactly at max length
    params = GreetingInput(name=max_name, style=GreetingStyle.CASUAL)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert
    assert max_name in result.greeting
    assert result.character_count > 100  # Greeting is longer than just name


# ====================
# Output Model Tests
# ====================


@pytest.mark.asyncio
@pytest.mark.unit
async def test_should_return_greeting_output_with_all_fields(
    sample_greeting_input, mock_settings, mock_logger
):
    """
    Test generate_greeting returns GreetingOutput with all required fields.

    WHY TEST THIS: Validates output model structure matches contract.
    PATTERN: Verify output model completeness and types.
    """
    # Arrange
    params = GreetingInput(**sample_greeting_input)

    # Act
    result = await generate_greeting(params, mock_settings, mock_logger)

    # Assert - verify all fields present and correct types
    assert isinstance(result, GreetingOutput)
    assert isinstance(result.greeting, str)
    assert isinstance(result.style_used, str)
    assert isinstance(result.character_count, int)
    assert isinstance(result.metadata, dict)

    # Verify metadata structure
    assert "app_name" in result.metadata
    assert "app_version" in result.metadata
    assert "style" in result.metadata


@pytest.mark.unit
def test_should_create_greeting_output_with_valid_data():
    """
    Test GreetingOutput model accepts valid data.

    WHY TEST THIS: Validates output model validation works.
    PATTERN: Test output model independently from business logic.
    """
    # Arrange
    output_data = {
        "greeting": "Hey, Alice!",
        "style_used": "casual",
        "character_count": 12,
        "metadata": {"app_name": "TestApp", "app_version": "1.0.0", "style": "casual"},
    }

    # Act
    output = GreetingOutput(**output_data)

    # Assert
    assert output.greeting == "Hey, Alice!"
    assert output.style_used == "casual"
    assert output.character_count == 12
    assert output.metadata["app_name"] == "TestApp"


# ====================
# Enum Tests
# ====================


@pytest.mark.unit
def test_should_have_all_greeting_styles_defined():
    """
    Test GreetingStyle enum has all expected values.

    WHY TEST THIS: Validates enum definition completeness.
    PATTERN: Test enum structure to catch accidental modifications.
    """
    # Assert - verify all expected styles exist
    assert hasattr(GreetingStyle, "FORMAL")
    assert hasattr(GreetingStyle, "CASUAL")
    assert hasattr(GreetingStyle, "ENTHUSIASTIC")

    # Verify enum values are correct strings
    assert GreetingStyle.FORMAL.value == "formal"
    assert GreetingStyle.CASUAL.value == "casual"
    assert GreetingStyle.ENTHUSIASTIC.value == "enthusiastic"


@pytest.mark.unit
def test_should_compare_greeting_styles_correctly():
    """
    Test GreetingStyle enum values compare correctly.

    WHY TEST THIS: Validates enum comparison behavior.
    PATTERN: Test enum equality and string comparison.
    """
    # Assert - enum comparison
    assert GreetingStyle.FORMAL == GreetingStyle.FORMAL
    assert GreetingStyle.FORMAL != GreetingStyle.CASUAL

    # Assert - string value comparison
    assert GreetingStyle.FORMAL.value == "formal"
    assert GreetingStyle.CASUAL.value == "casual"
