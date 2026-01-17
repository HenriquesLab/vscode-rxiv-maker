/**
 * Installation method detection for rxiv-maker Python package.
 *
 * Detects how rxiv-maker was installed (Homebrew, pipx, uv, pip, etc.)
 * to provide appropriate upgrade instructions.
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as vscode from 'vscode';

const execAsync = promisify(exec);

// Output channel for logging
let outputChannel: vscode.OutputChannel | null = null;

function getOutputChannel(): vscode.OutputChannel {
    if (!outputChannel) {
        outputChannel = vscode.window.createOutputChannel('Rxiv-Maker');
    }
    return outputChannel;
}

export type InstallMethod = 'homebrew' | 'pipx' | 'uv' | 'pip-user' | 'pip' | 'dev' | 'unknown';

/**
 * Detect how rxiv-maker was installed.
 *
 * @returns Installation method
 */
export async function detectInstallMethod(): Promise<InstallMethod> {
    try {
        // Get the path to rxiv executable
        // Use platform-specific command to avoid shell compatibility issues
        const isWindows = process.platform === 'win32';
        const cmd = isWindows ? 'where rxiv 2>nul' : 'which rxiv 2>/dev/null';
        const { stdout: whichOutput } = await execAsync(cmd);
        const executablePath = whichOutput.trim();

        if (!executablePath) {
            return 'unknown';
        }

        // Check for Homebrew installation
        // Common Homebrew prefixes on macOS and Linux
        const homebrewPrefixes = [
            '/opt/homebrew',      // Apple Silicon Macs
            '/usr/local',         // Intel Macs and some Linux
            '/home/linuxbrew/.linuxbrew'  // Linux Homebrew
        ];

        for (const prefix of homebrewPrefixes) {
            if (executablePath.startsWith(prefix)) {
                // Additional verification: check if Cellar or opt/homebrew path exists
                if (executablePath.includes('/Cellar/') || executablePath.includes('/opt/homebrew/')) {
                    return 'homebrew';
                }
            }
        }

        // Check for pipx installation
        // pipx typically installs to ~/.local/pipx/venvs/{package}/
        if (executablePath.includes('.local/pipx/venvs/rxiv-maker') ||
            executablePath.includes('.local/share/pipx/venvs/rxiv-maker')) {
            return 'pipx';
        }

        // Check for uv tool installation
        // uv typically installs to ~/.local/share/uv/tools/{package}/
        if (executablePath.includes('.local/share/uv/tools/rxiv-maker')) {
            return 'uv';
        }

        // Check for development installation
        // Look for indicators like '.git' in the path or 'editable' markers
        if (executablePath.includes('/rxiv-maker/') &&
            (executablePath.includes('.git') || executablePath.includes('src/'))) {
            return 'dev';
        }

        // Check for pip user installation
        // User site-packages typically in ~/.local/lib/python*/site-packages
        if (executablePath.includes('.local/lib/python') &&
            executablePath.includes('site-packages')) {
            return 'pip-user';
        }

        // Check for system pip installation
        // System site-packages in /usr/lib or /usr/local/lib
        if (executablePath.includes('/site-packages/') ||
            executablePath.includes('/dist-packages/')) {
            return 'pip';
        }

        return 'unknown';
    } catch (error) {
        const output = getOutputChannel();
        output.appendLine(`Error detecting install method: ${error}`);
        return 'unknown';
    }
}

/**
 * Get the appropriate upgrade command for the installation method.
 *
 * @param installMethod The detected installation method
 * @returns Upgrade command string
 */
export function getUpgradeCommand(installMethod: InstallMethod): string {
    const commands: Record<InstallMethod, string> = {
        'homebrew': 'brew update && brew upgrade rxiv-maker',
        'pipx': 'pipx upgrade rxiv-maker',
        'uv': 'uv tool upgrade rxiv-maker',
        'pip-user': 'pip install --upgrade --user rxiv-maker',
        'pip': 'pip install --upgrade rxiv-maker',
        'dev': 'cd <repo> && git pull && uv sync',
        'unknown': 'pip install --upgrade rxiv-maker'
    };
    return commands[installMethod];
}

/**
 * Get a user-friendly name for the installation method.
 *
 * @param installMethod The detected installation method
 * @returns Friendly name string
 */
export function getFriendlyInstallName(installMethod: InstallMethod): string {
    const names: Record<InstallMethod, string> = {
        'homebrew': 'Homebrew',
        'pipx': 'pipx',
        'uv': 'uv tool',
        'pip-user': 'pip (user)',
        'pip': 'pip',
        'dev': 'Development mode',
        'unknown': 'Unknown'
    };
    return names[installMethod];
}

/**
 * Check if rxiv-maker is installed.
 *
 * @returns true if rxiv-maker is installed, false otherwise
 */
export async function isRxivMakerInstalled(): Promise<boolean> {
    try {
        const isWindows = process.platform === 'win32';
        const cmd = isWindows ? 'rxiv.exe --version 2>nul' : 'rxiv --version 2>/dev/null';
        const { stdout } = await execAsync(cmd);
        return stdout.trim().length > 0;
    } catch (error) {
        return false;
    }
}
