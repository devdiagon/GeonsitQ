echo "=========================================="
echo "  EJECUTANDO TESTS DE INTEGRACIÓN"
echo "=========================================="
echo ""

if [ -d "env" ]; then
    source env/bin/activate
fi

pytest tests/integration/ \
    -v \
    --tb=short \
    --cov=src \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-append \
    -m integration

echo ""
echo "=========================================="
echo "  TESTS DE INTEGRACIÓN COMPLETADOS"
echo "=========================================="
echo ""
echo "Reporte de cobertura: htmlcov/index.html"