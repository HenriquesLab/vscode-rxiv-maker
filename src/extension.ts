import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

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
	rxivMakerRoot?: string;
	error?: string;
}

export function activate(context: vscode.ExtensionContext) {
	console.log('Rxiv-Maker extension is now active!');

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
		if (!result.success || !result.rxivMakerRoot) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.rxivMakerRoot);
		terminal.show();
		terminal.sendText(`make validate MANUSCRIPT_PATH="${result.manuscriptPath}"`);
	});

	const makePdfCommand = vscode.commands.registerCommand('rxiv-maker.makePdf', async () => {
		const result = await findManuscriptFolder();
		if (!result.success || !result.rxivMakerRoot) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.rxivMakerRoot);
		terminal.show();
		terminal.sendText(`make pdf MANUSCRIPT_PATH="${result.manuscriptPath}"`);
	});

	const makeCleanCommand = vscode.commands.registerCommand('rxiv-maker.makeClean', async () => {
		const result = await findManuscriptFolder();
		if (!result.success || !result.rxivMakerRoot) {
			vscode.window.showErrorMessage(result.error || 'Could not determine manuscript folder');
			return;
		}

		const terminal = getRxivMakerTerminal(result.rxivMakerRoot);
		terminal.show();
		terminal.sendText(`make clean MANUSCRIPT_PATH="${result.manuscriptPath}"`);
	});

	const makeAddBibliographyCommand = vscode.commands.registerCommand('rxiv-maker.makeAddBibliography', async () => {
		const result = await findManuscriptFolder();
		if (!result.success || !result.rxivMakerRoot) {
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

		const terminal = getRxivMakerTerminal(result.rxivMakerRoot);
		terminal.show();
		terminal.sendText(`make add-bibliography ${cleanDoi} MANUSCRIPT_PATH="${result.manuscriptPath}"`);
	});

	context.subscriptions.push(
		fileDetector,
		citationProvider,
		referenceProvider,
		insertCitationCommand,
		insertFigureReferenceCommand,
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
	const editor = vscode.window.activeTextEditor;
	if (!editor) {
		return [];
	}

	const document = editor.document;
	const references: ReferenceLabel[] = [];
	
	for (let i = 0; i < document.lineCount; i++) {
		const line = document.lineAt(i);
		const text = line.text;
		
		const labelRegex = /\{#(s?)((fig|table|eq|snote)):([a-zA-Z0-9_-]+)\}/g;
		let match;
		
		while ((match = labelRegex.exec(text)) !== null) {
			const supplementary = match[1] === 's';
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

	// Now find the rxiv-maker root directory (where Makefile is located)
	let rxivMakerRoot: string | null = null;
	let searchDir = manuscriptPath;
	
	// Search up the directory tree for Makefile
	while (searchDir !== path.dirname(searchDir)) { // Stop at filesystem root
		try {
			await fs.promises.access(path.join(searchDir, 'Makefile'));
			// Check if this Makefile contains rxiv-maker content
			const makefileContent = await fs.promises.readFile(path.join(searchDir, 'Makefile'), 'utf8');
			if (makefileContent.includes('Rxiv-Maker') || makefileContent.includes('MANUSCRIPT_PATH')) {
				rxivMakerRoot = searchDir;
				break;
			}
		} catch {
			// Makefile not found in this directory, continue searching
		}
		searchDir = path.dirname(searchDir);
	}

	if (!rxivMakerRoot) {
		return {
			success: false,
			error: 'Could not find rxiv-maker root directory (no Makefile found). Please ensure you have the rxiv-maker repository cloned and accessible.'
		};
	}

	// Convert manuscript path to relative path from rxiv-maker root
	const relativePath = path.relative(rxivMakerRoot, manuscriptPath);

	return {
		success: true,
		manuscriptPath: relativePath || '.',
		rxivMakerRoot: rxivMakerRoot
	};
}

export function deactivate() {}
