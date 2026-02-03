echo "=========================================="
echo "  EJECUTANDO TESTS UNITARIOS"
echo "=========================================="
echo ""

if [ -d "env" ]; then
    source env/bin/activate
fi

pytest tests/unit/ \
    -v \
    --tb=short \
    --cov=src \
    --cov-report=html \
    --cov-report=term-missing \
    -m unit

echo ""
echo "=========================================="
echo "  TESTS COMPLETADOS"
echo "=========================================="
echo ""
echo "Reporte de cobertura HTML: htmlcov/index.html"