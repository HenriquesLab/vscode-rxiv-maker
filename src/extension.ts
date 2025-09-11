import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import * as os from 'os';
import { RxivMarkdownDiagnosticsProvider } from './diagnostics';

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

export function activate(context: vscode.ExtensionContext) {
	console.log('Rxiv-Maker extension is now active!');

	// Initialize diagnostic provider for linting
	const diagnosticsProvider = new RxivMarkdownDiagnosticsProvider();
	context.subscriptions.push(diagnosticsProvider);

	// Cached project detection
	const projectCache = new Map<string, boolean>();

	// Status bar button for PDF generation
	let pdfStatusBarItem: vscode.StatusBarItem;

	// Function to create and update status bar item
	const createStatusBarItem = () => {
		if (pdfStatusBarItem) {
			pdfStatusBarItem.dispose();
		}
		
		const config = vscode.workspace.getConfiguration('rxiv-maker');
		if (!config.get('showStatusBarButton', true)) {
			return;
		}

		pdfStatusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
		pdfStatusBarItem.command = 'rxiv-maker.makePdf';
		pdfStatusBarItem.text = '$(file-pdf) PDF';
		pdfStatusBarItem.tooltip = 'Build PDF with rxiv-maker';
		context.subscriptions.push(pdfStatusBarItem);
	};

	// Function to update status bar visibility based on current file
	const updateStatusBarVisibility = async (document?: vscode.TextDocument) => {
		if (!pdfStatusBarItem) {
			return;
		}

		if (!document) {
			document = vscode.window.activeTextEditor?.document;
		}

		if (!document) {
			pdfStatusBarItem.hide();
			return;
		}

		const fileName = path.basename(document.fileName);
		const isRxivFile = document.fileName.endsWith('.rxm') ||
			fileName === '01_MAIN.md' ||
			fileName === '02_SUPPLEMENTARY_INFO.md' ||
			document.languageId === 'rxiv-markdown';

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
					pdfStatusBarItem.show();
				} else {
					pdfStatusBarItem.hide();
				}
			} else {
				pdfStatusBarItem.hide();
			}
		} else {
			pdfStatusBarItem.hide();
		}
	};

	// Create status bar item
	createStatusBarItem();

	// Update visibility when active editor changes
	vscode.window.onDidChangeActiveTextEditor((editor) => {
		updateStatusBarVisibility(editor?.document);
	}, null, context.subscriptions);

	// Update visibility when document is opened
	vscode.workspace.onDidOpenTextDocument(updateStatusBarVisibility, null, context.subscriptions);

	// Update visibility when configuration changes
	vscode.workspace.onDidChangeConfiguration((e) => {
		if (e.affectsConfiguration('rxiv-maker.showStatusBarButton')) {
			createStatusBarItem();
			updateStatusBarVisibility();
		}
	}, null, context.subscriptions);

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
					// Trigger validation for the newly detected document
					await diagnosticsProvider.validateDocument(document);
					// Update status bar visibility
					await updateStatusBarVisibility(document);
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
						// Trigger validation for already open documents
						await diagnosticsProvider.validateDocument(document);
						// Update status bar visibility
						await updateStatusBarVisibility(document);
					}
				}
			}
		}
	}, 500);

	// Register completion provider for citations
	const citationProvider = vscode.languages.registerCompletionItemProvider(
		{ language: 'rxiv-markdown' },
		{
			async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {
				const linePrefix = document.lineAt(position).text.substr(0, position.character);
				if (!linePrefix.endsWith('@')) {
					return [];
				}

				const bibEntries = await getBibEntries();
				return bibEntries.map(entry => {
					const item = new vscode.CompletionItem(entry.key, vscode.CompletionItemKind.Reference);
					item.detail = entry.title || entry.type;
					item.documentation = entry.author || '';
					item.insertText = entry.key;
					return item;
				});
			}
		},
		'@'
	);

	// Register completion provider for cross-references
	const referenceProvider = vscode.languages.registerCompletionItemProvider(
		{ language: 'rxiv-markdown' },
		{
			async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position) {
				const linePrefix = document.lineAt(position).text.substr(0, position.character);
				if (!linePrefix.endsWith('@')) {
					return [];
				}

				const references = await getDocumentReferences();
				return references.map(ref => {
					const prefix = ref.supplementary ? `s${ref.type}:` : `${ref.type}:`;
					const item = new vscode.CompletionItem(`${prefix}${ref.label}`, vscode.CompletionItemKind.Reference);
					item.detail = `${ref.type.toUpperCase()} reference`;
					item.documentation = `Line ${ref.line + 1}${ref.supplementary ? ' (Supplementary)' : ''}`;
					item.insertText = `${prefix}${ref.label}`;
					return item;
				});
			}
		},
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

	const getRxivMakerTerminal = (cwd: string): vscode.Terminal => {
		// Check if existing terminal is still alive
		if (rxivMakerTerminal && rxivMakerTerminal.exitStatus === undefined) {
			return rxivMakerTerminal;
		}

		// Create new terminal
		rxivMakerTerminal = vscode.window.createTerminal({
			name: 'rxiv-maker',
			cwd: cwd
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
		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv validate .`);
	});

	const makePdfCommand = vscode.commands.registerCommand('rxiv-maker.makePdf', async () => {
		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv pdf .`);
	});

	const makeCleanCommand = vscode.commands.registerCommand('rxiv-maker.makeClean', async () => {
		const result = await findManuscriptFolder();
		if (!result.success || !result.manuscriptPath) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.manuscriptPath);
		terminal.show();
		terminal.sendText(`rxiv clean .`);
	});

	const installRxivMakerCommand = vscode.commands.registerCommand('rxiv-maker.installRxivMaker', async () => {
		// Check if pipx is available first
		await vscode.window.withProgress({
			location: vscode.ProgressLocation.Notification,
			title: "Checking installation prerequisites...",
			cancellable: false
		}, async (progress) => {
			progress.report({
				increment: 50,
				message: 'Checking pipx availability...'
			});

			// Check for pipx
			let hasPipx = false;
			try {
				await new Promise<void>((resolve, reject) => {
					exec('pipx --version', { timeout: 5000 }, (error, stdout, stderr) => {
						if (!error) {
							hasPipx = true;
						}
						resolve();
					});
				});
			} catch {
				// pipx not available
			}

			if (!hasPipx) {
				const installPipx = await vscode.window.showWarningMessage(
					'pipx is required to install rxiv-maker. Would you like to see installation instructions?',
					{ modal: true },
					'Show Installation Instructions',
					'Cancel'
				);

				if (installPipx === 'Show Installation Instructions') {
					const instructions = `# Install pipx (Python Package Manager)\n\n` +
						`## macOS:\n\`\`\`bash\nbrew install pipx\n\`\`\`\n\n` +
						`## Linux (Ubuntu/Debian):\n\`\`\`bash\nsudo apt update\nsudo apt install pipx\n\`\`\`\n\n` +
						`## Linux (Other):\n\`\`\`bash\npython3 -m pip install --user pipx\npython3 -m pipx ensurepath\n\`\`\`\n\n` +
						`## Windows:\n\`\`\`powershell\npip install --user pipx\n\`\`\`\n\n` +
						`After installing pipx, restart VS Code and try again.`;

					const doc = await vscode.workspace.openTextDocument({
						content: instructions,
						language: 'markdown'
					});
					await vscode.window.showTextDocument(doc);
				}
				return;
			}

			// pipx is available, proceed with installation
			const choice = await vscode.window.showInformationMessage(
				'Install rxiv-maker using pipx? This will install rxiv-maker globally and make it available from any terminal.',
				{ modal: true },
				'Yes, install rxiv-maker',
				'No, cancel'
			);

			if (choice !== 'Yes, install rxiv-maker') {
				return;
			}

			// Create installation terminal
			const installTerminal = vscode.window.createTerminal({
				name: 'rxiv-maker-install'
			});

			installTerminal.show();

			// Simple pipx installation
			installTerminal.sendText('echo "Installing rxiv-maker with pipx..."');
			installTerminal.sendText('pipx install rxiv-maker');
			installTerminal.sendText('echo "Installation complete! You can now use rxiv commands."');
			installTerminal.sendText('rxiv --version');
		});
	});

	const makeAddBibliographyCommand = vscode.commands.registerCommand('rxiv-maker.makeAddBibliography', async () => {
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
		terminal.sendText(`rxiv bibliography add --manuscript-path . ${cleanDoi}`);
	});

	// New custom command insertions
	const insertBlindtextCommand = vscode.commands.registerCommand('rxiv-maker.insertBlindtext', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			await editor.edit(editBuilder => {
				editBuilder.insert(position, '{{blindtext}}');
			});
		}
	});

	const insertBlindtextParagraphCommand = vscode.commands.registerCommand('rxiv-maker.insertBlindtextParagraph', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			await editor.edit(editBuilder => {
				editBuilder.insert(position, '{{Blindtext}}');
			});
		}
	});

	const insertPythonBlockCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonBlock', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const selection = editor.selection;
			
			if (selection.isEmpty) {
				// Insert template with cursor placeholder
				const snippet = new vscode.SnippetString('{{py:\n$1\n}}');
				await editor.insertSnippet(snippet, position);
			} else {
				// Wrap selected code in Python block
				const selectedText = editor.document.getText(selection);
				await editor.edit(editBuilder => {
					editBuilder.replace(selection, `{{py:\n${selectedText}\n}}`);
				});
			}
		}
	});

	const insertPythonInlineCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonInline', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const selection = editor.selection;
			
			if (selection.isEmpty) {
				// Insert template with cursor placeholder
				const snippet = new vscode.SnippetString('{py: $1}');
				await editor.insertSnippet(snippet, position);
			} else {
				// Wrap selected code in inline Python
				const selectedText = editor.document.getText(selection);
				await editor.edit(editBuilder => {
					editBuilder.replace(selection, `{py: ${selectedText}}`);
				});
			}
		}
	});

	// New Python inline code commands
	const insertPythonImportCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonImport', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			
			// Show common modules as suggestions
			const commonModules = [
				{ label: 'datetime', detail: 'Date and time operations' },
				{ label: 'math', detail: 'Mathematical functions' },
				{ label: 'statistics', detail: 'Statistical functions' },
				{ label: 'json', detail: 'JSON encoder/decoder' },
				{ label: 'csv', detail: 'CSV file reading/writing' },
				{ label: 'random', detail: 'Generate random numbers' },
				{ label: 'collections', detail: 'Specialized container datatypes' },
				{ label: 'itertools', detail: 'Iterator building blocks' },
				{ label: 'functools', detail: 'Higher-order functions and operations on functions' }
			];

			const selected = await vscode.window.showQuickPick(commonModules, {
				placeHolder: 'Select a module to import (or type a custom module name)'
			});

			if (selected) {
				const snippet = new vscode.SnippetString(`{py:import ${selected.label}}`);
				await editor.insertSnippet(snippet, position);
			} else {
				// Allow custom module input
				const customModule = await vscode.window.showInputBox({
					prompt: 'Enter module name to import',
					placeHolder: 'e.g., datetime'
				});
				
				if (customModule) {
					const snippet = new vscode.SnippetString(`{py:import ${customModule}}`);
					await editor.insertSnippet(snippet, position);
				}
			}
		}
	});

	const insertPythonFromImportCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonFromImport', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const snippet = new vscode.SnippetString('{py:from ${1:module} import ${2:item}}');
			await editor.insertSnippet(snippet, position);
		}
	});

	const insertPythonSetCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonSet', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const snippet = new vscode.SnippetString('{py:set ${1:variable_name} = ${2:"value"}}');
			await editor.insertSnippet(snippet, position);
		}
	});

	const insertPythonGetCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonGet', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const snippet = new vscode.SnippetString('{py:get ${1:variable_name}}');
			await editor.insertSnippet(snippet, position);
		}
	});

	const insertPythonContextCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonContext', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const snippet = new vscode.SnippetString('{py:context="${1:context_name}" ${2:code}}');
			await editor.insertSnippet(snippet, position);
		}
	});

	const insertPythonFormatCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonFormat', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			
			// Show common format types as suggestions
			const formatTypes = [
				{ label: 'number,2', detail: 'Format number with 2 decimal places' },
				{ label: 'percentage,1', detail: 'Format as percentage with 1 decimal place' },
				{ label: 'currency', detail: 'Format as currency' },
				{ label: 'scientific,3', detail: 'Format in scientific notation with 3 decimal places' },
				{ label: 'date,%Y-%m-%d', detail: 'Format date as YYYY-MM-DD' },
				{ label: 'date,%B %d, %Y', detail: 'Format date as "Month DD, YYYY"' },
				{ label: 'comma', detail: 'Add thousand separators' }
			];

			const selected = await vscode.window.showQuickPick(formatTypes, {
				placeHolder: 'Select a format specification'
			});

			if (selected) {
				const snippet = new vscode.SnippetString(`{py:format="${selected.label}" \${1:expression}}`);
				await editor.insertSnippet(snippet, position);
			} else {
				// Allow custom format input
				const snippet = new vscode.SnippetString('{py:format="${1:format_spec}" ${2:expression}}');
				await editor.insertSnippet(snippet, position);
			}
		}
	});

	const insertPythonGlobalCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonGlobal', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const snippet = new vscode.SnippetString('{py:global ${1:variable_name} = ${2:"value"}}');
			await editor.insertSnippet(snippet, position);
		}
	});

	const insertPythonIfCommand = vscode.commands.registerCommand('rxiv-maker.insertPythonIf', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const snippet = new vscode.SnippetString('{py:if ${1:condition}: "${2:true_value}" else: "${3:false_value}"}');
			await editor.insertSnippet(snippet, position);
		}
	});

	const insertTexBlockCommand = vscode.commands.registerCommand('rxiv-maker.insertTexBlock', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const selection = editor.selection;
			
			if (selection.isEmpty) {
				// Insert template with cursor placeholder
				const snippet = new vscode.SnippetString('{{tex:\n$1\n}}');
				await editor.insertSnippet(snippet, position);
			} else {
				// Wrap selected code in TeX block
				const selectedText = editor.document.getText(selection);
				await editor.edit(editBuilder => {
					editBuilder.replace(selection, `{{tex:\n${selectedText}\n}}`);
				});
			}
		}
	});

	const insertTexInlineCommand = vscode.commands.registerCommand('rxiv-maker.insertTexInline', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			const position = editor.selection.active;
			const selection = editor.selection;
			
			if (selection.isEmpty) {
				// Insert template with cursor placeholder
				const snippet = new vscode.SnippetString('{{tex: $1}}');
				await editor.insertSnippet(snippet, position);
			} else {
				// Wrap selected code in inline TeX
				const selectedText = editor.document.getText(selection);
				await editor.edit(editBuilder => {
					editBuilder.replace(selection, `{{tex: ${selectedText}}}`);
				});
			}
		}
	});

	// Command to manually validate current document
	const validateDocumentCommand = vscode.commands.registerCommand('rxiv-maker.validateDocument', async () => {
		const editor = vscode.window.activeTextEditor;
		if (editor) {
			await diagnosticsProvider.validateDocument(editor.document);
			vscode.window.showInformationMessage('Document validation completed');
		} else {
			vscode.window.showWarningMessage('No active document to validate');
		}
	});

	// Command to clear all diagnostics
	const clearDiagnosticsCommand = vscode.commands.registerCommand('rxiv-maker.clearDiagnostics', () => {
		diagnosticsProvider.clearAllDiagnostics();
		vscode.window.showInformationMessage('All diagnostics cleared');
	});

	// Command to validate all open documents
	const validateAllCommand = vscode.commands.registerCommand('rxiv-maker.validateAllDocuments', async () => {
		await diagnosticsProvider.validateAllOpenDocuments();
		vscode.window.showInformationMessage('All documents validated');
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
		makeAddBibliographyCommand,
		insertBlindtextCommand,
		insertBlindtextParagraphCommand,
		insertPythonBlockCommand,
		insertPythonInlineCommand,
		insertPythonImportCommand,
		insertPythonFromImportCommand,
		insertPythonSetCommand,
		insertPythonGetCommand,
		insertPythonContextCommand,
		insertPythonFormatCommand,
		insertPythonGlobalCommand,
		insertPythonIfCommand,
		insertTexBlockCommand,
		insertTexInlineCommand,
		validateDocumentCommand,
		clearDiagnosticsCommand,
		validateAllCommand
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

		// Enhanced pattern matching for better trigger detection
		// Support patterns like: @fig:, @sfig:, @table:, @stable:, @eq:, @snote:
		// Also support partial patterns like: @f, @sf, @fig, @sfig, @t, @st, @table, @stable, @e, @eq, @sn, @snote
		const referenceMatch = beforeCursor.match(/@(s?)(fig|table|eq|snote)(:?)(.*)$/);
		const partialMatch = beforeCursor.match(/@(s?)(f|fig|t|table|stable|e|eq|sn|snote)$/);
		
		if (!referenceMatch && !partialMatch) {
			return [];
		}

		const references = await getDocumentReferences();
		let items: vscode.CompletionItem[] = [];

		if (referenceMatch) {
			// Complete reference pattern (e.g., @fig:, @table:)
			const isSupplementary = referenceMatch[1] === 's';
			const referenceType = referenceMatch[2] as 'fig' | 'table' | 'eq' | 'snote';
			const hasColon = referenceMatch[3] === ':';
			const labelPart = referenceMatch[4];

			const filteredRefs = references.filter(ref =>
				ref.type === referenceType &&
				(isSupplementary ? ref.supplementary : !ref.supplementary) &&
				(labelPart === '' || ref.label.toLowerCase().includes(labelPart.toLowerCase()))
			);

			items = filteredRefs.map(ref => {
				const item = new vscode.CompletionItem(ref.label, vscode.CompletionItemKind.Reference);
				item.detail = `${ref.supplementary ? 'Supplementary ' : ''}${ref.type.charAt(0).toUpperCase() + ref.type.slice(1)}`;
				item.documentation = new vscode.MarkdownString(`Line ${ref.line + 1}`);
				
				if (hasColon) {
					item.insertText = ref.label;
				} else {
					// Insert the complete reference format
					const prefix = ref.supplementary ? `@s${ref.type}:` : `@${ref.type}:`;
					item.insertText = `${prefix}${ref.label}`;
					item.range = new vscode.Range(
						position.with(position.line, beforeCursor.lastIndexOf('@')),
						position
					);
				}
				
				return item;
			});
		} else if (partialMatch) {
			// Partial pattern matching (e.g., @f -> show @fig: and @sfig: options)
			const isSupplementary = partialMatch[1] === 's';
			const partialType = partialMatch[2];
			
			// Map partial types to full types
			const typeMap: Record<string, string[]> = {
				'f': ['fig'],
				'fig': ['fig'],
				't': ['table'],
				'table': ['table'],
				'stable': ['table'],
				'e': ['eq'],
				'eq': ['eq'],
				'sn': ['snote'],
				'snote': ['snote']
			};
			
			const possibleTypes = typeMap[partialType] || [];
			
			for (const refType of possibleTypes) {
				const filteredRefs = references.filter(ref =>
					ref.type === refType &&
					(isSupplementary ? ref.supplementary : !ref.supplementary)
				);
				
				if (filteredRefs.length > 0) {
					// Add a completion item for the reference type
					const typeItem = new vscode.CompletionItem(
						`${isSupplementary ? 's' : ''}${refType}:`,
						vscode.CompletionItemKind.Keyword
					);
					typeItem.detail = `${isSupplementary ? 'Supplementary ' : ''}${refType.charAt(0).toUpperCase() + refType.slice(1)} reference`;
					typeItem.documentation = new vscode.MarkdownString(`Found ${filteredRefs.length} ${isSupplementary ? 'supplementary ' : ''}${refType} reference(s)`);
					typeItem.insertText = `${isSupplementary ? 's' : ''}${refType}:`;
					typeItem.range = new vscode.Range(
						position.with(position.line, beforeCursor.lastIndexOf('@') + 1),
						position
					);
					typeItem.sortText = '0'; // Priority sorting
					items.push(typeItem);
				}
			}
		}

		return items;
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
