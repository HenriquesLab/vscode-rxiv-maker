import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import * as os from 'os';

interface BibEntry {
	key: string;
	type: string;
	title?: string;
	author?: string;
	year?: string;
}

interface ReferenceLabel {
	type: 'fig' | 'table' | 'eq' | 'snote';
	label: string;
	line: number;
	supplementary?: boolean;
}

interface ManuscriptFolderResult {
	success: boolean;
	manuscriptPath?: string;
	error?: string;
}

interface InstallationTool {
	name: string;
	command: string;
	available: boolean;
	description: string;
}

interface RxivInstallationResult {
	isInstalled: boolean;
	availableTools: InstallationTool[];
}

export function activate(context: vscode.ExtensionContext) {
	console.log('Rxiv-Maker extension is now active!');

	// Helper function to check if rxiv CLI is installed
	async function checkRxivInstalled(): Promise<boolean> {
		try {
			await new Promise<void>((resolve, reject) => {
				exec('rxiv --version', { timeout: 5000 }, (error, stdout, stderr) => {
					if (error) {
						reject(error);
					} else {
						resolve();
					}
				});
			});
			return true;
		} catch {
			// Check if rxiv exists in common uv tool locations but isn't in PATH
			const uvToolPath = path.join(os.homedir(), '.local', 'bin', 'rxiv');
			try {
				await fs.promises.access(uvToolPath, fs.constants.F_OK);
				// rxiv exists but not in PATH - this is a PATH configuration issue
				console.log('Rxiv-Maker: rxiv found at', uvToolPath, 'but not in PATH');
				return false;
			} catch {
				// rxiv truly not installed
				return false;
			}
		}
	}

	// Helper function to detect available installation tools
	async function checkInstallationTools(): Promise<InstallationTool[]> {
		const tools: InstallationTool[] = [
			{
				name: 'pipx',
				command: 'pipx --version',
				available: false,
				description: 'Recommended: Install in isolated environment with global CLI access'
			},
			{
				name: 'uv',
				command: 'uv --version',
				available: false,
				description: 'Fast modern Python package manager'
			},
			{
				name: 'pip',
				command: os.platform() === 'win32' ? 'pip --version' : 'pip3 --version',
				available: false,
				description: 'Standard Python package manager (may fail on managed systems like macOS)'
			}
		];

		for (const tool of tools) {
			try {
				await new Promise<void>((resolve, reject) => {
					exec(tool.command, { timeout: 5000 }, (error, stdout, stderr) => {
						if (error) {
							reject(error);
						} else {
							resolve();
						}
					});
				});
				tool.available = true;
			} catch {
				tool.available = false;
			}
		}

		return tools;
	}

	// Helper function to install rxiv-maker using selected method
	async function installRxivMaker(tool: InstallationTool): Promise<boolean> {
		return new Promise((resolve) => {
			const installTerminal = vscode.window.createTerminal({
				name: `rxiv-maker-install-${tool.name}`,
			});

			installTerminal.show();

			let installCommand: string;
			let fallbackMessage: string = '';

			switch (tool.name) {
				case 'pipx':
					installCommand = 'pipx install rxiv-maker';
					break;
				case 'uv':
					installCommand = 'uv tool install rxiv-maker && uv tool update-shell';
					break;
				case 'pip':
					installCommand = os.platform() === 'win32'
						? 'pip install rxiv-maker --user'
						: 'pip3 install rxiv-maker --user';

					// Add fallback guidance for pip on systems with externally-managed environments
					if (os.platform() !== 'win32') {
						fallbackMessage = `echo "If pip installation fails due to externally-managed-environment:"
echo "  1. Consider using 'pipx install rxiv-maker' instead (recommended)"
echo "  2. Or create a virtual environment first:"
echo "     python3 -m venv ~/.rxiv-env"
echo "     source ~/.rxiv-env/bin/activate"
echo "     pip install rxiv-maker"
echo ""`;
					}
					break;
				default:
					resolve(false);
					return;
			}

			installTerminal.sendText(`echo "Installing rxiv-maker using ${tool.name}..."`);

			if (tool.name === 'uv') {
				installTerminal.sendText(`echo "This will also configure your shell PATH automatically using 'uv tool update-shell'"`);
			}

			if (fallbackMessage) {
				installTerminal.sendText(fallbackMessage);
			}

			installTerminal.sendText(installCommand);

			// Add conditional success message and fallback for pip
			if (tool.name === 'pip') {
				installTerminal.sendText(`if [ $? -eq 0 ]; then
    echo "✅ Installation complete! You can now use rxiv commands."
    echo "Please restart VS Code to ensure the extension recognizes the new installation."
else
    echo "⚠️  Pip installation failed. This is common on macOS/Linux with managed Python environments."
    echo "🚀 Recommended: Install pipx and run 'pipx install rxiv-maker' instead"
    echo "Or follow the virtual environment instructions above."
fi`);
			} else if (tool.name === 'uv') {
				installTerminal.sendText(`echo "✅ Installation complete! rxiv-maker is now installed with PATH configured."`);
				installTerminal.sendText(`echo "Please restart your terminal or VS Code for PATH changes to take effect."`);
				installTerminal.sendText(`echo "If 'rxiv' command is still not found, run: hash -r"`);
			} else {
				installTerminal.sendText(`echo "✅ Installation complete! You can now use rxiv commands."`);
				installTerminal.sendText(`echo "Please restart VS Code to ensure the extension recognizes the new installation."`);
			}

			// We can't easily detect when the installation is complete from here,
			// so we'll assume success and let the user restart if needed
			setTimeout(() => resolve(true), 1000);
		});
	}

	// Helper function to check if rxiv exists but isn't in PATH
	async function checkRxivPATHIssue(): Promise<boolean> {
		const uvToolPath = path.join(os.homedir(), '.local', 'bin', 'rxiv');
		try {
			await fs.promises.access(uvToolPath, fs.constants.F_OK);
			return true; // rxiv exists but not in PATH
		} catch {
			return false; // rxiv doesn't exist
		}
	}

	// Helper function to ensure rxiv is available before running commands
	async function ensureRxivAvailable(): Promise<boolean> {
		const isInstalled = await checkRxivInstalled();

		if (isInstalled) {
			return true;
		}

		// Check if this is a PATH configuration issue
		const hasPATHIssue = await checkRxivPATHIssue();
		if (hasPATHIssue) {
			const choice = await vscode.window.showWarningMessage(
				'rxiv-maker is installed but not accessible from PATH. This commonly happens after uv tool install.',
				'Configure PATH',
				'Reinstall',
				'Cancel'
			);

			if (choice === 'Configure PATH') {
				const terminal = vscode.window.createTerminal({
					name: 'rxiv-path-config'
				});
				terminal.show();
				terminal.sendText('echo "Configuring PATH for rxiv-maker..."');
				terminal.sendText('uv tool update-shell');
				terminal.sendText('echo "PATH configuration complete. Please restart your terminal or run: hash -r"');

				vscode.window.showInformationMessage(
					'PATH configuration initiated. Please restart VS Code or your terminal, then try again.',
					'Restart VS Code'
				).then(choice => {
					if (choice === 'Restart VS Code') {
						vscode.commands.executeCommand('workbench.action.reloadWindow');
					}
				});
				return false;
			} else if (choice === 'Reinstall') {
				// Fall through to installation options
			} else {
				return false;
			}
		}

		// rxiv is not installed, offer installation options
		const availableTools = await checkInstallationTools();
		const availableOptions = availableTools.filter(tool => tool.available);

		if (availableOptions.length === 0) {
			vscode.window.showErrorMessage(
				'rxiv-maker CLI is not installed and no suitable installation tools (pipx, uv, pip) were found. Please install pipx or uv first.',
				'Show Instructions'
			).then(choice => {
				if (choice === 'Show Instructions') {
					const instructions = `To install rxiv-maker CLI, you need one of these tools:

**Recommended: pipx**
\`\`\`bash
# Install pipx first
${os.platform() === 'win32' ? 'pip install pipx' :
  os.platform() === 'darwin' ? 'brew install pipx' : 'sudo apt install pipx'}

# Then install rxiv-maker
pipx install rxiv-maker
\`\`\`

**Alternative: uv**
\`\`\`bash
# Install uv first
${os.platform() === 'win32' ? 'pip install uv' :
  os.platform() === 'darwin' ? 'brew install uv' : 'curl -LsSf https://astral.sh/uv/install.sh | sh'}

# Then install rxiv-maker and configure PATH
uv tool install rxiv-maker
uv tool update-shell

# Restart your terminal after installation
\`\`\``;

					vscode.workspace.openTextDocument({
						content: instructions,
						language: 'markdown'
					}).then(doc => vscode.window.showTextDocument(doc));
				}
			});
			return false;
		}

		// Show installation options to user
		const items = availableOptions.map(tool => ({
			label: `$(package) Install with ${tool.name}`,
			description: tool.description,
			tool: tool
		}));

		items.push({
			label: '$(x) Cancel',
			description: 'Cancel the operation',
			tool: null as any
		});

		const selected = await vscode.window.showQuickPick(items, {
			placeHolder: 'rxiv-maker CLI is not installed. Choose an installation method:',
			ignoreFocusOut: true
		});

		if (!selected || !selected.tool) {
			return false;
		}

		// Install using selected tool
		const success = await installRxivMaker(selected.tool);

		if (success) {
			vscode.window.showInformationMessage(
				`rxiv-maker installation initiated using ${selected.tool.name}. Please restart VS Code after installation completes.`,
				'Restart Now'
			).then(choice => {
				if (choice === 'Restart Now') {
					vscode.commands.executeCommand('workbench.action.reloadWindow');
				}
			});
		} else {
			vscode.window.showErrorMessage(`Failed to install rxiv-maker using ${selected.tool.name}`);
		}

		return success;
	}

	// Cached project detection
	const projectCache = new Map<string, boolean>();

	// Automatically detect and set language mode for rxiv-maker files
	const fileDetector = vscode.workspace.onDidOpenTextDocument(async (document) => {
		const fileName = path.basename(document.fileName);
		const isRxivFile = document.fileName.endsWith('.rxm') ||
			fileName === '01_MAIN.md' ||
			fileName === '02_SUPPLEMENTARY_INFO.md';

		if (isRxivFile) {
			const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
			if (workspaceFolder) {
				const workspacePath = workspaceFolder.uri.fsPath;
				let isRxivProject = projectCache.get(workspacePath);

				if (isRxivProject === undefined) {
					isRxivProject = await isRxivMakerProject(workspacePath);
					projectCache.set(workspacePath, isRxivProject);
				}

				if (isRxivProject) {
					await vscode.languages.setTextDocumentLanguage(document, 'rxiv-markdown');
				}
			}
		}
	});

	// Check already open documents (non-blocking)
	setTimeout(async () => {
		for (const document of vscode.workspace.textDocuments) {
			const fileName = path.basename(document.fileName);
			const isRxivFile = document.fileName.endsWith('.rxm') ||
				fileName === '01_MAIN.md' ||
				fileName === '02_SUPPLEMENTARY_INFO.md';

			if (isRxivFile) {
				const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
				if (workspaceFolder) {
					const workspacePath = workspaceFolder.uri.fsPath;
					let isRxivProject = projectCache.get(workspacePath);

					if (isRxivProject === undefined) {
						isRxivProject = await isRxivMakerProject(workspacePath);
						projectCache.set(workspacePath, isRxivProject);
					}

					if (isRxivProject) {
						await vscode.languages.setTextDocumentLanguage(document, 'rxiv-markdown');
					}
				}
			}
		}
	}, 500);

	// Register completion provider for citations
	const citationProvider = vscode.languages.registerCompletionItemProvider(
		{ language: 'rxiv-markdown' },
		new CitationCompletionProvider(),
		'@'
	);

	// Register completion provider for cross-references
	const referenceProvider = vscode.languages.registerCompletionItemProvider(
		{ language: 'rxiv-markdown' },
		new ReferenceCompletionProvider(),
		'@'
	);

	// Register commands
	const insertCitationCommand = vscode.commands.registerCommand('rxiv-maker.insertCitation', async () => {
		const bibEntries = await getBibEntries();
		if (bibEntries.length === 0) {
			// Build the same search paths as getBibEntries() to show user exactly where we looked
			const searchPaths: string[] = [];
			const activeEditor = vscode.window.activeTextEditor;

			if (activeEditor) {
				const currentDir = path.dirname(activeEditor.document.fileName);
				searchPaths.push(path.join(currentDir, '03_REFERENCES.bib'));
			}

			if (vscode.workspace.workspaceFolders) {
				for (const folder of vscode.workspace.workspaceFolders) {
					const workspaceBib = path.join(folder.uri.fsPath, '03_REFERENCES.bib');
					if (!searchPaths.includes(workspaceBib)) {
						searchPaths.push(workspaceBib);
					}
				}
			}

			const message = `No bibliography file (03_REFERENCES.bib) found.\n\nSearched in:\n${searchPaths.join('\n')}\n\nPlease create 03_REFERENCES.bib in the same directory as your document.`;
			vscode.window.showWarningMessage(message);
			return;
		}

		const items = bibEntries.map(entry => ({
			label: entry.key,
			description: entry.title || entry.type,
			detail: entry.author || ''
		}));

		const selected = await vscode.window.showQuickPick(items, {
			placeHolder: 'Select citation to insert'
		});

		if (selected) {
			const editor = vscode.window.activeTextEditor;
			if (editor) {
				const position = editor.selection.active;
				await editor.edit(editBuilder => {
					editBuilder.insert(position, `@${selected.label}`);
				});
			}
		}
	});

	const insertFigureReferenceCommand = vscode.commands.registerCommand('rxiv-maker.insertFigureReference', async () => {
		const references = await getDocumentReferences();
		const figureRefs = references.filter(ref => ref.type === 'fig');

		if (figureRefs.length === 0) {
			vscode.window.showWarningMessage('No figure labels found in the document');
			return;
		}

		const items = figureRefs.map(ref => ({
			label: ref.label,
			description: ref.supplementary ? 'Supplementary Figure' : 'Figure',
			detail: `Line ${ref.line + 1}`
		}));

		const selected = await vscode.window.showQuickPick(items, {
			placeHolder: 'Select figure reference to insert'
		});

		if (selected) {
			const editor = vscode.window.activeTextEditor;
			if (editor) {
				const position = editor.selection.active;
				const prefix = figureRefs.find(ref => ref.label === selected.label)?.supplementary ? '@sfig:' : '@fig:';
				await editor.edit(editBuilder => {
					editBuilder.insert(position, `${prefix}${selected.label}`);
				});
			}
		}
	});

	const insertTableReferenceCommand = vscode.commands.registerCommand('rxiv-maker.insertTableReference', async () => {
		const references = await getDocumentReferences();
		const tableRefs = references.filter(ref => ref.type === 'table');

		if (tableRefs.length === 0) {
			vscode.window.showWarningMessage('No table labels found in the document');
			return;
		}

		const items = tableRefs.map(ref => ({
			label: ref.label,
			description: ref.supplementary ? 'Supplementary Table' : 'Table',
			detail: `Line ${ref.line + 1}`
		}));

		const selected = await vscode.window.showQuickPick(items, {
			placeHolder: 'Select table reference to insert'
		});

		if (selected) {
			const editor = vscode.window.activeTextEditor;
			if (editor) {
				const position = editor.selection.active;
				const prefix = tableRefs.find(ref => ref.label === selected.label)?.supplementary ? '@stable:' : '@table:';
				await editor.edit(editBuilder => {
					editBuilder.insert(position, `${prefix}${selected.label}`);
				});
			}
		}
	});

	const insertEquationReferenceCommand = vscode.commands.registerCommand('rxiv-maker.insertEquationReference', async () => {
		const references = await getDocumentReferences();
		const equationRefs = references.filter(ref => ref.type === 'eq');

		if (equationRefs.length === 0) {
			vscode.window.showWarningMessage('No equation labels found in the document');
			return;
		}

		const items = equationRefs.map(ref => ({
			label: ref.label,
			description: 'Equation',
			detail: `Line ${ref.line + 1}`
		}));

		const selected = await vscode.window.showQuickPick(items, {
			placeHolder: 'Select equation reference to insert'
		});

		if (selected) {
			const editor = vscode.window.activeTextEditor;
			if (editor) {
				const position = editor.selection.active;
				await editor.edit(editBuilder => {
					editBuilder.insert(position, `@eq:${selected.label}`);
				});
			}
		}
	});

	// Shared terminal management
	let rxivMakerTerminal: vscode.Terminal | undefined;

	const getRxivMakerTerminal = (manuscriptDir: string): vscode.Terminal => {
		// Check if existing terminal is still alive
		if (rxivMakerTerminal && rxivMakerTerminal.exitStatus === undefined) {
			return rxivMakerTerminal;
		}

		// Create new terminal
		rxivMakerTerminal = vscode.window.createTerminal({
			name: 'rxiv-maker',
			cwd: manuscriptDir
		});

		// Clean up reference when terminal is closed
		vscode.window.onDidCloseTerminal((terminal) => {
			if (terminal === rxivMakerTerminal) {
				rxivMakerTerminal = undefined;
			}
		});

		return rxivMakerTerminal;
	};

	const makeValidateCommand = vscode.commands.registerCommand('rxiv-maker.makeValidate', async () => {
		// Check if rxiv is available before proceeding
		const rxivAvailable = await ensureRxivAvailable();
		if (!rxivAvailable) {
			return;
		}

		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv validate "${result.manuscriptPath}"`);
	});

	const makePdfCommand = vscode.commands.registerCommand('rxiv-maker.makePdf', async () => {
		// Check if rxiv is available before proceeding
		const rxivAvailable = await ensureRxivAvailable();
		if (!rxivAvailable) {
			return;
		}

		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv pdf "${result.manuscriptPath}"`);
	});

	const makeCleanCommand = vscode.commands.registerCommand('rxiv-maker.makeClean', async () => {
		// Check if rxiv is available before proceeding
		const rxivAvailable = await ensureRxivAvailable();
		if (!rxivAvailable) {
			return;
		}

		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv clean "${result.manuscriptPath}"`);
	});

	const installRxivMakerCommand = vscode.commands.registerCommand('rxiv-maker.installRxivMaker', async () => {
		// Show progress while checking installation status
		await vscode.window.withProgress({
			location: vscode.ProgressLocation.Notification,
			title: "Checking rxiv-maker installation...",
			cancellable: false
		}, async (progress) => {
			progress.report({ increment: 30, message: 'Checking if rxiv-maker is already installed...' });

			// First check if rxiv-maker is already installed
			const isInstalled = await checkRxivInstalled();
			if (isInstalled) {
				const choice = await vscode.window.showInformationMessage(
					'rxiv-maker CLI is already installed on your system.',
					'Show Version Info',
					'Reinstall Anyway',
					'Cancel'
				);

				if (choice === 'Show Version Info') {
					const terminal = vscode.window.createTerminal({
						name: 'rxiv-maker-info'
					});
					terminal.show();
					terminal.sendText('rxiv --version');
					terminal.sendText('echo "rxiv-maker is ready to use!"');
					return;
				} else if (choice !== 'Reinstall Anyway') {
					return;
				}
			}

			progress.report({ increment: 30, message: 'Checking available installation methods...' });

			// Check for available installation tools
			const availableTools = await checkInstallationTools();
			const availableOptions = availableTools.filter(tool => tool.available);

			if (availableOptions.length === 0) {
				// No modern tools available, fall back to repository installation
				progress.report({ increment: 40, message: 'No package managers found, checking system dependencies...' });

				// Check system dependencies for repository-based installation
				const dependencies = [
					{ name: 'git', command: 'git --version' },
					{ name: 'make', command: 'make --version' },
					{ name: 'python', command: os.platform() === 'win32' ? 'python --version' : 'python3 --version' }
				];

				const missingDeps: string[] = [];
				for (const dep of dependencies) {
					try {
						await new Promise<void>((resolve, reject) => {
							exec(dep.command, { timeout: 5000 }, (error, stdout, stderr) => {
								if (error) {
									reject(error);
								} else {
									resolve();
								}
							});
						});
					} catch {
						missingDeps.push(dep.name);
					}
				}

				if (missingDeps.length > 0) {
					const installInstructions = {
						git: 'Install Git from https://git-scm.com/',
						make: os.platform() === 'win32'
							? 'Install Visual Studio Build Tools or Git Bash'
							: os.platform() === 'darwin'
							? 'Run: xcode-select --install'
							: 'Run: sudo apt install build-essential',
						python: 'Install Python from https://python.org/'
					};

					const message = `To install rxiv-maker, you need these tools:\n\nMissing dependencies: ${missingDeps.join(', ')}\n\nInstallation instructions:\n${missingDeps.map(dep => `• ${dep}: ${installInstructions[dep as keyof typeof installInstructions]}`).join('\n')}\n\n**Recommended**: Install pipx or uv for easier rxiv-maker installation:\n• pipx: ${os.platform() === 'darwin' ? 'brew install pipx' : 'pip install pipx'}\n• uv: ${os.platform() === 'darwin' ? 'brew install uv' : 'curl -LsSf https://astral.sh/uv/install.sh | sh'}`;

					const choice = await vscode.window.showErrorMessage(
						`Missing dependencies for rxiv-maker installation: ${missingDeps.join(', ')}`,
						'Show Instructions',
						'Cancel'
					);

					if (choice === 'Show Instructions') {
						const doc = await vscode.workspace.openTextDocument({
							content: message,
							language: 'markdown'
						});
						await vscode.window.showTextDocument(doc);
					}
					return;
				}

				// Proceed with repository-based installation
				const choice = await vscode.window.showInformationMessage(
					'No modern package managers (pipx, uv) found. Install rxiv-maker from source repository?',
					{ modal: true },
					'Yes, install from repository',
					'Cancel'
				);

				if (choice !== 'Yes, install from repository') {
					return;
				}

				// Show directory selection for repository installation
				const installDir = await vscode.window.showInputBox({
					prompt: 'Enter directory where to clone rxiv-maker repository',
					value: path.join(os.homedir(), 'Documents', 'GitHub'),
					validateInput: (value) => {
						if (!value) {
							return 'Installation directory is required';
						}
						return undefined;
					}
				});

				if (!installDir) {
					return;
				}

				// Repository installation
				try {
					await fs.promises.mkdir(installDir, { recursive: true });
				} catch (error) {
					vscode.window.showErrorMessage(`Failed to create installation directory: ${installDir}\n${error}`);
					return;
				}

				const installTerminal = vscode.window.createTerminal({
					name: 'rxiv-maker-repo-install',
					cwd: installDir
				});

				installTerminal.show();
				installTerminal.sendText('echo "Installing rxiv-maker from repository..."');
				installTerminal.sendText('git clone https://github.com/HenriquesLab/rxiv-maker.git');
				installTerminal.sendText('cd rxiv-maker');
				installTerminal.sendText('make setup');
				installTerminal.sendText('echo "Repository installation complete! The CLI may not be globally available."');
				installTerminal.sendText('echo "Consider installing pipx or uv for global CLI access."');

				return;
			}

			// Modern installation options available
			progress.report({ increment: 40, message: 'Preparing installation options...' });

			// Add repository option as fallback
			const allOptions = [...availableOptions, {
				name: 'repository',
				command: '',
				available: true,
				description: 'Install from source repository (advanced users)'
			}];

			// Show installation method selection
			const items = allOptions.map(tool => ({
				label: tool.name === 'repository' ? '$(repo) Install from repository' : `$(package) Install with ${tool.name}`,
				description: tool.description,
				tool: tool
			}));

			items.push({
				label: '$(x) Cancel',
				description: 'Cancel installation',
				tool: null as any
			});

			const selected = await vscode.window.showQuickPick(items, {
				placeHolder: 'Choose installation method for rxiv-maker:',
				ignoreFocusOut: true
			});

			if (!selected || !selected.tool) {
				return;
			}

			if (selected.tool.name === 'repository') {
				// Handle repository installation (similar to old logic but simplified)
				const installDir = await vscode.window.showInputBox({
					prompt: 'Enter directory where to clone rxiv-maker repository',
					value: path.join(os.homedir(), 'Documents', 'GitHub'),
					validateInput: (value) => {
						if (!value) {
							return 'Installation directory is required';
						}
						return undefined;
					}
				});

				if (!installDir) {
					return;
				}

				try {
					await fs.promises.mkdir(installDir, { recursive: true });
				} catch (error) {
					vscode.window.showErrorMessage(`Failed to create installation directory: ${installDir}\n${error}`);
					return;
				}

				const installTerminal = vscode.window.createTerminal({
					name: 'rxiv-maker-repo-install',
					cwd: installDir
				});

				installTerminal.show();
				installTerminal.sendText('echo "Installing rxiv-maker from repository..."');
				installTerminal.sendText('git clone https://github.com/HenriquesLab/rxiv-maker.git');
				installTerminal.sendText('cd rxiv-maker');
				installTerminal.sendText('make setup');
				installTerminal.sendText('echo "Repository installation complete!"');
			} else {
				// Install using selected modern tool
				const success = await installRxivMaker(selected.tool);

				if (success) {
					vscode.window.showInformationMessage(
						`rxiv-maker installation initiated using ${selected.tool.name}. Please restart VS Code after installation completes.`,
						'Restart Now'
					).then(choice => {
						if (choice === 'Restart Now') {
							vscode.commands.executeCommand('workbench.action.reloadWindow');
						}
					});
				} else {
					vscode.window.showErrorMessage(`Failed to install rxiv-maker using ${selected.tool.name}`);
				}
			}
		});
	});

	const makeAddBibliographyCommand = vscode.commands.registerCommand('rxiv-maker.makeAddBibliography', async () => {
		// Check if rxiv is available before proceeding
		const rxivAvailable = await ensureRxivAvailable();
		if (!rxivAvailable) {
			return;
		}

		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		// Prompt user for DOI
		const doi = await vscode.window.showInputBox({
			prompt: 'Enter DOI to add to bibliography',
			placeHolder: 'e.g., 10.1000/example or https://doi.org/10.1000/example',
			validateInput: (value) => {
				if (!value) {
					return 'DOI is required';
				}
				// Basic DOI validation - should start with 10. or be a full DOI URL
				const doiPattern = /^(https?:\/\/)?(dx\.)?doi\.org\/10\.|^10\./;
				if (!doiPattern.test(value)) {
					return 'Please enter a valid DOI (e.g., 10.1000/example)';
				}
				return undefined;
			}
		});

		if (!doi) {
			return; // User cancelled
		}

		// Clean up DOI - remove URL parts if present
		const cleanDoi = doi.replace(/^(https?:\/\/)?(dx\.)?doi\.org\//, '');

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv bibliography add "${result.manuscriptPath}" ${cleanDoi}`);
	});

	context.subscriptions.push(
		fileDetector,
		citationProvider,
		referenceProvider,
		insertCitationCommand,
		insertFigureReferenceCommand,
		insertTableReferenceCommand,
		insertEquationReferenceCommand,
		installRxivMakerCommand,
		makeValidateCommand,
		makePdfCommand,
		makeCleanCommand,
		makeAddBibliographyCommand
	);
}

class CitationCompletionProvider implements vscode.CompletionItemProvider {
	async provideCompletionItems(
		document: vscode.TextDocument,
		position: vscode.Position,
		token: vscode.CancellationToken,
		context: vscode.CompletionContext
	): Promise<vscode.CompletionItem[]> {
		const lineText = document.lineAt(position).text;
		const beforeCursor = lineText.substring(0, position.character);

		// Check for @ at cursor position or after [ for citations like [@citation]
		if (!beforeCursor.endsWith('@') && !beforeCursor.match(/\[@$/)) {
			return [];
		}

		const bibEntries = await getBibEntries();
		return bibEntries.map(entry => {
			const item = new vscode.CompletionItem(entry.key, vscode.CompletionItemKind.Reference);
			item.detail = entry.title || entry.type;
			item.documentation = new vscode.MarkdownString(`**${entry.type}**\n\n${entry.author || ''}\n\n${entry.year || ''}`);
			item.insertText = entry.key;
			return item;
		});
	}
}

class ReferenceCompletionProvider implements vscode.CompletionItemProvider {
	async provideCompletionItems(
		document: vscode.TextDocument,
		position: vscode.Position,
		token: vscode.CancellationToken,
		context: vscode.CompletionContext
	): Promise<vscode.CompletionItem[]> {
		const lineText = document.lineAt(position).text;
		const beforeCursor = lineText.substring(0, position.character);

		// Only provide reference completions for specific patterns, not general citations
		if (!beforeCursor.match(/@s?fig:$|@s?table:$|@eq:$|@snote:$/)) {
			return [];
		}

		const references = await getDocumentReferences();
		const referenceType = beforeCursor.match(/@(s?)(fig|table|eq|snote):$/)?.[2] as 'fig' | 'table' | 'eq' | 'snote';
		const isSupplementary = beforeCursor.includes('@s');

		if (!referenceType) {
			return [];
		}

		const filteredRefs = references.filter(ref =>
			ref.type === referenceType &&
			(isSupplementary ? ref.supplementary : !ref.supplementary)
		);

		return filteredRefs.map(ref => {
			const item = new vscode.CompletionItem(ref.label, vscode.CompletionItemKind.Reference);
			item.detail = `${ref.supplementary ? 'Supplementary ' : ''}${ref.type}`;
			item.documentation = new vscode.MarkdownString(`Line ${ref.line + 1}`);
			item.insertText = ref.label;
			return item;
		});
	}
}

async function getBibEntries(): Promise<BibEntry[]> {
	// Try to find bibliography file in multiple locations
	const searchPaths: string[] = [];

	// 1. Try current document's directory first (highest priority)
	const activeEditor = vscode.window.activeTextEditor;
	if (activeEditor) {
		const currentDir = path.dirname(activeEditor.document.fileName);
		const currentDirBib = path.join(currentDir, '03_REFERENCES.bib');
		searchPaths.push(currentDirBib);
		console.log('Rxiv-Maker: Searching for bibliography in current document directory:', currentDirBib);
	}

	// 2. Try workspace folders as fallback
	if (vscode.workspace.workspaceFolders) {
		for (const folder of vscode.workspace.workspaceFolders) {
			const workspaceBib = path.join(folder.uri.fsPath, '03_REFERENCES.bib');
			// Avoid duplicates
			if (!searchPaths.includes(workspaceBib)) {
				searchPaths.push(workspaceBib);
				console.log('Rxiv-Maker: Searching for bibliography in workspace folder:', workspaceBib);
			}
		}
	}

	// Find the first existing bibliography file
	let bibPath: string | null = null;
	for (const searchPath of searchPaths) {
		try {
			await fs.promises.access(searchPath, fs.constants.F_OK | fs.constants.R_OK);
			bibPath = searchPath;
			console.log('Rxiv-Maker: Found bibliography file at:', bibPath);
			break;
		} catch (error) {
			console.log('Rxiv-Maker: Bibliography not found at:', searchPath);
			// Continue searching
		}
	}

	if (!bibPath) {
		console.log('Rxiv-Maker: No bibliography file found in any search location');
		return [];
	}

	try {
		const content = await fs.promises.readFile(bibPath, 'utf8');
		const entries: BibEntry[] = [];

		const entryRegex = /@(\w+)\s*\{\s*([^,\s]+)\s*,/g;
		let match;

		while ((match = entryRegex.exec(content)) !== null) {
			const type = match[1];
			const key = match[2];

			const entryStart = match.index;
			const entryEnd = findMatchingBrace(content, entryStart);
			const entryContent = content.substring(entryStart, entryEnd);

			const titleMatch = entryContent.match(/title\s*=\s*[{"](.*?)["}]/);
			const authorMatch = entryContent.match(/author\s*=\s*[{"](.*?)["}]/);
			const yearMatch = entryContent.match(/year\s*=\s*[{"](.*?)["}]/);

			entries.push({
				key,
				type,
				title: titleMatch?.[1],
				author: authorMatch?.[1],
				year: yearMatch?.[1]
			});
		}

		return entries;
	} catch (error) {
		// Silently handle missing bibliography file - this is normal for non-rxiv-maker projects
		if ((error as any).code === 'ENOENT') {
			return [];
		}
		console.error('Error parsing bibliography:', error);
		return [];
	}
}

async function getDocumentReferences(): Promise<ReferenceLabel[]> {
	const references: ReferenceLabel[] = [];

	// Get search paths for manuscript files
	const searchPaths: string[] = [];

	// 1. Try current document's directory first (highest priority)
	const activeEditor = vscode.window.activeTextEditor;
	if (activeEditor) {
		const currentDir = path.dirname(activeEditor.document.fileName);
		searchPaths.push(path.join(currentDir, '01_MAIN.md'));
		searchPaths.push(path.join(currentDir, '02_SUPPLEMENTARY_INFO.md'));
	}

	// 2. Try workspace folders as fallback
	if (vscode.workspace.workspaceFolders) {
		for (const folder of vscode.workspace.workspaceFolders) {
			const workspaceMain = path.join(folder.uri.fsPath, '01_MAIN.md');
			const workspaceSupp = path.join(folder.uri.fsPath, '02_SUPPLEMENTARY_INFO.md');

			if (!searchPaths.includes(workspaceMain)) {
				searchPaths.push(workspaceMain);
			}
			if (!searchPaths.includes(workspaceSupp)) {
				searchPaths.push(workspaceSupp);
			}
		}
	}

	// Search for references in each file
	for (const filePath of searchPaths) {
		try {
			const content = await fs.promises.readFile(filePath, 'utf8');
			const lines = content.split('\n');
			const isSupplementary = filePath.includes('02_SUPPLEMENTARY_INFO');

			for (let i = 0; i < lines.length; i++) {
				const text = lines[i];
				const labelRegex = /\{#(s?)((fig|table|eq|snote)):([a-zA-Z0-9_-]+)(?:\s[^}]*)?\}/g;
				let match;

				while ((match = labelRegex.exec(text)) !== null) {
					const supplementary = match[1] === 's' || isSupplementary;
					const type = match[2] as 'fig' | 'table' | 'eq' | 'snote';
					const label = match[4];

					references.push({
						type,
						label,
						line: i,
						supplementary
					});
				}
			}
		} catch (error) {
			// File doesn't exist or can't be read, continue with next file
			continue;
		}
	}

	return references;
}

function findMatchingBrace(content: string, start: number): number {
	let braceCount = 0;
	let inString = false;
	let stringChar = '';

	for (let i = start; i < content.length; i++) {
		const char = content[i];

		if (inString) {
			if (char === stringChar && content[i - 1] !== '\\') {
				inString = false;
			}
		} else {
			if (char === '"' || char === "'") {
				inString = true;
				stringChar = char;
			} else if (char === '{') {
				braceCount++;
			} else if (char === '}') {
				braceCount--;
				if (braceCount === 0) {
					return i + 1;
				}
			}
		}
	}

	return content.length;
}

async function isRxivMakerProject(workspacePath: string): Promise<boolean> {
	try {
		const requiredFiles = ['00_CONFIG.yml', '01_MAIN.rxm', '01_MAIN.md', '03_REFERENCES.bib'];
		const optionalFiles = ['02_SUPPLEMENTARY_INFO.rxm', '02_SUPPLEMENTARY_INFO.md'];

		const detectedFiles = await Promise.all(
			requiredFiles.map(async (file) => {
				try {
					await fs.promises.access(path.join(workspacePath, file));
					return true;
				} catch {
					return false;
				}
			})
		);

		const foundCount = detectedFiles.filter(Boolean).length;
		// Consider it an rxiv-maker project if at least 2 out of 4 required files are present
		// This accounts for either .rxm or .md versions of main files
		return foundCount >= 2;
	} catch (error) {
		console.error('Error checking rxiv-maker project:', error);
		return false;
	}
}

async function findManuscriptFolder(): Promise<ManuscriptFolderResult> {
	// Get current active document
	const activeEditor = vscode.window.activeTextEditor;
	if (!activeEditor) {
		return {
			success: false,
			error: 'No active document. Please open a file in your manuscript folder.'
		};
	}

	const currentFile = activeEditor.document.fileName;
	const currentDir = path.dirname(currentFile);

	// Check if current directory contains manuscript files
	const manuscriptFiles = ['00_CONFIG.yml', '01_MAIN.md', '01_MAIN.rxm', '03_REFERENCES.bib'];
	const hasManuscriptFiles = await Promise.all(
		manuscriptFiles.map(async (file) => {
			try {
				await fs.promises.access(path.join(currentDir, file));
				return true;
			} catch {
				return false;
			}
		})
	);

	let manuscriptPath: string;
	if (hasManuscriptFiles.some(exists => exists)) {
		// Current directory is a manuscript folder
		manuscriptPath = currentDir;
	} else {
		// Try to find manuscript folder in workspace
		const workspaceFolders = vscode.workspace.workspaceFolders;
		if (!workspaceFolders) {
			return {
				success: false,
				error: 'No workspace folder found. Please open the manuscript folder in VS Code.'
			};
		}

		// Look for manuscript folders in workspace
		let foundManuscriptPath: string | null = null;
		for (const folder of workspaceFolders) {
			const folderPath = folder.uri.fsPath;
			const hasFiles = await Promise.all(
				manuscriptFiles.map(async (file) => {
					try {
						await fs.promises.access(path.join(folderPath, file));
						return true;
					} catch {
						return false;
					}
				})
			);

			if (hasFiles.some(exists => exists)) {
				foundManuscriptPath = folderPath;
				break;
			}
		}

		if (!foundManuscriptPath) {
			return {
				success: false,
				error: 'No manuscript folder found. Please ensure your workspace contains a folder with rxiv-maker files (00_CONFIG.yml, 01_MAIN.md, etc.)'
			};
		}

		manuscriptPath = foundManuscriptPath;
	}

	return {
		success: true,
		manuscriptPath: manuscriptPath
	};
}

export function deactivate() {}
