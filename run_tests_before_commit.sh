#!/bin/bash
# Pre-Deployment Validation Script
# Run this BEFORE committing changes to ensure no regressions

set -e  # Exit on any error

echo ""
echo "=========================================="
echo "  PRE-DEPLOYMENT VALIDATION"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Run Django Tests
echo -e "${BLUE}[1/4] Running Django Unit Tests...${NC}"
docker compose exec -T web python manage.py test management_reports --verbosity=2

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All unit tests passed${NC}"
else
    echo -e "${RED}✗ Unit tests failed - DO NOT DEPLOY${NC}"
    exit 1
fi

echo ""

# Step 2: Run System Validation
echo -e "${BLUE}[2/4] Running System Validation...${NC}"
docker compose exec -T web python validate_system.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ System validation passed${NC}"
else
    echo -e "${RED}✗ System validation failed - DO NOT DEPLOY${NC}"
    exit 1
fi

echo ""

# Step 3: Check for Migration Issues
echo -e "${BLUE}[3/4] Checking for pending migrations...${NC}"
PENDING=$(docker compose exec -T web python manage.py showmigrations --plan | grep "\[ \]" | wc -l)

if [ "$PENDING" -eq 0 ]; then
    echo -e "${GREEN}✓ No pending migrations${NC}"
else
    echo -e "${YELLOW}⚠ Warning: $PENDING pending migrations found${NC}"
    echo -e "${YELLOW}  Run: docker compose exec web python manage.py migrate${NC}"
fi

echo ""

# Step 4: Static Files Check
echo -e "${BLUE}[4/4] Verifying critical files exist...${NC}"

FILES_TO_CHECK=(
    "app/management_reports/views.py"
    "app/reports/excel_generator.py"
    "app/reports/pdf_generator.py"
    "app/core/templates/base.html"
    "app/management_reports/templates/management_reports/dashboard.html"
)

ALL_FILES_EXIST=true

for file in "${FILES_TO_CHECK[@]}"; do
    if docker compose exec -T web test -f "$file"; then
        echo -e "${GREEN}✓ $file${NC}"
    else
        echo -e "${RED}✗ $file NOT FOUND${NC}"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    echo -e "${RED}✗ Critical files missing - DO NOT DEPLOY${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}  ✓ ALL VALIDATIONS PASSED"
echo -e "  SAFE TO COMMIT AND DEPLOY${NC}"
echo "=========================================="
echo ""

exit 0
