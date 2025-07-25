"""Centralized Docker management for Rxiv-Maker.

This module provides efficient Docker container management with session reuse,
volume caching, and optimized command construction for all Rxiv-Maker operations.
"""

import os
import platform
import subprocess
import time
from pathlib import Path
from typing import Any

from ..utils.platform import platform_detector


class DockerSession:
    """Manages a persistent Docker container session for multiple operations."""

    def __init__(self, container_id: str, image: str, workspace_dir: Path):
        """Initialize Docker session.

        Args:
            container_id: Docker container ID
            image: Docker image name
            workspace_dir: Workspace directory path
        """
        self.container_id = container_id
        self.image = image
        self.workspace_dir = workspace_dir
        self.created_at = time.time()
        self._active = True

    def is_active(self) -> bool:
        """Check if the Docker container is still running."""
        if not self._active:
            return False

        try:
            result = subprocess.run(
                [
                    "docker",
                    "container",
                    "inspect",
                    self.container_id,
                    "--format",
                    "{{.State.Running}}",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                is_running = result.stdout.strip().lower() == "true"
                if not is_running:
                    self._active = False
                return is_running
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            self._active = False

        return False

    def cleanup(self) -> bool:
        """Stop and remove the Docker container."""
        if not self._active:
            return True

        try:
            # Stop the container
            subprocess.run(
                ["docker", "stop", self.container_id], capture_output=True, timeout=10
            )

            # Remove the container
            subprocess.run(
                ["docker", "rm", self.container_id], capture_output=True, timeout=10
            )

            self._active = False
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False


class DockerManager:
    """Centralized Docker operations manager with session reuse and optimization."""

    def __init__(
        self,
        default_image: str = "henriqueslab/rxiv-maker-base:latest",
        workspace_dir: Path | None = None,
        enable_session_reuse: bool = True,
    ):
        """Initialize Docker manager.

        Args:
            default_image: Default Docker image to use
            workspace_dir: Workspace directory (defaults to current working directory)
            enable_session_reuse: Whether to reuse Docker containers across operations
        """
        self.default_image = default_image
        self.workspace_dir = workspace_dir or Path.cwd().resolve()
        self.enable_session_reuse = enable_session_reuse
        self.platform = platform_detector

        # Session management
        self._active_sessions: dict[str, DockerSession] = {}
        self._session_timeout = 300  # 5 minutes

        # Docker configuration
        self._docker_platform = self._detect_docker_platform()
        self._base_volumes = self._get_base_volumes()
        self._base_env = self._get_base_environment()

    def _detect_docker_platform(self) -> str:
        """Detect the optimal Docker platform for the current architecture."""
        machine = platform.machine().lower()
        if machine in ["arm64", "aarch64"]:
            return "linux/arm64"
        elif machine in ["x86_64", "amd64"]:
            return "linux/amd64"
        else:
            return "linux/amd64"  # fallback

    def _get_base_volumes(self) -> list[str]:
        """Get base volume mounts for all Docker operations."""
        return [f"{self.workspace_dir}:/workspace"]

    def _get_base_environment(self) -> dict[str, str]:
        """Get base environment variables for Docker containers."""
        env = {}

        # Pass through Rxiv-specific environment variables
        rxiv_vars = [
            "RXIV_ENGINE",
            "RXIV_VERBOSE",
            "RXIV_NO_UPDATE_CHECK",
            "MANUSCRIPT_PATH",
            "FORCE_FIGURES",
        ]

        for var in rxiv_vars:
            if var in os.environ:
                env[var] = os.environ[var]

        return env

    def _build_docker_command(
        self,
        command: str | list[str],
        image: str | None = None,
        working_dir: str = "/workspace",
        volumes: list[str] | None = None,
        environment: dict[str, str] | None = None,
        user: str | None = None,
        interactive: bool = False,
        remove: bool = True,
        detach: bool = False,
    ) -> list[str]:
        """Build a Docker run command with optimal settings."""
        docker_cmd = ["docker", "run"]

        # Container options
        if remove and not detach:
            docker_cmd.append("--rm")

        if detach:
            docker_cmd.append("-d")

        if interactive:
            docker_cmd.extend(["-i", "-t"])

        # Platform specification
        docker_cmd.extend(["--platform", self._docker_platform])

        # Volume mounts
        all_volumes = self._base_volumes.copy()
        if volumes:
            all_volumes.extend(volumes)

        for volume in all_volumes:
            docker_cmd.extend(["-v", volume])

        # Working directory
        docker_cmd.extend(["-w", working_dir])

        # Environment variables
        all_env = self._base_env.copy()
        if environment:
            all_env.update(environment)

        for key, value in all_env.items():
            docker_cmd.extend(["-e", f"{key}={value}"])

        # User specification
        if user:
            docker_cmd.extend(["--user", user])

        # Image
        docker_cmd.append(image or self.default_image)

        # Command
        if isinstance(command, str):
            docker_cmd.extend(["sh", "-c", command])
        else:
            docker_cmd.extend(command)

        return docker_cmd

    def _get_or_create_session(
        self, session_key: str, image: str
    ) -> DockerSession | None:
        """Get an existing session or create a new one if session reuse is enabled."""
        if not self.enable_session_reuse:
            return None

        # Clean up expired sessions
        self._cleanup_expired_sessions()

        # Check if we have an active session
        if session_key in self._active_sessions:
            session = self._active_sessions[session_key]
            if session.is_active():
                return session
            else:
                # Session is dead, remove it
                del self._active_sessions[session_key]

        # Create new session
        try:
            docker_cmd = self._build_docker_command(
                command=["sleep", "infinity"],  # Keep container alive
                image=image,
                detach=True,
                remove=False,
            )

            result = subprocess.run(
                docker_cmd, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                container_id = result.stdout.strip()
                session = DockerSession(container_id, image, self.workspace_dir)
                self._active_sessions[session_key] = session
                return session
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass

        return None

    def _cleanup_expired_sessions(self) -> None:
        """Clean up expired or inactive Docker sessions."""
        current_time = time.time()
        expired_keys = []

        for key, session in self._active_sessions.items():
            if (
                current_time - session.created_at > self._session_timeout
                or not session.is_active()
            ):
                session.cleanup()
                expired_keys.append(key)

        for key in expired_keys:
            del self._active_sessions[key]

    def run_command(
        self,
        command: str | list[str],
        image: str | None = None,
        working_dir: str = "/workspace",
        volumes: list[str] | None = None,
        environment: dict[str, str] | None = None,
        session_key: str | None = None,
        capture_output: bool = True,
        timeout: int | None = None,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        """Execute a command in a Docker container with optimization.

        Args:
            command: Command to execute (string or list)
            image: Docker image to use (defaults to default_image)
            working_dir: Working directory inside container
            volumes: Additional volume mounts
            environment: Additional environment variables
            session_key: Session key for container reuse (enables session reuse)
            capture_output: Whether to capture stdout/stderr
            timeout: Command timeout in seconds
            **kwargs: Additional arguments passed to subprocess.run

        Returns:
            CompletedProcess result
        """
        target_image = image or self.default_image

        # Try to use existing session if session_key provided
        session = None
        if session_key:
            session = self._get_or_create_session(session_key, target_image)

        if session and session.is_active():
            # Execute in existing container
            if isinstance(command, str):
                exec_cmd = [
                    "docker",
                    "exec",
                    "-w",
                    working_dir,
                    session.container_id,
                    "sh",
                    "-c",
                    command,
                ]
            else:
                exec_cmd = [
                    "docker",
                    "exec",
                    "-w",
                    working_dir,
                    session.container_id,
                ] + command
        else:
            # Create new container for this command
            exec_cmd = self._build_docker_command(
                command=command,
                image=target_image,
                working_dir=working_dir,
                volumes=volumes,
                environment=environment,
            )

        # Execute the command
        return subprocess.run(
            exec_cmd,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            **kwargs,
        )

    def run_mermaid_generation(
        self,
        input_file: Path,
        output_file: Path,
        background_color: str = "transparent",
        config_file: Path | None = None,
    ) -> subprocess.CompletedProcess:
        """Generate SVG from Mermaid diagram using Cairo-only approach."""
        # Build relative paths for Docker
        input_rel = input_file.relative_to(self.workspace_dir)
        output_rel = output_file.relative_to(self.workspace_dir)

        # Use Cairo-only Mermaid rendering via online Kroki service
        # This eliminates the need for local Puppeteer/Chromium dependencies
        python_script = f'''
import sys
import base64
import urllib.request
import urllib.parse
import zlib
from pathlib import Path

def generate_mermaid_svg():
    """Generate SVG from Mermaid using Kroki service (Cairo-compatible)."""
    try:
        # Read the Mermaid file
        with open("/workspace/{input_rel}", "r") as f:
            mermaid_content = f.read().strip()

        # Use Kroki service for Mermaid rendering (no browser dependencies)
        # Encode the content for URL safety
        encoded_content = base64.urlsafe_b64encode(
            zlib.compress(mermaid_content.encode("utf-8"))
        ).decode("ascii")

        # Build Kroki URL for SVG generation
        kroki_url = f"https://kroki.io/mermaid/svg/{{encoded_content}}"

        # Try to fetch SVG from Kroki service
        try:
            with urllib.request.urlopen(kroki_url, timeout=30) as response:
                if response.status == 200:
                    svg_content = response.read().decode("utf-8")

                    # Write the SVG file
                    with open("/workspace/{output_rel}", "w") as f:
                        f.write(svg_content)

                    print("Generated SVG using Kroki service (Cairo-compatible)")
                    return 0
                else:
                    raise Exception(
                        f"Kroki service returned status {{response.status}}"
                    )

        except Exception as kroki_error:
            print(f"Kroki service unavailable: {{kroki_error}}")
            # Fall back to a simple SVG placeholder
            fallback_svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" viewBox="0 0 800 400">
  <rect width="800" height="400" fill="{background_color}" stroke="#ddd" \
stroke-width="2"/>
  <text x="400" y="180" text-anchor="middle" \
font-family="Arial, sans-serif" font-size="18" fill="#666">
    <tspan x="400" dy="0">Mermaid Diagram</tspan>
    <tspan x="400" dy="30">(Service temporarily unavailable)</tspan>
  </text>
  <text x="400" y="250" text-anchor="middle" \
font-family="monospace" font-size="12" fill="#999">
    Source: {input_rel.name}
  </text>
</svg>"""

            with open("/workspace/{output_rel}", "w") as f:
                f.write(fallback_svg)

            print("Generated fallback SVG (Kroki service unavailable)")
            return 0

    except Exception as e:
        print(f"Error generating Mermaid SVG: {{e}}")
        return 1

if __name__ == "__main__":
    sys.exit(generate_mermaid_svg())
'''

        # Execute the Python-based Mermaid generation
        cmd_parts = ["python3", "-c", python_script]

        return self.run_command(command=cmd_parts, session_key="mermaid_generation")

    def run_cairo_conversion(
        self,
        input_file: Path,
        output_file: Path,
        output_format: str,
        dpi: int | None = 300,
    ) -> subprocess.CompletedProcess:
        """Convert SVG to other formats using CairoSVG with optimized execution."""
        input_rel = input_file.relative_to(self.workspace_dir)
        output_rel = output_file.relative_to(self.workspace_dir)

        # Build Python command for Cairo conversion
        cairo_cmd = (
            f"import cairosvg; "
            f"cairosvg.svg2{output_format}("
            f"url='/workspace/{input_rel}', "
            f"write_to='/workspace/{output_rel}'"
        )

        if output_format == "png" and dpi is not None:
            cairo_cmd += f", dpi={dpi}"

        cairo_cmd += ")"

        return self.run_command(
            command=["python3", "-c", cairo_cmd], session_key="cairo_conversion"
        )

    def run_python_script(
        self,
        script_file: Path,
        working_dir: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        """Execute a Python script with optimized Docker execution."""
        script_rel = script_file.relative_to(self.workspace_dir)
        docker_working_dir = "/workspace"

        if working_dir:
            work_rel = working_dir.relative_to(self.workspace_dir)
            docker_working_dir = f"/workspace/{work_rel}"

        return self.run_command(
            command=["python", f"/workspace/{script_rel}"],
            working_dir=docker_working_dir,
            environment=environment,
            session_key="python_execution",
        )

    def run_r_script(
        self,
        script_file: Path,
        working_dir: Path | None = None,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        """Execute an R script with optimized Docker execution."""
        script_rel = script_file.relative_to(self.workspace_dir)
        docker_working_dir = "/workspace"

        if working_dir:
            work_rel = working_dir.relative_to(self.workspace_dir)
            docker_working_dir = f"/workspace/{work_rel}"

        return self.run_command(
            command=["Rscript", f"/workspace/{script_rel}"],
            working_dir=docker_working_dir,
            environment=environment,
            session_key="r_execution",
        )

    def run_latex_compilation(
        self, tex_file: Path, working_dir: Path | None = None, passes: int = 3
    ) -> list[subprocess.CompletedProcess]:
        """Run LaTeX compilation with multiple passes in Docker."""
        tex_rel = tex_file.relative_to(self.workspace_dir)
        docker_working_dir = "/workspace"

        if working_dir:
            work_rel = working_dir.relative_to(self.workspace_dir)
            docker_working_dir = f"/workspace/{work_rel}"

        results = []
        session_key = "latex_compilation"

        for i in range(passes):
            result = self.run_command(
                command=["pdflatex", "-interaction=nonstopmode", tex_rel.name],
                working_dir=docker_working_dir,
                session_key=session_key,
            )
            results.append(result)

            # Run bibtex after first pass if bib file exists
            if i == 0:
                bib_file = tex_file.with_suffix(".bib")
                if bib_file.exists():
                    bib_result = self.run_command(
                        command=["bibtex", tex_rel.stem],
                        working_dir=docker_working_dir,
                        session_key=session_key,
                    )
                    results.append(bib_result)

        return results

    def check_docker_available(self) -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            return False

    def pull_image(self, image: str | None = None) -> bool:
        """Pull the Docker image if not already available."""
        target_image = image or self.default_image

        # First check if image is already available locally
        try:
            result = subprocess.run(
                ["docker", "image", "inspect", target_image],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return True  # Image already available locally
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            pass  # Image not available locally, proceed with pull

        # Image not available locally, try to pull it
        try:
            result = subprocess.run(
                ["docker", "pull", target_image],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False

    def cleanup_all_sessions(self) -> None:
        """Clean up all active Docker sessions."""
        for session in self._active_sessions.values():
            session.cleanup()
        self._active_sessions.clear()

    def get_session_stats(self) -> dict[str, Any]:
        """Get statistics about active Docker sessions."""
        stats: dict[str, Any] = {
            "total_sessions": len(self._active_sessions),
            "active_sessions": sum(
                1 for s in self._active_sessions.values() if s.is_active()
            ),
            "session_details": [],
        }

        for key, session in self._active_sessions.items():
            session_info = {
                "key": key,
                "container_id": session.container_id[:12],  # Short ID
                "image": session.image,
                "active": session.is_active(),
                "age_seconds": time.time() - session.created_at,
            }
            stats["session_details"].append(session_info)

        return stats

    def enable_aggressive_cleanup(self, enabled: bool = True) -> None:
        """Enable aggressive session cleanup for resource-constrained environments."""
        if enabled:
            self._session_timeout = 60  # 1 minute for aggressive cleanup
            self.enable_session_reuse = False  # Disable session reuse
        else:
            self._session_timeout = 300  # 5 minutes default
            self.enable_session_reuse = True

    def __del__(self):
        """Cleanup when manager is destroyed."""
        import contextlib

        with contextlib.suppress(Exception):
            self.cleanup_all_sessions()


# Global Docker manager instance
_docker_manager: DockerManager | None = None


def get_docker_manager(
    image: str | None = None,
    workspace_dir: Path | None = None,
    enable_session_reuse: bool = True,
    force_new: bool = False,
) -> DockerManager:
    """Get or create the global Docker manager instance."""
    global _docker_manager

    if _docker_manager is None or force_new:
        if _docker_manager is not None and force_new:
            # Clean up existing manager before creating new one
            _docker_manager.cleanup_all_sessions()

        default_image = image or "henriqueslab/rxiv-maker-base:latest"
        _docker_manager = DockerManager(
            default_image=default_image,
            workspace_dir=workspace_dir,
            enable_session_reuse=enable_session_reuse,
        )

    return _docker_manager


def cleanup_global_docker_manager() -> None:
    """Clean up the global Docker manager and all its sessions."""
    global _docker_manager
    if _docker_manager is not None:
        _docker_manager.cleanup_all_sessions()
        _docker_manager = None


def get_docker_stats() -> dict[str, Any] | None:
    """Get Docker session statistics from the global manager."""
    global _docker_manager
    if _docker_manager is not None:
        return _docker_manager.get_session_stats()
    return None
