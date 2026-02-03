@echo off

echo ==========================================
echo   EJECUTANDO TESTS DE INTEGRACION
echo ==========================================
echo.

if exist env\Scripts\activate.bat (
    call env\Scripts\activate.bat
)

pytest tests/integration/ ^
    -v ^
    --tb=short ^
    --cov=src ^
    --cov-report=html ^
    --cov-report=term-missing ^
    --cov-append ^
    -m integration

echo.
echo ==========================================
echo   TESTS DE INTEGRACION COMPLETADOS
echo ==========================================
echo.
echo Reporte de cobertura: htmlcov\index.html

pause