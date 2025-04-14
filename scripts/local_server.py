#!/usr/bin/env python
"""
Local server management script for BPTracker.

This script provides commands to start, stop, and restart both
the PostgreSQL database and the BPTracker backend server.
"""
import errno
import os
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv

# Create Typer app
app = typer.Typer(help="Manage local BPTracker servers", add_completion=False)

# Add the parent directory to the path so we can import from src if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Get PostgreSQL configuration from environment variables
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "bptracker")

# Backend server configuration
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8078

# Store process IDs in the project directory for better persistence
PROJECT_ROOT = Path(__file__).parent.parent
PG_PID_FILE = PROJECT_ROOT / "pg.pid"
BACKEND_PID_FILE = PROJECT_ROOT / "backend.pid"


def is_process_running(pid: int) -> bool:
    """Check if a process with the given PID is running."""
    try:
        os.kill(pid, 0)
        return True
    except OSError as e:
        # Process doesn't exist
        if e.errno == errno.ESRCH:
            return False
        # Process exists but we don't have permission to send signals to it
        elif e.errno == errno.EPERM:
            return True
        # Some other error
        else:
            return False


def get_pid_from_file(pid_file: Path) -> Optional[int]:
    """Get PID from a PID file if it exists and the process is running."""
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
            if is_process_running(pid):
                return pid
        except (ValueError, IOError):
            pass
    return None


def is_port_in_use(host: str, port: int) -> bool:
    """Check if a port is in use by attempting to connect to it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.settimeout(1)
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False


def save_pid_to_file(pid_file: Path, pid: int) -> None:
    """Save PID to a file."""
    try:
        # Ensure the parent directory exists
        pid_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the PID to the file
        with open(pid_file, 'w') as f:
            f.write(str(pid))
        
        # Verify the file was created
        if pid_file.exists():
            typer.echo(f"Successfully saved PID {pid} to {pid_file}")
        else:
            typer.echo(f"Warning: PID file {pid_file} was not created")
    except Exception as e:
        typer.echo(f"Warning: Failed to save PID to {pid_file}: {e}")


def kill_process(pid: int, force: bool = False) -> bool:
    """Kill a process with the given PID."""
    try:
        if force:
            os.kill(pid, signal.SIGKILL)
        else:
            os.kill(pid, signal.SIGTERM)
        return True
    except OSError as e:
        # Process doesn't exist - consider this a success since the goal was to ensure the process is not running
        if e.errno == errno.ESRCH:
            return True
        # Process exists but we don't have permission
        elif e.errno == errno.EPERM:
            return False
        # Some other error
        else:
            return False


def start_postgresql() -> bool:
    """Start PostgreSQL database server."""
    # Check if PostgreSQL is already running
    if is_port_in_use(DB_HOST, int(DB_PORT)):
        typer.echo(f"PostgreSQL is already running on port {DB_PORT}")
        return True

    try:
        typer.echo("Starting PostgreSQL...")
        # Use pg_ctl to start PostgreSQL with -w (wait) flag and redirect logs to /dev/null
        result = subprocess.run(
            [
                "pg_ctl", 
                "-D", "/opt/homebrew/var/postgresql@14", 
                "-l", "/dev/null", 
                "-w",  # Wait for startup to complete
                "start"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        
        # Check if PostgreSQL started successfully
        if result.returncode == 0 and is_port_in_use(DB_HOST, int(DB_PORT)):
            typer.echo(f"PostgreSQL is running on port {DB_PORT}")
            return True
        else:
            typer.echo(f"Failed to start PostgreSQL: {result.stderr}")
            return False
    except Exception as e:
        typer.echo(f"Error starting PostgreSQL: {e}")
        return False


def stop_postgresql() -> bool:
    """Stop PostgreSQL database server."""
    # Check if PostgreSQL is running
    if not is_port_in_use(DB_HOST, int(DB_PORT)):
        typer.echo("PostgreSQL is not running")
        return True
    
    try:
        # Stop PostgreSQL using pg_ctl with -w (wait) flag
        typer.echo("Stopping PostgreSQL...")
        result = subprocess.run(
            [
                "pg_ctl", 
                "-D", "/opt/homebrew/var/postgresql@14", 
                "-w",  # Wait for shutdown to complete
                "stop"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        
        # Check if PostgreSQL stopped successfully
        if result.returncode == 0 and not is_port_in_use(DB_HOST, int(DB_PORT)):
            typer.echo("PostgreSQL stopped successfully")
            return True
        else:
            typer.echo(f"Failed to stop PostgreSQL: {result.stderr}")
            return False
    except Exception as e:
        typer.echo(f"Error stopping PostgreSQL: {e}")
        return False


def start_backend() -> bool:
    """Start BPTracker backend server."""
    # Check if backend is already running
    backend_pid = get_pid_from_file(BACKEND_PID_FILE)
    if backend_pid:
        typer.echo(f"Backend server is already running (PID: {backend_pid})")
        return True
    
    # Check if port is in use, which means backend might be running without a PID file
    if is_port_in_use(BACKEND_HOST, BACKEND_PORT):
        typer.echo(f"Backend server is already running on port {BACKEND_PORT} (PID file not found)")
        typer.echo(f"API available at http://{BACKEND_HOST}:{BACKEND_PORT}")
        return True
    
    try:
        # Start the backend server
        typer.echo("Starting BPTracker backend server...")
        
        process = subprocess.Popen(
            [
                "python", "-m", "uvicorn", 
                "src.main:app", 
                "--host", BACKEND_HOST, 
                "--port", str(BACKEND_PORT)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            cwd=PROJECT_ROOT,
        )
        
        # Save PID to file
        save_pid_to_file(BACKEND_PID_FILE, process.pid)
        
        # Wait to ensure it starts properly
        typer.echo("Waiting for backend server to start...")
        for i in range(20):  # Try for up to 10 seconds (20 * 0.5s)
            time.sleep(0.5)
            if is_port_in_use(BACKEND_HOST, BACKEND_PORT):
                typer.echo(f"Backend server is running on port {BACKEND_PORT}")
                typer.echo(f"API available at http://{BACKEND_HOST}:{BACKEND_PORT}")
                return True
            # Print a dot every second to show progress
            if i % 2 == 0:
                typer.echo(".", nl=False)
        
        typer.echo("")  # New line after dots
        
        # If we get here, the server didn't start properly
        if is_process_running(process.pid):
            typer.echo("Process is running but port is not active. Server might not have started correctly.")
            # Print any error output from the process
            try:
                stderr_output = process.stderr.read().decode('utf-8')
                if stderr_output:
                    typer.echo(f"Server error output: {stderr_output}")
            except Exception:
                pass
            
            # Kill the process since it's not working correctly
            kill_process(process.pid, force=True)
            if BACKEND_PID_FILE.exists():
                BACKEND_PID_FILE.unlink()
                typer.echo(f"Removed PID file {BACKEND_PID_FILE}")
            return False
        else:
            typer.echo("Failed to start backend server")
            # Clean up PID file if process didn't start successfully
            if BACKEND_PID_FILE.exists():
                BACKEND_PID_FILE.unlink()
                typer.echo(f"Removed PID file {BACKEND_PID_FILE}")
            return False
    except Exception as e:
        typer.echo(f"Error starting backend server: {e}")
        # Clean up PID file if there was an error
        if BACKEND_PID_FILE.exists():
            BACKEND_PID_FILE.unlink()
            typer.echo(f"Removed PID file {BACKEND_PID_FILE}")
        return False


def stop_backend() -> bool:
    """Stop BPTracker backend server."""
    backend_pid = get_pid_from_file(BACKEND_PID_FILE)
    
    if not backend_pid:
        # Check if backend is running without a PID file
        if is_port_in_use(BACKEND_HOST, BACKEND_PORT):
            typer.echo("Backend server is running but was not started by this script (no PID file)")
            typer.echo("Please stop the backend server manually")
            return False
        else:
            typer.echo("Backend server is not running")
            return True
    
    try:
        # Stop the backend server by killing the process
        typer.echo(f"Stopping backend server (PID: {backend_pid})...")
        if kill_process(int(backend_pid)):
            typer.echo("Backend server stopped successfully")
            BACKEND_PID_FILE.unlink(missing_ok=True)
            return True
        else:
            typer.echo("Failed to stop backend server, trying force kill...")
            if kill_process(int(backend_pid), force=True):
                typer.echo("Backend server force stopped successfully")
                BACKEND_PID_FILE.unlink(missing_ok=True)
                return True
            else:
                typer.echo("Failed to stop backend server")
                return False
    except Exception as e:
        typer.echo(f"Error stopping backend server: {e}")
        return False


@app.command()
def start():
    """Start PostgreSQL and BPTracker backend server."""
    pg_success = start_postgresql()
    backend_success = start_backend()
    
    if pg_success and backend_success:
        typer.echo("All services started successfully")
    else:
        typer.echo("Some services failed to start")


@app.command()
def stop():
    """Stop PostgreSQL and BPTracker backend server."""
    backend_success = stop_backend()
    pg_success = stop_postgresql()
    
    if pg_success and backend_success:
        typer.echo("All services stopped successfully")
    else:
        typer.echo("Some services failed to stop")


@app.command()
def restart():
    """Restart PostgreSQL and BPTracker backend server."""
    typer.echo("Restarting services...")
    
    # Check if backend is running without a PID file
    backend_pid = get_pid_from_file(BACKEND_PID_FILE)
    backend_port_in_use = is_port_in_use(BACKEND_HOST, BACKEND_PORT)
    
    # If backend is running without a PID file, we can't restart it
    if not backend_pid and backend_port_in_use:
        typer.echo("Backend server is running but was not started by this script (no PID file)")
        typer.echo("Please stop the backend server manually before restarting")
        return
    
    # Stop services
    backend_stopped = stop_backend()
    pg_stopped = stop_postgresql()
    
    if not backend_stopped or not pg_stopped:
        typer.echo("Failed to stop some services, cannot restart")
        return
    
    # Wait a moment before starting again
    time.sleep(2)
    
    # Start services
    pg_success = start_postgresql()
    backend_success = start_backend()
    
    if pg_success and backend_success:
        typer.echo("All services restarted successfully")
    else:
        typer.echo("Some services failed to restart")


@app.command()
def status():
    """Check the status of PostgreSQL and BPTracker backend server."""
    # Check PostgreSQL status
    pg_port_in_use = is_port_in_use(DB_HOST, int(DB_PORT))
    
    if pg_port_in_use:
        typer.echo(f"PostgreSQL: Running (Port {DB_PORT} is active)")
    else:
        typer.echo("PostgreSQL: Not running")
    
    # Check backend status
    backend_pid = get_pid_from_file(BACKEND_PID_FILE)
    backend_port_in_use = is_port_in_use(BACKEND_HOST, BACKEND_PORT)
    
    # Debug information about PID file
    typer.echo(f"Debug: PID file location: {BACKEND_PID_FILE}")
    if BACKEND_PID_FILE.exists():
        try:
            pid_content = BACKEND_PID_FILE.read_text().strip()
            typer.echo(f"Debug: PID file exists with content: {pid_content}")
            try:
                pid = int(pid_content)
                if is_process_running(pid):
                    typer.echo(f"Debug: Process with PID {pid} is running")
                else:
                    typer.echo(f"Debug: Process with PID {pid} is NOT running")
            except ValueError:
                typer.echo(f"Debug: PID file contains invalid content")
        except Exception as e:
            typer.echo(f"Debug: Error reading PID file: {e}")
    else:
        typer.echo("Debug: PID file does not exist")
    
    typer.echo(f"Debug: Port {BACKEND_PORT} is {'in use' if backend_port_in_use else 'NOT in use'}")
    
    # Determine backend status based on port usage if PID file is missing
    if backend_pid and is_port_in_use(BACKEND_HOST, BACKEND_PORT):
        typer.echo(f"Backend server: Running (PID: {backend_pid})")
        typer.echo(f"API available at http://{BACKEND_HOST}:{BACKEND_PORT}")
    elif backend_port_in_use:
        # If port is in use but no PID file, create a PID file for the process using the port
        typer.echo(f"Backend server: Running (Port {BACKEND_PORT} is active, but PID file not found)")
        typer.echo(f"API available at http://{BACKEND_HOST}:{BACKEND_PORT}")
        
        # Try to find the process using this port and save its PID
        try:
            # On macOS, use lsof to find the process using the port
            result = subprocess.run(
                ["lsof", "-i", f":{BACKEND_PORT}", "-t"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = int(result.stdout.strip().split("\n")[0])
                typer.echo(f"Debug: Found process with PID {pid} using port {BACKEND_PORT}")
                if is_process_running(pid):
                    save_pid_to_file(BACKEND_PID_FILE, pid)
                    typer.echo(f"Debug: Saved PID {pid} to {BACKEND_PID_FILE}")
        except Exception as e:
            typer.echo(f"Debug: Error finding process for port {BACKEND_PORT}: {e}")
    elif backend_pid:
        typer.echo(f"Backend server: Process with PID {backend_pid} exists but is not listening on port {BACKEND_PORT}")
        # Clean up the PID file since the process isn't working correctly
        BACKEND_PID_FILE.unlink(missing_ok=True)
        typer.echo("Removed invalid PID file")
    else:
        typer.echo("Backend server: Not running")


if __name__ == "__main__":
    app()
