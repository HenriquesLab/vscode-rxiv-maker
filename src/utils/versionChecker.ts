/**
 * Version checking and update notification for rxiv-maker Python package.
 *
 * Checks PyPI for the latest version and notifies users when updates are available.
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as https from 'https';
import * as vscode from 'vscode';
import { detectInstallMethod, type InstallMethod } from './installDetector';

const execAsync = promisify(exec);

interface VersionInfo {
    current: string | null;
    latest: string | null;
    updateAvailable: boolean;
}

interface CacheData {
    lastCheck: string;
    latestVersion: string;
    currentVersion: string;
    updateAvailable: boolean;
}

/**
 * Get the current installed version of rxiv-maker.
 *
 * @returns Version string or null if not installed
 */
export async function getRxivMakerVersion(): Promise<string | null> {
    try {
        const { stdout } = await execAsync('rxiv --version 2>/dev/null || rxiv.exe --version 2>nul');
        // Parse output like "rxiv-maker version 1.8.8"
        const match = stdout.trim().match(/(\d+\.\d+\.\d+)/);
        return match ? match[1] : null;
    } catch (error) {
        return null;
    }
}

/**
 * Check if rxiv-maker is outdated via Homebrew.
 *
 * @returns Object with current and latest version if outdated, null otherwise
 */
export async function checkHomebrewOutdated(): Promise<{ current: string; latest: string } | null> {
    try {
        // Run: brew outdated --verbose rxiv-maker
        // Output format: "rxiv-maker (1.8.6) < 1.8.8"
        const { stdout } = await execAsync('brew outdated --verbose rxiv-maker 2>/dev/null');

        if (!stdout.trim()) {
            // Package is up to date or not installed
            return null;
        }

        // Parse output: "rxiv-maker (1.8.6) < 1.8.8"
        const match = stdout.trim().match(/\(([0-9.]+)\)\s*<\s*([0-9.]+)/);
        if (match) {
            return {
                current: match[1],
                latest: match[2]
            };
        }

        return null;
    } catch (error) {
        // brew not installed or command failed
        return null;
    }
}

/**
 * Fetch the latest version from PyPI.
 *
 * @returns Latest version string or null on error
 */
export async function fetchLatestVersion(): Promise<string | null> {
    return new Promise((resolve) => {
        const url = 'https://pypi.org/pypi/rxiv-maker/json';

        https.get(url, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    resolve(json.info.version);
                } catch (error) {
                    console.error('Error parsing PyPI response:', error);
                    resolve(null);
                }
            });
        }).on('error', (error) => {
            console.error('Error fetching latest version:', error);
            resolve(null);
        });
    });
}

/**
 * Compare two semantic version strings.
 *
 * @param current Current version
 * @param latest Latest version
 * @returns true if latest is newer than current
 */
export function isNewerVersion(current: string, latest: string): boolean {
    const currentParts = current.split('.').map(Number);
    const latestParts = latest.split('.').map(Number);

    for (let i = 0; i < Math.max(currentParts.length, latestParts.length); i++) {
        const currentPart = currentParts[i] || 0;
        const latestPart = latestParts[i] || 0;

        if (latestPart > currentPart) {
            return true;
        }
        if (latestPart < currentPart) {
            return false;
        }
    }

    return false;
}

/**
 * Check if an update is available for rxiv-maker.
 *
 * @param context Extension context for caching
 * @returns Version information
 */
export async function checkForUpdates(context: vscode.ExtensionContext): Promise<VersionInfo> {
    const config = vscode.workspace.getConfiguration('rxiv-maker');
    const checkEnabled = config.get<boolean>('checkForUpdates', true);

    if (!checkEnabled) {
        return {
            current: null,
            latest: null,
            updateAvailable: false
        };
    }

    // Check cache first
    const cacheKey = 'rxivMakerVersionCache';
    const cachedData = context.globalState.get<CacheData>(cacheKey);

    if (cachedData) {
        const lastCheck = new Date(cachedData.lastCheck);
        const now = new Date();
        const hoursSinceLastCheck = (now.getTime() - lastCheck.getTime()) / (1000 * 60 * 60);
        const checkInterval = config.get<number>('updateCheckInterval', 24);

        if (hoursSinceLastCheck < checkInterval) {
            // Use cached data
            return {
                current: cachedData.currentVersion,
                latest: cachedData.latestVersion,
                updateAvailable: cachedData.updateAvailable
            };
        }
    }

    // Perform fresh check
    const current = await getRxivMakerVersion();
    let latest: string | null = null;
    let updateAvailable = false;

    // Try Homebrew first if installed via Homebrew
    const installMethod = await detectInstallMethod();
    if (installMethod === 'homebrew') {
        const brewResult = await checkHomebrewOutdated();
        if (brewResult) {
            latest = brewResult.latest;
            updateAvailable = true;
        } else {
            // Not outdated according to Homebrew
            latest = current; // Assume current is latest
            updateAvailable = false;
        }
    } else {
        // Fall back to PyPI for all other methods
        latest = await fetchLatestVersion();
        updateAvailable = current && latest ? isNewerVersion(current, latest) : false;
    }

    // Cache the result
    const newCacheData: CacheData = {
        lastCheck: new Date().toISOString(),
        latestVersion: latest || '',
        currentVersion: current || '',
        updateAvailable
    };
    await context.globalState.update(cacheKey, newCacheData);

    return {
        current,
        latest,
        updateAvailable
    };
}

/**
 * Force a fresh update check, ignoring cache.
 *
 * @param context Extension context
 * @returns Version information
 */
export async function forceCheckForUpdates(context: vscode.ExtensionContext): Promise<VersionInfo> {
    // Clear cache
    await context.globalState.update('rxivMakerVersionCache', undefined);

    // Perform fresh check
    return checkForUpdates(context);
}
