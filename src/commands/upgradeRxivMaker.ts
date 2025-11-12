/**
 * Upgrade rxiv-maker command.
 *
 * Detects the installation method and runs the appropriate upgrade command.
 */

import * as vscode from 'vscode';
import {
    detectInstallMethod,
    getUpgradeCommand,
    getFriendlyInstallName,
    isRxivMakerInstalled
} from '../utils/installDetector';
import { getRxivMakerVersion, forceCheckForUpdates } from '../utils/versionChecker';

/**
 * Upgrade rxiv-maker to the latest version.
 *
 * @param context Extension context
 */
export async function upgradeRxivMakerCommand(context: vscode.ExtensionContext): Promise<void> {
    // Check if rxiv-maker is installed
    const installed = await isRxivMakerInstalled();

    if (!installed) {
        const install = await vscode.window.showErrorMessage(
            'rxiv-maker is not installed. Would you like to install it?',
            'Install',
            'Cancel'
        );

        if (install === 'Install') {
            // Trigger the install command
            vscode.commands.executeCommand('rxiv-maker.install');
        }
        return;
    }

    // Detect installation method
    const installMethod = await detectInstallMethod();
    const installName = getFriendlyInstallName(installMethod);

    // Handle development installations
    if (installMethod === 'dev') {
        await vscode.window.showWarningMessage(
            'Development installation detected. To update, pull the latest changes from git:\ncd <repo> && git pull && uv sync',
            { modal: true }
        );
        return;
    }

    // Check for updates
    await vscode.window.withProgress(
        {
            location: vscode.ProgressLocation.Notification,
            title: 'Checking for updates...',
            cancellable: false
        },
        async () => {
            const versionInfo = await forceCheckForUpdates(context);

            if (!versionInfo.updateAvailable) {
                vscode.window.showInformationMessage(
                    `✅ You already have the latest version (${versionInfo.current})`
                );
                return;
            }

            // Show update notification
            const upgradeCmd = getUpgradeCommand(installMethod);
            const message = `📦 Update available: rxiv-maker v${versionInfo.current} → v${versionInfo.latest}\n` +
                           `Installed via: ${installName}\n` +
                           `Upgrade command: ${upgradeCmd}`;

            const choice = await vscode.window.showInformationMessage(
                message,
                { modal: true },
                'Run Upgrade Command',
                'Copy to Clipboard',
                'Later'
            );

            if (choice === 'Run Upgrade Command') {
                // Open terminal and run upgrade command
                const terminal = vscode.window.createTerminal('rxiv-maker upgrade');
                terminal.show();
                terminal.sendText(upgradeCmd);
            } else if (choice === 'Copy to Clipboard') {
                await vscode.env.clipboard.writeText(upgradeCmd);
                vscode.window.showInformationMessage('Upgrade command copied to clipboard');
            }
        }
    );
}

/**
 * Show the status of rxiv-maker installation.
 *
 * @param context Extension context
 */
export async function showRxivMakerStatus(context: vscode.ExtensionContext): Promise<void> {
    // Check if installed
    const installed = await isRxivMakerInstalled();

    if (!installed) {
        vscode.window.showInformationMessage('❌ rxiv-maker is not installed');
        return;
    }

    // Get version and installation method
    const version = await getRxivMakerVersion();
    const installMethod = await detectInstallMethod();
    const installName = getFriendlyInstallName(installMethod);

    // Check for updates
    const versionInfo = await forceCheckForUpdates(context);

    let message = `rxiv-maker v${version}\n`;
    message += `Installed via: ${installName}\n`;

    if (versionInfo.updateAvailable) {
        message += `⚠️ Update available: v${versionInfo.latest}`;
    } else {
        message += `✅ Up to date`;
    }

    vscode.window.showInformationMessage(message);
}
