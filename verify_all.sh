#!/bin/bash
echo "=================================="
echo "Complete Verification Script"
echo "=================================="
echo ""

echo "1. Python Syntax Check..."
for file in template_query_inference.py run_template_query_inference.py test_template_query_integration.py test_llm_inference.py openai_functionality.py; do
    python3 -m py_compile "$file" 2>&1 && echo "   ✓ $file" || echo "   ✗ $file"
done
echo ""

echo "2. Integration Tests..."
python3 test_template_query_integration.py | tail -3
echo ""

echo "3. Infrastructure Demo Test..."
python3 test_llm_inference.py 3 2>&1 | grep -E "(✓|✗|DEMO MODE|Test Complete)" | tail -10
echo ""

echo "4. CLI Tools Check..."
echo "   Testing --list..."
python3 run_template_query_inference.py --list | head -5 | tail -3
echo "   Testing --health..."
python3 run_template_query_inference.py --health 2>&1 | head -2
echo ""

echo "=================================="
echo "Verification Complete!"
echo "=================================="
