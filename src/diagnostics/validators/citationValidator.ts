import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';
import { Validator } from '../index';

interface BibEntry {
	key: string;
	type: string;
	title?: string;
	author?: string;
	year?: string;
}

export class CitationValidator implements Validator {
	private bibEntriesCache: Map<string, { entries: BibEntry[]; timestamp: number }> = new Map();
	private readonly CACHE_DURATION = 5000; // 5 seconds

	async validate(document: vscode.TextDocument): Promise<vscode.Diagnostic[]> {
		const diagnostics: vscode.Diagnostic[] = [];
		const text = document.getText();
		const lines = text.split('\n');

		try {
			// Get bibliography entries
			const bibEntries = await this.getBibEntries(document);
			const bibKeys = new Set(bibEntries.map(entry => entry.key));

			// Find all citations using patterns matching rxiv-maker's approach
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
				
				// Pattern 1: Bracketed multiple citations like [@citation1;@citation2], excluding escaped
				const bracketedMatches = line.matchAll(/(?<!\\)\[(@[^\]]+)\]/g);
				for (const match of bracketedMatches) {
					// Skip if this match is inside a code span
					if (this.isPositionInCodeSpan(line, match.index!)) {
						continue;
					}
					
					const citations = match[1].match(/(?<!\\)@([a-zA-Z0-9_-]+)/g);
					if (citations) {
						for (const citation of citations) {
							const key = citation.substring(1); // Remove @
							const citationIndex = line.indexOf(citation, match.index!);
							this.validateCitationKey(key, lineNumber, line, citationIndex, bibKeys, diagnostics);
						}
					}
				}

				// Pattern 2: Single citations @key (but exclude cross-references and escaped citations)
				const singleMatches = line.matchAll(/(?<!\\)@(?!fig:|eq:|table:|tbl:|sfig:|stable:|snote:)([a-zA-Z0-9_-]+)/g);
				for (const match of singleMatches) {
					// Skip if this match is inside a code span
					if (this.isPositionInCodeSpan(line, match.index!)) {
						continue;
					}
					
					const key = match[1];
					if (key && this.isValidCitationKey(key)) {
						this.validateCitationKey(key, lineNumber, line, match.index!, bibKeys, diagnostics);
					}
				}
			}

		} catch (error) {
			// If no bibliography file is found, warn about missing citations
			const missingBibDiagnostic = new vscode.Diagnostic(
				new vscode.Range(0, 0, 0, 0),
				'No bibliography file (03_REFERENCES.bib) found. Citation validation disabled.',
				vscode.DiagnosticSeverity.Information
			);
			missingBibDiagnostic.source = 'rxiv-markdown';
			missingBibDiagnostic.code = 'missing-bibliography';
			diagnostics.push(missingBibDiagnostic);
		}

		return diagnostics;
	}

	private validateCitationKey(
		key: string,
		lineNumber: number,
		line: string,
		matchIndex: number,
		bibKeys: Set<string>,
		diagnostics: vscode.Diagnostic[]
	): void {
		if (!bibKeys.has(key)) {
			const startPos = line.indexOf('@' + key, matchIndex);
			const range = new vscode.Range(
				lineNumber,
				startPos,
				lineNumber,
				startPos + key.length + 1 // +1 for the @
			);

			const diagnostic = new vscode.Diagnostic(
				range,
				`Citation '@${key}' not found in bibliography`,
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'unknown-citation';
			diagnostics.push(diagnostic);
		}
	}

	private isValidCitationKey(key: string): boolean {
		// Valid citation key pattern matching rxiv-maker's approach
		return /^[a-zA-Z0-9_-]+$/.test(key);
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

	private async getBibEntries(document: vscode.TextDocument): Promise<BibEntry[]> {
		const searchPaths = this.getBibliographySearchPaths(document);
		
		// Find the first existing bibliography file
		let bibPath: string | null = null;
		for (const searchPath of searchPaths) {
			try {
				await fs.promises.access(searchPath, fs.constants.F_OK | fs.constants.R_OK);
				bibPath = searchPath;
				break;
			} catch {
				// Continue searching
			}
		}

		if (!bibPath) {
			throw new Error('No bibliography file found');
		}

		// Check cache first
		const cached = this.bibEntriesCache.get(bibPath);
		const now = Date.now();
		if (cached && (now - cached.timestamp) < this.CACHE_DURATION) {
			return cached.entries;
		}

		try {
			const content = await fs.promises.readFile(bibPath, 'utf8');
			const entries = this.parseBibFile(content);
			
			// Update cache
			this.bibEntriesCache.set(bibPath, { entries, timestamp: now });
			
			return entries;
		} catch (error) {
			throw new Error(`Error reading bibliography file: ${error}`);
		}
	}

	private getBibliographySearchPaths(document: vscode.TextDocument): string[] {
		const searchPaths: string[] = [];

		// 1. Try current document's directory first
		const currentDir = path.dirname(document.fileName);
		searchPaths.push(path.join(currentDir, '03_REFERENCES.bib'));

		// 2. Try workspace folders
		if (vscode.workspace.workspaceFolders) {
			for (const folder of vscode.workspace.workspaceFolders) {
				const workspaceBib = path.join(folder.uri.fsPath, '03_REFERENCES.bib');
				if (!searchPaths.includes(workspaceBib)) {
					searchPaths.push(workspaceBib);
				}
			}
		}

		return searchPaths;
	}

	private parseBibFile(content: string): BibEntry[] {
		const entries: BibEntry[] = [];
		const entryRegex = /@(\w+)\s*\{\s*([^,\s]+)\s*,/g;
		let match;

		while ((match = entryRegex.exec(content)) !== null) {
			const type = match[1];
			const key = match[2];

			const entryStart = match.index;
			const entryEnd = this.findMatchingBrace(content, entryStart);
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
	}

	private findMatchingBrace(content: string, start: number): number {
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
}