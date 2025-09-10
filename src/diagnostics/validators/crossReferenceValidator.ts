import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { Validator } from '../index';

interface ReferenceLabel {
	type: 'fig' | 'sfig' | 'table' | 'stable' | 'eq' | 'snote';
	label: string;
	line: number;
	file: string;
}

export class CrossReferenceValidator implements Validator {
	private labelsCache: Map<string, { labels: ReferenceLabel[]; timestamp: number }> = new Map();
	private readonly CACHE_DURATION = 5000; // 5 seconds

	async validate(document: vscode.TextDocument): Promise<vscode.Diagnostic[]> {
		const diagnostics: vscode.Diagnostic[] = [];
		const text = document.getText();
		const lines = text.split('\n');

		try {
			// Get all defined labels from manuscript files
			const definedLabels = await this.getDefinedLabels(document);
			const labelMap = this.createLabelMap(definedLabels);

			// Reference patterns matching rxiv-maker's approach, but excluding escaped references
			const referencePatterns = {
				'fig': /(?<!\\)@fig:([a-zA-Z0-9_-]+)/g,
				'sfig': /(?<!\\)@sfig:([a-zA-Z0-9_-]+)/g,
				'table': /(?<!\\)@table:([a-zA-Z0-9_-]+)/g,
				'stable': /(?<!\\)@stable:([a-zA-Z0-9_-]+)/g,
				'eq': /(?<!\\)@eq:([a-zA-Z0-9_-]+)/g,
				'snote': /(?<!\\)@snote:([a-zA-Z0-9_-]+)/g
			};

			// Find all cross-references in the document
			let inCodeBlock = false;
			for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
				const line = lines[lineNumber];
				
				// Check for code block boundaries
				if (line.trim().startsWith('```')) {
					inCodeBlock = !inCodeBlock;
					continue;
				}
				
				// Skip validation inside code blocks
				if (inCodeBlock) {
					continue;
				}
				
				for (const [refType, pattern] of Object.entries(referencePatterns)) {
					const matches = line.matchAll(pattern);
					for (const match of matches) {
						// Skip if this match is inside a code span
						if (this.isPositionInCodeSpan(line, match.index!)) {
							continue;
						}
						
						const label = match[1];
						const fullRef = `${refType}:${label}`;
						
						if (!labelMap.has(fullRef)) {
							const range = new vscode.Range(
								lineNumber,
								match.index!,
								lineNumber,
								match.index! + match[0].length
							);

							const diagnostic = new vscode.Diagnostic(
								range,
								`Reference '${match[0]}' not found. No matching label defined.`,
								vscode.DiagnosticSeverity.Error
							);
							diagnostic.source = 'rxiv-markdown';
							diagnostic.code = 'undefined-reference';
							diagnostics.push(diagnostic);
						}
					}
				}
			}

			// Check for duplicate label definitions
			const duplicates = this.findDuplicateLabels(definedLabels);
			for (const duplicate of duplicates) {
				if (duplicate.file === document.fileName) {
					const range = new vscode.Range(duplicate.line, 0, duplicate.line, 0);
					const diagnostic = new vscode.Diagnostic(
						range,
						`Duplicate label '${duplicate.type}:${duplicate.label}' defined multiple times`,
						vscode.DiagnosticSeverity.Warning
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'duplicate-label';
					diagnostics.push(diagnostic);
				}
			}

		} catch (error) {
			console.error('Error validating cross-references:', error);
		}

		return diagnostics;
	}

	private async getDefinedLabels(document: vscode.TextDocument): Promise<ReferenceLabel[]> {
		const manuscriptFiles = await this.getManuscriptFiles(document);
		const allLabels: ReferenceLabel[] = [];

		for (const filePath of manuscriptFiles) {
			try {
				// Check cache first
				const cached = this.labelsCache.get(filePath);
				const now = Date.now();
				if (cached && (now - cached.timestamp) < this.CACHE_DURATION) {
					allLabels.push(...cached.labels);
					continue;
				}

				const content = await fs.promises.readFile(filePath, 'utf8');
				const labels = this.extractLabelsFromContent(content, filePath);
				
				// Update cache
				this.labelsCache.set(filePath, { labels, timestamp: now });
				allLabels.push(...labels);

			} catch (error) {
				// File might not exist or be readable, continue with others
				continue;
			}
		}

		return allLabels;
	}

	private extractLabelsFromContent(content: string, filePath: string): ReferenceLabel[] {
		const labels: ReferenceLabel[] = [];
		const lines = content.split('\n');

		// Label patterns matching rxiv-maker's approach
		const labelPatterns = {
			'fig': /\{#fig:([a-zA-Z0-9_:-]+)([^}]*)\}/g,
			'sfig': /\{#sfig:([a-zA-Z0-9_:-]+)([^}]*)\}/g,
			'table': /\{#table:([a-zA-Z0-9_:-]+)([^}]*)\}/g,
			'stable': /\{#stable:([a-zA-Z0-9_:-]+)([^}]*)\}/g,
			'eq': /\$\$.*?\$\$\s*\{[^}]*#eq:([a-zA-Z0-9_:-]+)[^}]*\}/g,
			'snote': /\{#snote:([a-zA-Z0-9_:-]+)\}/g
		};

		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];
			
			for (const [labelType, pattern] of Object.entries(labelPatterns)) {
				const matches = line.matchAll(pattern);
				for (const match of matches) {
					const label = match[1];
					labels.push({
						type: labelType as 'fig' | 'sfig' | 'table' | 'stable' | 'eq' | 'snote',
						label,
						line: lineNumber,
						file: filePath
					});
				}
			}
		}

		return labels;
	}

	private async getManuscriptFiles(document: vscode.TextDocument): Promise<string[]> {
		const searchPaths: string[] = [];

		// 1. Try current document's directory first
		const currentDir = path.dirname(document.fileName);
		searchPaths.push(path.join(currentDir, '01_MAIN.md'));
		searchPaths.push(path.join(currentDir, '02_SUPPLEMENTARY_INFO.md'));
		searchPaths.push(path.join(currentDir, '01_MAIN.rxm'));
		searchPaths.push(path.join(currentDir, '02_SUPPLEMENTARY_INFO.rxm'));

		// 2. Try workspace folders
		if (vscode.workspace.workspaceFolders) {
			for (const folder of vscode.workspace.workspaceFolders) {
				const folderPath = folder.uri.fsPath;
				const mainMd = path.join(folderPath, '01_MAIN.md');
				const suppMd = path.join(folderPath, '02_SUPPLEMENTARY_INFO.md');
				const mainRxm = path.join(folderPath, '01_MAIN.rxm');
				const suppRxm = path.join(folderPath, '02_SUPPLEMENTARY_INFO.rxm');

				if (!searchPaths.includes(mainMd)) { searchPaths.push(mainMd); }
				if (!searchPaths.includes(suppMd)) { searchPaths.push(suppMd); }
				if (!searchPaths.includes(mainRxm)) { searchPaths.push(mainRxm); }
				if (!searchPaths.includes(suppRxm)) { searchPaths.push(suppRxm); }
			}
		}

		// Filter to only existing files
		const existingFiles: string[] = [];
		for (const filePath of searchPaths) {
			try {
				await fs.promises.access(filePath, fs.constants.F_OK);
				existingFiles.push(filePath);
			} catch {
				// File doesn't exist, skip
			}
		}

		return existingFiles;
	}

	private createLabelMap(labels: ReferenceLabel[]): Map<string, ReferenceLabel> {
		const labelMap = new Map<string, ReferenceLabel>();
		
		for (const label of labels) {
			const key = `${label.type}:${label.label}`;
			labelMap.set(key, label);
		}
		
		return labelMap;
	}

	private findDuplicateLabels(labels: ReferenceLabel[]): ReferenceLabel[] {
		const seen = new Map<string, ReferenceLabel>();
		const duplicates: ReferenceLabel[] = [];

		for (const label of labels) {
			const key = `${label.type}:${label.label}`;
			if (seen.has(key)) {
				duplicates.push(label);
				// Also mark the first occurrence as duplicate
				const firstOccurrence = seen.get(key)!;
				if (!duplicates.includes(firstOccurrence)) {
					duplicates.push(firstOccurrence);
				}
			} else {
				seen.set(key, label);
			}
		}

		return duplicates;
	}

	private isPositionInCodeSpan(line: string, position: number): boolean {
		// Find all backtick pairs in the line
		const backtickMatches: { start: number; end: number }[] = [];
		let start = -1;
		
		for (let i = 0; i < line.length; i++) {
			if (line[i] === '`') {
				if (start === -1) {
					start = i;
				} else {
					backtickMatches.push({ start, end: i });
					start = -1;
				}
			}
		}
		
		// Check if position falls within any code span
		for (const span of backtickMatches) {
			if (position >= span.start && position <= span.end) {
				return true;
			}
		}
		
		return false;
	}
}