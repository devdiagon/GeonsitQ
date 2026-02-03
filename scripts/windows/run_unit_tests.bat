@echo off

echo ==========================================
echo   EJECUTANDO TESTS UNITARIOS
echo ==========================================
echo.

if exist env\Scripts\activate.bat (
    call env\Scripts\activate.bat
)

pytest tests/unit/ ^
    -v ^
    --tb=short ^
    --cov=src ^
    --cov-report=html ^
    --cov-report=term-missing ^
    -m unit

echo.
echo ==========================================
echo   TESTS COMPLETADOS
echo ==========================================
echo.
echo Reporte de cobertura HTML: htmlcov\index.html

pause