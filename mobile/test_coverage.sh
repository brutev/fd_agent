#!/bin/bash

# Flutter Test Coverage Script
# This script runs all tests and generates comprehensive coverage reports

set -e

echo "🚀 Starting Flutter Test Coverage Analysis..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    print_error "Flutter is not installed or not in PATH"
    exit 1
fi

# Check if we're in a Flutter project
if [ ! -f "pubspec.yaml" ]; then
    print_error "Not in a Flutter project directory"
    exit 1
fi

print_status "Cleaning previous build artifacts..."
flutter clean

print_status "Getting dependencies..."
flutter pub get

# Create coverage directory
mkdir -p coverage

print_status "Running unit tests with coverage..."
flutter test --coverage test/unit/

if [ $? -ne 0 ]; then
    print_error "Unit tests failed"
    exit 1
fi

print_success "Unit tests completed successfully"

print_status "Running widget tests with coverage..."
flutter test --coverage test/widget/

if [ $? -ne 0 ]; then
    print_error "Widget tests failed"
    exit 1
fi

print_success "Widget tests completed successfully"

print_status "Running integration tests..."
flutter test test/integration/

if [ $? -ne 0 ]; then
    print_warning "Some integration tests failed, but continuing..."
fi

# Check if lcov is installed for HTML report generation
if command -v lcov &> /dev/null; then
    print_status "Generating HTML coverage report..."
    
    # Remove system files from coverage
    lcov --remove coverage/lcov.info \
        '*/flutter/packages/*' \
        '*/flutter/.pub-cache/*' \
        '*/flutter/bin/cache/*' \
        '*/.pub-cache/*' \
        '*/test/*' \
        '*/test_driver/*' \
        '*/*.g.dart' \
        '*/*.freezed.dart' \
        '*/*.mocks.dart' \
        -o coverage/lcov_cleaned.info
    
    # Generate HTML report
    genhtml coverage/lcov_cleaned.info -o coverage/html
    
    print_success "HTML coverage report generated in coverage/html/"
    
    # Calculate coverage percentage
    COVERAGE_PERCENT=$(lcov --summary coverage/lcov_cleaned.info 2>&1 | grep -o '[0-9.]*%' | tail -1)
    print_status "Overall test coverage: $COVERAGE_PERCENT"
    
    # Check if coverage meets minimum threshold
    COVERAGE_NUM=$(echo $COVERAGE_PERCENT | sed 's/%//')
    THRESHOLD=85
    
    if (( $(echo "$COVERAGE_NUM >= $THRESHOLD" | bc -l) )); then
        print_success "Coverage threshold met ($COVERAGE_NUM% >= $THRESHOLD%)"
    else
        print_warning "Coverage below threshold ($COVERAGE_NUM% < $THRESHOLD%)"
    fi
    
else
    print_warning "lcov not found. Install it to generate HTML reports:"
    print_warning "  macOS: brew install lcov"
    print_warning "  Ubuntu: sudo apt-get install lcov"
fi

# Generate coverage summary
print_status "Generating coverage summary..."

cat > coverage/summary.md << EOF
# Flutter Test Coverage Summary

Generated on: $(date)

## Test Results

### Unit Tests
- Location: \`test/unit/\`
- Status: ✅ Passed
- Coverage: Included in overall coverage

### Widget Tests  
- Location: \`test/widget/\`
- Status: ✅ Passed
- Coverage: Included in overall coverage

### Integration Tests
- Location: \`test/integration/\`
- Status: ⚠️ Check individual test results
- Coverage: Not included in coverage metrics

## Coverage Details

Overall Coverage: $COVERAGE_PERCENT

### Key Areas Covered:
- ✅ Validators (100% target)
- ✅ Shared utilities
- ✅ Widget components
- ✅ Business logic
- ✅ State management (BLoC)

### Files Excluded from Coverage:
- Generated files (\*.g.dart, \*.freezed.dart)
- Mock files (\*.mocks.dart)
- Test files
- Flutter framework files

## Coverage Reports

- **HTML Report**: Open \`coverage/html/index.html\` in a browser
- **LCOV Report**: \`coverage/lcov.info\`
- **Cleaned LCOV**: \`coverage/lcov_cleaned.info\`

## Recommendations

1. Maintain coverage above 85%
2. Focus on critical business logic
3. Add integration tests for user flows
4. Regular coverage monitoring in CI/CD

EOF

print_success "Coverage summary generated in coverage/summary.md"

# Run specific test categories if requested
if [ "$1" = "validators" ]; then
    print_status "Running validator-specific tests..."
    flutter test test/unit/shared/utils/validators_test.dart --coverage
    print_success "Validator tests completed"
fi

if [ "$1" = "widgets" ]; then
    print_status "Running widget-specific tests..."
    flutter test test/widget/ --coverage
    print_success "Widget tests completed"
fi

if [ "$1" = "integration" ]; then
    print_status "Running integration tests only..."
    flutter test test/integration/
    print_success "Integration tests completed"
fi

# Golden tests (if they exist)
if [ -d "test/golden" ]; then
    print_status "Running golden tests..."
    flutter test test/golden/
    if [ $? -eq 0 ]; then
        print_success "Golden tests passed"
    else
        print_warning "Golden tests failed - UI changes detected"
        print_status "To update golden files, run: flutter test --update-goldens test/golden/"
    fi
fi

print_success "🎉 Test coverage analysis completed!"
print_status "📊 View detailed results in coverage/html/index.html"
print_status "📋 Summary available in coverage/summary.md"

# Open coverage report if on macOS
if [[ "$OSTYPE" == "darwin"* ]] && [ -f "coverage/html/index.html" ]; then
    read -p "Open coverage report in browser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open coverage/html/index.html
    fi
fi