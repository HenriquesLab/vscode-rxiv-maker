import * as vscode from 'vscode';
import { CitationValidator } from './validators/citationValidator';
import { CrossReferenceValidator } from './validators/crossReferenceValidator';
import { PythonBlockValidator } from './validators/pythonBlockValidator';
import { LaTeXBlockValidator } from './validators/latexBlockValidator';
import { StructureValidator } from './validators/structureValidator';
import { ContentParser, DocumentContent } from './contentParser';

export interface ValidationResult {
	diagnostics: vscode.Diagnostic[];
}

export interface Validator {
	validate(document: vscode.TextDocument, content?: DocumentContent): Promise<vscode.Diagnostic[]>;
}

export class RxivMarkdownDiagnosticsProvider {
	private diagnosticCollection: vscode.DiagnosticCollection;
	private validators: Validator[];
	private disposables: vscode.Disposable[] = [];

	constructor() {
		this.diagnosticCollection = vscode.languages.createDiagnosticCollection('rxiv-markdown');
		
		// Initialize validators
		this.validators = [
			new CitationValidator(),
			new CrossReferenceValidator(),
			new PythonBlockValidator(),
			new LaTeXBlockValidator(),
			new StructureValidator()
		];

		this.setupEventHandlers();
	}

	private setupEventHandlers(): void {
		// Validate on document change
		const onDidChangeDisposable = vscode.workspace.onDidChangeTextDocument(
			async (event) => {
				if (this.isRxivMarkdownDocument(event.document)) {
					await this.validateDocument(event.document);
				}
			}
		);

		// Validate on document save
		const onDidSaveDisposable = vscode.workspace.onDidSaveTextDocument(
			async (document) => {
				if (this.isRxivMarkdownDocument(document)) {
					await this.validateDocument(document);
				}
			}
		);

		// Validate on document open
		const onDidOpenDisposable = vscode.workspace.onDidOpenTextDocument(
			async (document) => {
				if (this.isRxivMarkdownDocument(document)) {
					await this.validateDocument(document);
				}
			}
		);

		// Clear diagnostics when document is closed
		const onDidCloseDisposable = vscode.workspace.onDidCloseTextDocument(
			(document) => {
				if (this.isRxivMarkdownDocument(document)) {
					this.diagnosticCollection.delete(document.uri);
				}
			}
		);

		this.disposables.push(
			onDidChangeDisposable,
			onDidSaveDisposable,
			onDidOpenDisposable,
			onDidCloseDisposable
		);
	}

	private isRxivMarkdownDocument(document: vscode.TextDocument): boolean {
		const fileName = document.fileName;
		const isRxivFile = fileName.endsWith('.rxm') ||
			fileName.endsWith('01_MAIN.md') ||
			fileName.endsWith('02_SUPPLEMENTARY_INFO.md');
		
		return document.languageId === 'rxiv-markdown' || isRxivFile;
	}

	public async validateDocument(document: vscode.TextDocument): Promise<void> {
		if (!this.isRxivMarkdownDocument(document)) {
			return;
		}

		try {
			const allDiagnostics: vscode.Diagnostic[] = [];

			// Parse document to identify content regions
			const documentContent = ContentParser.parseDocument(document);

			// Run all validators in parallel with content awareness
			const validationResults = await Promise.all(
				this.validators.map(validator => validator.validate(document, documentContent))
			);

			// Combine all diagnostics
			for (const diagnostics of validationResults) {
				allDiagnostics.push(...diagnostics);
			}

			// Update diagnostic collection
			this.diagnosticCollection.set(document.uri, allDiagnostics);
		} catch (error) {
			console.error('Error validating rxiv-markdown document:', error);
		}
	}

	public async validateAllOpenDocuments(): Promise<void> {
		const promises = vscode.workspace.textDocuments
			.filter(doc => this.isRxivMarkdownDocument(doc))
			.map(doc => this.validateDocument(doc));
		
		await Promise.all(promises);
	}

	public clearAllDiagnostics(): void {
		this.diagnosticCollection.clear();
	}

	public dispose(): void {
		this.diagnosticCollection.dispose();
		this.disposables.forEach(disposable => disposable.dispose());
		this.disposables = [];
	}
}