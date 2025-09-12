import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { Validator } from '../index';

export class StructureValidator implements Validator {
	async validate(document: vscode.TextDocument): Promise<vscode.Diagnostic[]> {
		const diagnostics: vscode.Diagnostic[] = [];
		const text = document.getText();
		const lines = text.split('\n');

		// Check document structure
		await this.validateDocumentStructure(document, diagnostics);
		
		// Validate heading structure
		this.validateHeadingStructure(lines, document, diagnostics);
		
		// Check for required elements
		this.checkRequiredElements(text, document.fileName, diagnostics);
		
		// Validate figure references and file existence
		await this.validateFigureFiles(lines, document, diagnostics);
		
		// Check for orphaned elements
		await this.checkOrphanedElements(text, document, diagnostics);

		return diagnostics;
	}

	private async validateDocumentStructure(document: vscode.TextDocument, diagnostics: vscode.Diagnostic[]): Promise<void> {
		const fileName = path.basename(document.fileName);
		const currentDir = path.dirname(document.fileName);
		
		// Check for required files in rxiv-maker project
		const requiredFiles = [
			{ name: '00_CONFIG.yml', description: 'Configuration file' },
			{ name: '03_REFERENCES.bib', description: 'Bibliography file' }
		];

		for (const file of requiredFiles) {
			const filePath = path.join(currentDir, file.name);
			try {
				await fs.promises.access(filePath, fs.constants.F_OK);
			} catch {
				// Check if this is likely an rxiv-maker project
				if (fileName === '01_MAIN.md' || fileName === '01_MAIN.rxm' || 
					fileName === '02_SUPPLEMENTARY_INFO.md' || fileName === '02_SUPPLEMENTARY_INFO.rxm') {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(0, 0, 0, 0),
						`Missing required file: ${file.name} (${file.description})`,
						vscode.DiagnosticSeverity.Warning
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'missing-required-file';
					diagnostics.push(diagnostic);
				}
			}
		}

		// Check FIGURES directory existence if figures are referenced
		const text = document.getText();
		if (text.includes('FIGURES/') || text.includes('![')) {
			const figuresDir = path.join(currentDir, 'FIGURES');
			try {
				const stats = await fs.promises.stat(figuresDir);
				if (!stats.isDirectory()) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(0, 0, 0, 0),
						'FIGURES should be a directory, not a file',
						vscode.DiagnosticSeverity.Error
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'invalid-figures-path';
					diagnostics.push(diagnostic);
				}
			} catch {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(0, 0, 0, 0),
					'FIGURES directory not found. Create it to store figure files.',
					vscode.DiagnosticSeverity.Information
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'missing-figures-directory';
				diagnostics.push(diagnostic);
			}
		}
	}

	private validateHeadingStructure(lines: string[], document: vscode.TextDocument, diagnostics: vscode.Diagnostic[]): void {
		let lastHeadingLevel = 0;
		let hasTitle = false;

		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];
			const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
			
			if (headingMatch) {
				const level = headingMatch[1].length;
				const title = headingMatch[2].trim();
				
				// Check if this is the document title (first heading)
				if (!hasTitle && level === 1) {
					hasTitle = true;
				}
				
				// Check for empty headings
				if (!title) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, 0, lineNumber, line.length),
						'Empty heading - headings should have descriptive text',
						vscode.DiagnosticSeverity.Warning
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'empty-heading';
					diagnostics.push(diagnostic);
				}

				// Check heading level progression
				if (level > lastHeadingLevel + 1 && lastHeadingLevel > 0) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, 0, lineNumber, headingMatch[1].length),
						`Heading level skipped. Level ${level} follows level ${lastHeadingLevel}. Consider using level ${lastHeadingLevel + 1} instead.`,
						vscode.DiagnosticSeverity.Information
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'heading-level-skip';
					diagnostics.push(diagnostic);
				}

				lastHeadingLevel = level;

				// Check for common heading formatting issues
				if (title.endsWith('.')) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, line.lastIndexOf('.'), lineNumber, line.length),
						'Headings typically should not end with periods',
						vscode.DiagnosticSeverity.Information
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'heading-period';
					diagnostics.push(diagnostic);
				}
			}
		}

		// Check if document has a title (but skip for supplementary documents)
		const fileName = path.basename(document.fileName);
		const isSupplementary = fileName === '02_SUPPLEMENTARY_INFO.md' || fileName === '02_SUPPLEMENTARY_INFO.rxm';
		
		if (!hasTitle && !isSupplementary) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(0, 0, 0, 0),
				'Document should start with a main title (# Title)',
				vscode.DiagnosticSeverity.Information
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'missing-title';
			diagnostics.push(diagnostic);
		}
	}

	private checkRequiredElements(text: string, fileName: string, diagnostics: vscode.Diagnostic[]): void {
		const basename = path.basename(fileName);
		
		// Check main manuscript requirements
		if (basename === '01_MAIN.md' || basename === '01_MAIN.rxm') {
			// Should have at least one figure or table
			const hasFigures = /!\[.*?\]\(.*?\)/.test(text) || /@fig:/.test(text);
			const hasTables = /@table:/.test(text) || text.includes('|') || text.includes('\\begin{table}');
			
			if (!hasFigures && !hasTables) {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(0, 0, 0, 0),
					'Main manuscript typically should include figures or tables',
					vscode.DiagnosticSeverity.Information
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'missing-figures-tables';
				diagnostics.push(diagnostic);
			}

			// Should have citations - check for both bracketed [@citation] and single @citation formats
			// Use more specific patterns to avoid false positives with cross-references
			const hasBracketedCitations = /\[@[a-zA-Z0-9_-]+(?:;@[a-zA-Z0-9_-]+)*\]/.test(text);
			const hasStandaloneCitations = /(?<![@\w])@[a-zA-Z0-9_-]+(?![:\w])/.test(text) && !text.match(/(?<![@\w])@(fig|table|eq|sfig|stable|snote)(?![:\w])/);
			const hasCitations = hasBracketedCitations || hasStandaloneCitations;
			if (!hasCitations) {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(0, 0, 0, 0),
					'Main manuscript should typically include citations',
					vscode.DiagnosticSeverity.Information
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'missing-citations';
				diagnostics.push(diagnostic);
			}
		}

		// Check for abstract section in main manuscript
		if ((basename === '01_MAIN.md' || basename === '01_MAIN.rxm') && text.length > 1000) {
			const hasAbstract = /^#+\s*(abstract|summary)/mi.test(text);
			if (!hasAbstract) {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(0, 0, 0, 0),
					'Consider adding an Abstract section to your manuscript',
					vscode.DiagnosticSeverity.Information
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'missing-abstract';
				diagnostics.push(diagnostic);
			}
		}
	}

	private async validateFigureFiles(lines: string[], document: vscode.TextDocument, diagnostics: vscode.Diagnostic[]): Promise<void> {
		const currentDir = path.dirname(document.fileName);
		
		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];
			
			// Find figure references with file paths
			const figureMatches = line.matchAll(/!\[([^\]]*)\]\(([^)]+)\)/g);
			
			for (const match of figureMatches) {
				const altText = match[1];
				const filePath = match[2];
				
				// Skip external URLs
				if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
					continue;
				}
				
				// Check if file exists
				const fullPath = path.resolve(currentDir, filePath);
				try {
					await fs.promises.access(fullPath, fs.constants.F_OK);
				} catch {
					const startIndex = match.index! + match[0].indexOf(filePath);
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, startIndex, lineNumber, startIndex + filePath.length),
						`Figure file not found: ${filePath}`,
						vscode.DiagnosticSeverity.Error
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'missing-figure-file';
					diagnostics.push(diagnostic);
				}


				// Check for recommended file formats
				const fileExt = path.extname(filePath).toLowerCase();
				const recommendedFormats = ['.png', '.jpg', '.jpeg', '.pdf', '.svg'];
				if (fileExt && !recommendedFormats.includes(fileExt)) {
					const startIndex = match.index! + match[0].indexOf(filePath);
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, startIndex, lineNumber, startIndex + filePath.length),
						`Consider using recommended figure formats: ${recommendedFormats.join(', ')}`,
						vscode.DiagnosticSeverity.Information
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'non-recommended-format';
					diagnostics.push(diagnostic);
				}
			}
		}
	}

	private async checkOrphanedElements(text: string, document: vscode.TextDocument, diagnostics: vscode.Diagnostic[]): Promise<void> {
		const lines = text.split('\n');
		
		// Find all defined labels in current document
		const definedLabels = new Set<string>();
		const labelRegex = /\{#(s?(?:fig|table|eq|snote)):([a-zA-Z0-9_-]+)[^}]*\}/g;
		let match;
		while ((match = labelRegex.exec(text)) !== null) {
			const prefix = match[1];
			const label = match[2];
			definedLabels.add(`${prefix}:${label}`);
		}

		// Find all references across all project files
		const referencedLabels = await this.findAllReferencesInProject(document);

		// Find orphaned labels (defined but never referenced across the project)
		for (const definedLabel of definedLabels) {
			if (!referencedLabels.has(definedLabel)) {
				// Find the line where this label is defined
				const labelDefMatch = text.match(new RegExp(`\\{#${definedLabel.replace(':', ':')}[^}]*\\}`, 'g'));
				if (labelDefMatch) {
					const labelText = labelDefMatch[0];
					const textBeforeLabel = text.substring(0, text.indexOf(labelText));
					const lineNumber = textBeforeLabel.split('\n').length - 1;
					
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, 0, lineNumber, lines[lineNumber]?.length || 0),
						`Label '${definedLabel}' is defined but never referenced in project`,
						vscode.DiagnosticSeverity.Information
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'orphaned-label';
					diagnostics.push(diagnostic);
				}
			}
		}

		// Check for unusual patterns that might indicate issues
		this.checkUnusualPatterns(lines, diagnostics);
	}

	private async findAllReferencesInProject(document: vscode.TextDocument): Promise<Set<string>> {
		const referencedLabels = new Set<string>();
		const currentDir = path.dirname(document.fileName);
		
		// Priority manuscript files to check for cross-references
		const priorityFiles = [
			'01_MAIN.md',
			'01_MAIN.rxm', 
			'02_SUPPLEMENTARY_INFO.md',
			'02_SUPPLEMENTARY_INFO.rxm'
		];
		
		// Files to check (priority files first, then others)
		const filesToCheck: string[] = [];
		
		try {
			const allFiles = await fs.promises.readdir(currentDir);
			
			// Add priority files if they exist
			for (const priorityFile of priorityFiles) {
				if (allFiles.includes(priorityFile)) {
					filesToCheck.push(priorityFile);
				}
			}
			
			// Add other markdown files
			const otherMarkdownFiles = allFiles.filter(file => 
				(file.endsWith('.rxm') || file.endsWith('.md')) && 
				!file.startsWith('.') && 
				!priorityFiles.includes(file) &&
				file !== 'README.md' && 
				file !== 'CHANGELOG.md'
			);
			filesToCheck.push(...otherMarkdownFiles);

			// Read all files and extract references
			for (const file of filesToCheck) {
				const filePath = path.join(currentDir, file);
				try {
					const content = await fs.promises.readFile(filePath, 'utf8');
					// Regex that matches all reference patterns
					const refRegex = /@(stable|sfig|fig|table|eq|snote):([a-zA-Z0-9_-]+)/g;
					let match;
					while ((match = refRegex.exec(content)) !== null) {
						const prefix = match[1];
						const label = match[2];
						referencedLabels.add(`${prefix}:${label}`);
					}
				} catch {
					// Skip files that can't be read
					continue;
				}
			}
		} catch {
			// Fall back to checking only current document if directory read fails
			const text = document.getText();
			const refRegex = /@(stable|sfig|fig|table|eq|snote):([a-zA-Z0-9_-]+)/g;
			let match;
			while ((match = refRegex.exec(text)) !== null) {
				const prefix = match[1];
				const label = match[2];
				referencedLabels.add(`${prefix}:${label}`);
			}
		}

		return referencedLabels;
	}


	private checkUnusualPatterns(lines: string[], diagnostics: vscode.Diagnostic[]): void {
		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];
			
			// Check for multiple consecutive empty lines
			if (lineNumber < lines.length - 2) {
				const currentEmpty = !line.trim();
				const nextEmpty = !lines[lineNumber + 1]?.trim();
				const thirdEmpty = !lines[lineNumber + 2]?.trim();
				
				if (currentEmpty && nextEmpty && thirdEmpty) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, 0, lineNumber + 2, 0),
						'Multiple consecutive empty lines - consider reducing for cleaner formatting',
						vscode.DiagnosticSeverity.Information
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'multiple-empty-lines';
					diagnostics.push(diagnostic);
				}
			}


			// Check for trailing whitespace
			if (line.match(/\s+$/)) {
				const trailingStart = line.search(/\s+$/);
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(lineNumber, trailingStart, lineNumber, line.length),
					'Trailing whitespace',
					vscode.DiagnosticSeverity.Information
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'trailing-whitespace';
				diagnostics.push(diagnostic);
			}
		}
	}
}