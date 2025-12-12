@echo off
REM Cleanup chromadb-docker folder for Windows-only usage
echo ====================================================================
echo CLEANING UP CHROMADB-DOCKER FOLDER
echo ====================================================================
echo.

cd /d "%~dp0"

echo The following files will be deleted:
echo.

REM Check which files exist
set FOUND=0

if exist "bootstrap-full.sh" (echo   X bootstrap-full.sh & set /a FOUND+=1)
if exist "bootstrap.sh" (echo   X bootstrap.sh & set /a FOUND+=1)
if exist "run-mcp-server.sh" (echo   X run-mcp-server.sh & set /a FOUND+=1)
if exist "start-po-rag.sh" (echo   X start-po-rag.sh & set /a FOUND+=1)
if exist "stop-po-rag.sh" (echo   X stop-po-rag.sh & set /a FOUND+=1)
if exist "bootstrap-full.ps1" (echo   X bootstrap-full.ps1 & set /a FOUND+=1)
if exist "bootstrap.ps1" (echo   X bootstrap.ps1 & set /a FOUND+=1)
if exist "setup-windows.bat" (echo   X setup-windows.bat & set /a FOUND+=1)
if exist "bedrock_embeddings.py" (echo   X bedrock_embeddings.py & set /a FOUND+=1)
if exist "test-embeddings.py" (echo   X test-embeddings.py & set /a FOUND+=1)
if exist "test-import.py" (echo   X test-import.py & set /a FOUND+=1)
if exist "test-metadata.py" (echo   X test-metadata.py & set /a FOUND+=1)
if exist "test-rag-connection.bat" (echo   X test-rag-connection.bat & set /a FOUND+=1)

if %FOUND%==0 (
    echo No files to delete. Folder is already clean!
    pause
    exit /b 0
)

echo.
set /p CONFIRM="Delete %FOUND% files? (Y/N): "
if /i not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo Deleting files...

REM Delete files
if exist "bootstrap-full.sh" del /f "bootstrap-full.sh" && echo   OK Deleted: bootstrap-full.sh
if exist "bootstrap.sh" del /f "bootstrap.sh" && echo   OK Deleted: bootstrap.sh
if exist "run-mcp-server.sh" del /f "run-mcp-server.sh" && echo   OK Deleted: run-mcp-server.sh
if exist "start-po-rag.sh" del /f "start-po-rag.sh" && echo   OK Deleted: start-po-rag.sh
if exist "stop-po-rag.sh" del /f "stop-po-rag.sh" && echo   OK Deleted: stop-po-rag.sh
if exist "bootstrap-full.ps1" del /f "bootstrap-full.ps1" && echo   OK Deleted: bootstrap-full.ps1
if exist "bootstrap.ps1" del /f "bootstrap.ps1" && echo   OK Deleted: bootstrap.ps1
if exist "setup-windows.bat" del /f "setup-windows.bat" && echo   OK Deleted: setup-windows.bat
if exist "bedrock_embeddings.py" del /f "bedrock_embeddings.py" && echo   OK Deleted: bedrock_embeddings.py
if exist "test-embeddings.py" del /f "test-embeddings.py" && echo   OK Deleted: test-embeddings.py
if exist "test-import.py" del /f "test-import.py" && echo   OK Deleted: test-import.py
if exist "test-metadata.py" del /f "test-metadata.py" && echo   OK Deleted: test-metadata.py
if exist "test-rag-connection.bat" del /f "test-rag-connection.bat" && echo   OK Deleted: test-rag-connection.bat

echo.
echo ====================================================================
echo CLEANUP COMPLETE
echo ====================================================================
echo.
echo Folder is now clean and Windows-ready!
echo.
pause
