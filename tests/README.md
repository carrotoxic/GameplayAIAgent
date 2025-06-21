# GameplayAIAgent Tests

This directory contains comprehensive tests for the GameplayAIAgent project.

## Test Structure

```
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── unit/                    # Unit tests for individual components
│   ├── test_curriculum_service.py
│   ├── test_critic_service.py
│   ├── test_planner_service.py
│   ├── test_models.py
│   └── test_exceptions.py
└── integration/             # Integration tests for workflows
    └── test_agent_workflow.py
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run unit tests only
```bash
pytest tests/unit/
```

### Run integration tests only
```bash
pytest tests/integration/
```

### Run with coverage
```bash
pytest --cov=domain --cov=adapters --cov=interface
```

### Run specific test file
```bash
pytest tests/unit/test_curriculum_service.py
```

### Run specific test function
```bash
pytest tests/unit/test_curriculum_service.py::TestCurriculumService::test_init
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Service Tests**: Test individual domain services (Curriculum, Critic, Planner)
- **Model Tests**: Test domain models and data structures
- **Exception Tests**: Test custom exception handling

### Integration Tests (`tests/integration/`)
- **Workflow Tests**: Test complete agent workflows
- **Component Interaction**: Test how different components work together
- **Error Handling**: Test error scenarios across the system

## Test Fixtures

Common test fixtures are defined in `conftest.py`:

- **Mock Objects**: LLM, parser, prompt builder, etc.
- **Sample Data**: Events, beliefs, desires, contexts, etc.
- **Configuration**: Warmup thresholds, test settings

## Test Coverage

The test suite aims for:
- **80%+ code coverage** for all modules
- **100% coverage** of critical paths
- **Comprehensive error handling** testing
- **Edge case** coverage

## Writing New Tests

### Unit Test Template
```python
import pytest
from unittest.mock import Mock
from domain.services.your_service import YourService

class TestYourService:
    def test_your_method(self, mock_dependency):
        """Test description"""
        # Setup
        service = YourService(mock_dependency)
        
        # Execute
        result = service.your_method()
        
        # Assert
        assert result == expected_value
```

### Integration Test Template
```python
import pytest
from domain.services.service1 import Service1
from domain.services.service2 import Service2

class TestServiceIntegration:
    def test_service_interaction(self, mock_llm, mock_parser):
        """Test how services work together"""
        # Setup multiple services
        service1 = Service1(mock_llm)
        service2 = Service2(mock_parser)
        
        # Execute workflow
        result = service1.process(service2.get_data())
        
        # Assert workflow result
        assert result.success is True
```

## Best Practices

1. **Use descriptive test names** that explain what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies** to isolate units under test
4. **Test both success and failure scenarios**
5. **Use fixtures for common setup**
6. **Keep tests independent** - no test should depend on another
7. **Test edge cases and error conditions**

## Continuous Integration

Tests are automatically run on:
- Pull requests
- Main branch commits
- Release tags

The CI pipeline ensures:
- All tests pass
- Coverage thresholds are met
- Code quality checks pass 