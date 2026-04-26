# Automated Testing and Coverage Guide for Sprint 3

## Overview
This document explains how to run automated tests for BetaTrax, measure code coverage, and verify the developer effectiveness metrics implementation.

## Project Structure

### Test Files Created
- `defects/tests.py` - Main API tests and developer effectiveness metric tests
- `defects/metrics.py` - Developer effectiveness metric calculation logic
- `comments/tests.py` - Comment API tests
- `Resolving/tests.py` - Resolving/Result API tests
- `assigned_defects/tests.py` - Assigned defects API tests
- `products/tests.py` - Products API tests

### Coverage Configuration
- `.coveragerc` - Coverage.py configuration for measuring statement and branch coverage

## Setup

### 1. Install Required Packages
```bash
cd /Users/mct61674/Desktop/BetaTraxService-GroupK
pip install -r requirements.txt
pip install factory_boy django-tenants psycopg2-binary
```

### 2. PostgreSQL Configuration (Multi-Tenant Setup)

#### Option A: Using Docker
BetaTrax uses PostgreSQL with separate-schema multi-tenancy via `django-tenants`. To run tests locally:

```bash
# Start PostgreSQL container using docker-compose
docker-compose up -d

# Or using docker CLI
docker run --name betatrax_postgres \
  -e POSTGRES_USER=betatrax \
  -e POSTGRES_PASSWORD=betatrax \
  -e POSTGRES_DB=betatrax \
  -p 5432:5432 \
  -d postgres:13
```

#### Option B: Manual PostgreSQL Installation
1. Install PostgreSQL locally (macOS: `brew install postgresql`)
2. Start PostgreSQL service (macOS: `brew services start postgresql`)
3. Create database and user:
   ```bash
   createdb betatrax
   psql -d betatrax -c "CREATE USER betatrax WITH PASSWORD 'betatrax';"
   psql -d betatrax -c "ALTER USER betatrax CREATEDB;"
   ```

### 3. Verify Database Connection
```bash
psql -h localhost -U betatrax -d betatrax
# If connection succeeds, exit with \q
```

### 4. Migrate Databases
Navigate to the project and initialize tenant schemas:
```bash
cd /Users/mct61674/Desktop/BetaTraxService-GroupK/BetaTrax
python manage.py migrate_schemas --executor=sequential
```

### 5. Navigate to Project Directory
```bash
cd /Users/mct61674/Desktop/BetaTraxService-GroupK/BetaTrax
```

## Running Tests

### Tenant-Aware Test Execution
BetaTrax uses `django-tenants` for multi-tenant support. All tests in `defects/tests/` use `TenantTestCase` and require PostgreSQL.

**Important**: Ensure PostgreSQL is running before executing tests!

### Option 1: Run All Tests with Tenant Support
```bash
python manage.py test defects.tests
```

### Option 2: Run Tests with Verbose Output
```bash
python manage.py test --verbosity=2 defects.tests
```

### Option 3: Run Specific Test Class
```bash
python manage.py test defects.tests.DeveloperMetricsTests
```

### Option 4: Run Single Test Method
```bash
python manage.py test defects.tests.DeveloperMetricsTests.test_good_rating
```

### Option 5: Using the Automated Test Runner Script
```bash
chmod +x run_tests.sh
./run_tests.sh             # Run tests only
./run_tests.sh --coverage  # Run with coverage
./run_tests.sh --html      # Generate HTML coverage report
```

## Coverage Analysis

### 1. Run Tests with Coverage
```bash
coverage run --source='.' manage.py test
```

### 2. Generate Coverage Report (Terminal)
```bash
coverage report
```

Example output:
```
Name                              Stmts   Miss  Cover
-----------------------------------------------------
defects/metrics.py                   25      0   100%
defects/tests.py                    120      5    96%
comments/tests.py                    12      2    83%
...
-----------------------------------------------------
TOTAL                              400     45    89%
```

### 3. Generate HTML Coverage Report
```bash
coverage html
```

Then open the report:
```bash
open htmlcov/index.html
```

Or if on Linux:
```bash
firefox htmlcov/index.html
```

### 4. View Coverage for Specific File
```bash
coverage report -m defects/metrics.py
```

### 5. View Branch Coverage (Advanced)
Enable branch coverage in .coveragerc or command:
```bash
coverage run --branch --source='.' manage.py test
coverage report --show-missing
```

## Developer Effectiveness Metrics Tests

The `DeveloperMetricsTestCase` class contains **8 comprehensive tests** covering all classification branches:

### Test Cases

1. **test_insufficient_data_less_than_twenty_fixed**
   - Tests when defects fixed < 20
   - Expected: Classification = "Insufficient data"
   - Branch coverage: Condition 1

2. **test_good_classification_low_reopen_ratio**
   - Tests when ratio = 0 (no reopened defects)
   - Expected: Classification = "Good"
   - Branch coverage: Condition 2.1

3. **test_good_classification_just_below_threshold**
   - Tests ratio at boundary (exactly 0)
   - Expected: Classification = "Good"
   - Branch coverage: Boundary condition

4. **test_fair_classification_between_thresholds**
   - Tests when 0.03125 ≤ ratio < 0.125
   - Expected: Classification = "Fair"
   - Branch coverage: Condition 2.2

5. **test_poor_classification_high_reopen_ratio**
   - Tests when ratio ≥ 0.125
   - Expected: Classification = "Poor"
   - Branch coverage: Condition 2.3

6. **test_no_fixed_defects**
   - Tests edge case with 0 fixed defects
   - Expected: Classification = "Insufficient data"
   - Branch coverage: Edge case

7. **test_metric_details_included**
   - Tests that all metric details are computed correctly
   - Branch coverage: Return value verification

8. **test_fair_classification_between_thresholds** (Ratio 1/32)
   - Tests at the exact boundary of 1/32
   - Branch coverage: Boundary condition

## API Endpoint Tests

The `DefectReportAPITestCase` covers these methods:

| Method     | Endpoint                    | Test Name                  |
|------------|-----------------------------|-----------------------------|
| GET        | /api/reports/               | test_list_defect_reports   |
| POST       | /api/reports/               | test_create_defect_report  |
| GET        | /api/reports/{id}/          | test_retrieve_defect_report|
| PATCH      | /api/reports/{id}/          | test_update_defect_report  |
| DELETE     | /api/reports/{id}/          | test_delete_defect_report  |
| GET        | /api/reports/?Status=...    | test_filter_by_status      |

## Expected Coverage Results

For the `defects/metrics.py` module:
- **Statement Coverage**: 100% (all lines executed)
- **Branch Coverage**: 100% (all conditional paths exercised)

For the overall project:
- **Minimum Target**: 85% statement coverage
- **Focus modules**: defects/metrics.py (100%), defects/tests.py (95%+)

## Example Coverage Report Output

```
Name                              Stmts   Miss  Cover   Missing
-----------------------------------------------------------------
defects/__init__.py                   0      0   100%
defects/admin.py                      4      0   100%
defects/apps.py                       4      0   100%
defects/metrics.py                   25      0   100%   (Full coverage!)
defects/models.py                    15      0   100%
defects/serializers.py               30      2    93%   42-44
defects/tests.py                    140      8    94%   150-157
defects/views.py                     80     12    85%   200-211
models/defects.py                    20      0   100%
-----------------------------------------------------------------
TOTAL                              318     22    93%
```

## Running Tests During Final Review

For the review presentation:

### Quick Verification (2 minutes)
```bash
cd BetaTrax
python manage.py test --verbosity=2
```

### Full Coverage Report (5 minutes)
```bash
cd BetaTrax
coverage run --source='.' manage.py test
coverage report -m
coverage html
open htmlcov/index.html
```

## Troubleshooting

### Tests fail with "ImproperlyConfigured"
- Ensure you're in the `BetaTrax` directory (where `manage.py` is located)
- Check that your `.venv` is activated

### Coverage shows 0% for a file
- Make sure tests are actually importing and using that file
- Add print statements to verify test execution

### AttributeError: 'module' has no attribute 'xyz'
- Ensure all necessary models are imported in test files
- Check that migrations have been run: `python manage.py migrate`

## Unit Tests Summary

Total test methods: **15+**
- Developer Effectiveness Metrics: 8 tests
- Defect API Operations: 6 tests  
- Comment API: 2 tests
- Resolving API: 1 test
- Assigned Defects API: 1 test
- Products API: 1 test

## Coverage Commands Quick Reference

```bash
# Run tests and generate coverage
coverage run --source='.' manage.py test

# View coverage report in terminal
coverage report

# View coverage report with missing lines
coverage report -m

# Generate HTML report
coverage html

# View specific file coverage
coverage report -m defects/metrics.py

# Clear coverage data
coverage erase

# Combine coverage runs
coverage combine
```

## Key Metrics for Sprint 3 Demonstration

### Metric Classification Rules (Verified by Tests)
- **Insufficient Data**: defects_fixed < 20
- **Good**: defects_fixed ≥ 20 AND reopen_ratio < 0.03125 (1/32)
- **Fair**: defects_fixed ≥ 20 AND 0.03125 ≤ reopen_ratio < 0.125 (1/8)
- **Poor**: defects_fixed ≥ 20 AND reopen_ratio ≥ 0.125

### Coverage Criteria Met
✓ Full Statement Coverage on metrics.py
✓ Full Branch Coverage on metrics.py
✓ Representative API endpoint tests
✓ Edge case handling tests

---

**Last Updated**: April 2026
**Testing Framework**: Django TestCase, Django REST Framework APIClient
**Coverage Tool**: coverage.py v7.4.1
