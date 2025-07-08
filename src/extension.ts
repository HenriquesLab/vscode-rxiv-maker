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

export function activate(context: vscode.ExtensionContext) {
	console.log('Rxiv-Maker extension is now active!');

	// Automatically detect and set language mode for rxiv-maker files
	const fileDetector = vscode.workspace.onDidOpenTextDocument(async (document) => {
		if (document.fileName.endsWith('.md')) {
			const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
			if (workspaceFolder && await isRxivMakerProject(workspaceFolder.uri.fsPath)) {
				await vscode.languages.setTextDocumentLanguage(document, 'rxiv-markdown');
			}
		}
	});

	// Check already open documents
	vscode.workspace.textDocuments.forEach(async (document) => {
		if (document.fileName.endsWith('.md')) {
			const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
			if (workspaceFolder && await isRxivMakerProject(workspaceFolder.uri.fsPath)) {
				await vscode.languages.setTextDocumentLanguage(document, 'rxiv-markdown');
			}
		}
	});

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
			vscode.window.showWarningMessage('No bibliography file found. Please create 03_REFERENCES.bib');
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

	const validateProjectCommand = vscode.commands.registerCommand('rxiv-maker.validateProject', async () => {
		const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
		if (!workspaceFolder) {
			vscode.window.showErrorMessage('No workspace folder found');
			return;
		}

		const requiredFiles = ['00_CONFIG.yml', '01_MAIN.md', '03_REFERENCES.bib'];
		const optionalFiles = ['02_SUPPLEMENTARY_INFO.md'];
		const messages: string[] = [];

		for (const file of requiredFiles) {
			const filePath = path.join(workspaceFolder.uri.fsPath, file);
			if (!fs.existsSync(filePath)) {
				messages.push(`❌ Missing required file: ${file}`);
			} else {
				messages.push(`✅ Found: ${file}`);
			}
		}

		for (const file of optionalFiles) {
			const filePath = path.join(workspaceFolder.uri.fsPath, file);
			if (fs.existsSync(filePath)) {
				messages.push(`✅ Found: ${file}`);
			} else {
				messages.push(`ℹ️ Optional file not found: ${file}`);
			}
		}

		const figuresDir = path.join(workspaceFolder.uri.fsPath, 'FIGURES');
		if (fs.existsSync(figuresDir)) {
			messages.push(`✅ Found: FIGURES/ directory`);
		} else {
			messages.push(`ℹ️ FIGURES/ directory not found`);
		}

		vscode.window.showInformationMessage(`Project validation complete:\n${messages.join('\n')}`);
	});

	context.subscriptions.push(
		fileDetector,
		citationProvider,
		referenceProvider,
		insertCitationCommand,
		insertFigureReferenceCommand,
		validateProjectCommand
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
		
		if (!beforeCursor.endsWith('@')) {
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
		
		if (!beforeCursor.match(/@(s?)fig:$|@(s?)table:$|@eq:$|@snote:$/)) {
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
	const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
	if (!workspaceFolder) {
		return [];
	}

	const bibPath = path.join(workspaceFolder.uri.fsPath, '03_REFERENCES.bib');
	if (!fs.existsSync(bibPath)) {
		return [];
	}

	try {
		const content = fs.readFileSync(bibPath, 'utf8');
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
	const requiredFiles = ['00_CONFIG.yml', '01_MAIN.md', '03_REFERENCES.bib'];
	const detectedFiles = requiredFiles.filter(file => 
		fs.existsSync(path.join(workspacePath, file))
	);
	
	// Consider it an rxiv-maker project if at least 2 out of 3 required files are present
	return detectedFiles.length >= 2;
}

export function deactivate() {}
