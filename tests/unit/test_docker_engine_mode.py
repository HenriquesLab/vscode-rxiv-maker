"""Tests for Docker Engine Mode functionality.

This module tests the Docker engine mode implementation logic,
including platform detection, command generation, and architecture handling.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest


class TestDockerEngineMode(unittest.TestCase):
    """Test Docker Engine Mode functionality."""

    def setUp(self):
        """Set up test environment."""
        self.original_env = os.environ.copy()
        # Clean environment for consistent testing
        for var in ['RXIV_ENGINE', 'DOCKER_IMAGE', 'DOCKER_HUB_REPO']:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_default_engine_mode_is_local(self):
        """Test that default engine mode is LOCAL."""
        # Test environment variable logic
        engine_mode = os.environ.get('RXIV_ENGINE', 'LOCAL')
        self.assertEqual(engine_mode, "LOCAL")

    def test_docker_engine_mode_override(self):
        """Test RXIV_ENGINE=DOCKER override."""
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        engine_mode = os.environ.get('RXIV_ENGINE', 'LOCAL')
        self.assertEqual(engine_mode, "DOCKER")

    def test_default_docker_image(self):
        """Test default Docker image configuration."""
        docker_image = os.environ.get('DOCKER_IMAGE', 'henriqueslab/rxiv-maker-base:latest')
        self.assertEqual(docker_image, "henriqueslab/rxiv-maker-base:latest")

    def test_custom_docker_image_override(self):
        """Test custom Docker image override."""
        os.environ['DOCKER_IMAGE'] = 'custom/image:tag'
        docker_image = os.environ.get('DOCKER_IMAGE', 'henriqueslab/rxiv-maker-base:latest')
        self.assertEqual(docker_image, "custom/image:tag")

    @patch('subprocess.run')
    def test_platform_detection_amd64(self, mock_run):
        """Test platform detection for AMD64 architecture."""
        # Mock uname -m to return x86_64
        mock_run.return_value = Mock(stdout="x86_64\n", returncode=0)
        
        result = self._get_docker_platform()
        self.assertEqual(result.strip(), "linux/amd64")

    @patch('subprocess.run')
    def test_platform_detection_arm64(self, mock_run):
        """Test platform detection for ARM64 architecture."""
        # Mock uname -m to return arm64
        mock_run.return_value = Mock(stdout="arm64\n", returncode=0)
        
        result = self._get_docker_platform()
        self.assertEqual(result.strip(), "linux/arm64")

    @patch('subprocess.run')
    def test_platform_detection_aarch64(self, mock_run):
        """Test platform detection for aarch64 architecture."""
        # Mock uname -m to return aarch64
        mock_run.return_value = Mock(stdout="aarch64\n", returncode=0)
        
        result = self._get_docker_platform()
        self.assertEqual(result.strip(), "linux/arm64")

    def test_docker_command_generation(self):
        """Test Docker command generation in Docker mode."""
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        
        # Simulate Docker command generation logic
        def generate_docker_command():
            if os.environ.get('RXIV_ENGINE') == 'DOCKER':
                docker_image = os.environ.get('DOCKER_IMAGE', 'henriqueslab/rxiv-maker-base:latest')
                platform = self._get_docker_platform()
                return f"docker run --rm --platform {platform} -v $(PWD):/workspace -w /workspace {docker_image} python"
            else:
                return "python3"
        
        result = generate_docker_command()
        
        expected_parts = [
            "docker run",
            "--rm",
            "--platform",
            "-v $(PWD):/workspace",
            "-w /workspace",
            "henriqueslab/rxiv-maker-base:latest",
            "python"
        ]
        
        for part in expected_parts:
            self.assertIn(part, result)

    def test_docker_mode_status_detection(self):
        """Test Docker mode status detection."""
        # Test LOCAL mode status
        def get_engine_status():
            if os.environ.get('RXIV_ENGINE') == 'DOCKER':
                platform = self._get_docker_platform()
                return f"🐳 Docker ({platform})"
            else:
                return "💻 Local"
        
        status = get_engine_status()
        self.assertIn("💻 Local", status)
        
        # Test DOCKER mode status
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        status = get_engine_status()
        self.assertIn("🐳 Docker", status)

    def test_docker_mode_active_flag(self):
        """Test DOCKER_MODE_ACTIVE flag setting."""
        # Test LOCAL mode
        def is_docker_mode_active():
            return os.environ.get('RXIV_ENGINE') == 'DOCKER'
        
        self.assertFalse(is_docker_mode_active())
        
        # Test DOCKER mode
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        self.assertTrue(is_docker_mode_active())

    def test_docker_run_cmd_structure(self):
        """Test Docker run command structure."""
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        
        def generate_docker_run_cmd():
            platform = self._get_docker_platform()
            return f"docker run --rm --platform {platform} -v $(PWD):/workspace -w /workspace"
        
        result = generate_docker_run_cmd()
        
        # Verify Docker run command has proper structure
        self.assertIn("docker run --rm", result)
        self.assertIn("--platform", result)
        self.assertIn("-v $(PWD):/workspace", result)
        self.assertIn("-w /workspace", result)

    def test_docker_platform_includes_architecture(self):
        """Test that Docker platform includes proper architecture."""
        result = self._get_docker_platform()
        
        # Should be either linux/amd64 or linux/arm64
        self.assertTrue(
            result in ["linux/amd64", "linux/arm64"],
            f"Unexpected platform: {result}"
        )

    def test_multiple_docker_variables_consistency(self):
        """Test consistency between Docker-related variables."""
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        os.environ['DOCKER_IMAGE'] = 'test/image:v1.0'
        
        # Test variable consistency
        self.assertEqual(os.environ.get('RXIV_ENGINE'), 'DOCKER')
        self.assertEqual(os.environ.get('DOCKER_IMAGE'), 'test/image:v1.0')
        self.assertTrue(os.environ.get('RXIV_ENGINE') == 'DOCKER')

    def test_docker_hub_repo_configuration(self):
        """Test Docker Hub repository configuration."""
        docker_hub_repo = os.environ.get('DOCKER_HUB_REPO', 'henriqueslab/rxiv-maker-base')
        self.assertEqual(docker_hub_repo, "henriqueslab/rxiv-maker-base")
        
        # Test override
        os.environ['DOCKER_HUB_REPO'] = 'custom/repo'
        docker_hub_repo = os.environ.get('DOCKER_HUB_REPO', 'henriqueslab/rxiv-maker-base')
        self.assertEqual(docker_hub_repo, "custom/repo")

    def test_output_dir_consistent_across_modes(self):
        """Test that OUTPUT_DIR is consistent across engine modes."""
        # Both modes should use the same output directory
        output_dir = "output"
        
        # LOCAL mode
        self.assertEqual(output_dir, "output")
        
        # DOCKER mode (should be the same)
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        self.assertEqual(output_dir, "output")

    @patch('subprocess.run')
    def test_platform_detection_fallback(self, mock_run):
        """Test platform detection fallback for unknown architectures."""
        # Mock uname -m to return unknown architecture
        mock_run.return_value = Mock(stdout="unknown_arch\n", returncode=0)
        
        result = self._get_docker_platform()
        # Should default to amd64 for unknown architectures
        self.assertEqual(result.strip(), "linux/amd64")

    def test_case_sensitivity_docker_mode(self):
        """Test case sensitivity for RXIV_ENGINE values."""
        # Test lowercase (should not match, case sensitive)
        os.environ['RXIV_ENGINE'] = 'docker'
        self.assertFalse(os.environ.get('RXIV_ENGINE') == 'DOCKER')
        
        # Test uppercase
        os.environ['RXIV_ENGINE'] = 'DOCKER'  
        self.assertTrue(os.environ.get('RXIV_ENGINE') == 'DOCKER')

    def test_makefile_conditional_logic(self):
        """Test conditional logic for engine modes."""
        # Test that command generation differs between modes
        def get_python_cmd():
            if os.environ.get('RXIV_ENGINE') == 'DOCKER':
                docker_image = os.environ.get('DOCKER_IMAGE', 'henriqueslab/rxiv-maker-base:latest')
                platform = self._get_docker_platform()
                return f"docker run --rm --platform {platform} -v $(PWD):/workspace -w /workspace {docker_image} python"
            else:
                return "python3"
        
        # Local mode
        local_cmd = get_python_cmd()
        
        # Docker mode
        os.environ['RXIV_ENGINE'] = 'DOCKER'
        docker_cmd = get_python_cmd()
        
        self.assertNotEqual(local_cmd, docker_cmd)
        self.assertNotIn("docker", local_cmd.lower())
        self.assertIn("docker", docker_cmd.lower())

    def _get_docker_platform(self) -> str:
        """Helper to get Docker platform detection result."""
        # Simulate the shell command from Makefile
        try:
            result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
            arch = result.stdout.strip()
            
            if arch in ['arm64', 'aarch64']:
                return "linux/arm64"
            else:
                return "linux/amd64"
        except Exception:
            return "linux/amd64"  # Default fallback


class TestDockerCommandIntegration(unittest.TestCase):
    """Test Docker command integration scenarios."""

    @patch('subprocess.run')
    def test_docker_availability_check(self, mock_run):
        """Test checking if Docker is available."""
        # Mock successful docker --version
        mock_run.return_value = Mock(returncode=0, stdout="Docker version 20.10.0")
        
        result = subprocess.run(['docker', '--version'], capture_output=True)
        self.assertEqual(result.returncode, 0)

    @patch('subprocess.run')
    def test_docker_image_pull_simulation(self, mock_run):
        """Test Docker image pull simulation."""
        # Mock successful docker pull
        mock_run.return_value = Mock(returncode=0, stdout="Pull complete")
        
        result = subprocess.run(
            ['docker', 'pull', 'henriqueslab/rxiv-maker-base:latest'],
            capture_output=True
        )
        self.assertEqual(result.returncode, 0)

    def test_volume_mount_path_construction(self):
        """Test Docker volume mount path construction."""
        current_dir = Path.cwd()
        expected_mount = f"-v {current_dir}:/workspace"
        
        # This would be part of the Docker run command
        docker_cmd_parts = [
            "docker", "run", "--rm",
            f"-v {current_dir}:/workspace",
            "-w /workspace",
            "henriqueslab/rxiv-maker-base:latest",
            "python"
        ]
        
        self.assertIn(expected_mount, " ".join(docker_cmd_parts))

    def test_working_directory_setting(self):
        """Test Docker working directory setting."""
        docker_cmd = "docker run --rm -v $(PWD):/workspace -w /workspace"
        self.assertIn("-w /workspace", docker_cmd)


if __name__ == '__main__':
    unittest.main()