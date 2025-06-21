@echo off
echo Reinstalling shotgun-terminal...
echo.

echo Uninstalling current version...
pipx uninstall shotgun-terminal

echo.
echo Installing from current directory...
pipx install -e .

echo.
echo Reinstallation complete!
pause