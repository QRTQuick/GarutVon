import threading
import sys
import os

# Add parent path to path imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def run_flask():
    print("[INIT] Starting GarutVON Flask Web Server on http://0.0.0.0:5000")
    from backend.web import app

    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def run_fastapi():
    import uvicorn

    default_port = int(os.getenv("FASTAPI_PORT", "8000"))
    ports_to_try = [default_port, 8001, 8002, 8003]

    for port in ports_to_try:
        try:
            print(
                f"[INIT] Starting GarutVON FastAPI Developer Portal on http://0.0.0.0:{port}"
            )
            uvicorn.run("backend.main:app", host="0.0.0.0", port=port, log_level="info")
            return
        except Exception as exc:
            exc_str = str(exc).lower()
            is_port_error = any(
                phrase in exc_str
                for phrase in ["address already in use", "bind", "10048", "48"]
            )
            if is_port_error and port != ports_to_try[-1]:
                print(
                    f"[WARN] Port {port} unavailable, trying port {ports_to_try[ports_to_try.index(port)+1]}..."
                )
                continue
            print(f"[ERROR] FastAPI startup failed on port {port}: {exc}")
            raise


if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)

    flask_thread.start()
    fastapi_thread.start()

    print("\n" + "=" * 60)
    print("  GarutVON v2 - High Performance Engine Running Successfully!")
    print("  - Website & User Dashboard: http://localhost:5000")
    print("  - Developer programmatic API: http://localhost:8000")
    print("=" * 60 + "\n")

    # Keep the main thread alive to allow clean exit handling
    try:
        flask_thread.join()
        fastapi_thread.join()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] GarutVON system terminated by user request.")
        sys.exit(0)
