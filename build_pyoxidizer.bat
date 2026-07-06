@echo off
REM Build the GarutVON Desktop app with PyOxidizer.
REM macOS/Linux targets require a matching build host and toolchain.
pyoxidizer build --release --target-triple x86_64-pc-windows-msvc
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%
echo Build complete. Artifacts are in build\x86_64-pc-windows-msvc\release\exe\
