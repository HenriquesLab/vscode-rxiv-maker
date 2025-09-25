import * as vscode from 'vscode';

export interface ContentRegion {
	start: vscode.Position;
	end: vscode.Position;
	type: 'markdown' | 'latex' | 'python';
}

export interface DocumentContent {
	regions: ContentRegion[];
	latexBlocks: ContentRegion[];
	pythonBlocks: ContentRegion[];
	markdownRegions: ContentRegion[];
}

export class ContentParser {
	/**
	 * Parse a document to identify different content regions (markdown, LaTeX, Python)
	 */
	static parseDocument(document: vscode.TextDocument): DocumentContent {
		const text = document.getText();
		const lines = text.split('\n');
		const regions: ContentRegion[] = [];
		const latexBlocks: ContentRegion[] = [];
		const pythonBlocks: ContentRegion[] = [];
		const markdownRegions: ContentRegion[] = [];

		let currentMarkdownStart = new vscode.Position(0, 0);
		let inLatexBlock = false;
		let inPythonBlock = false;
		let blockStartPos: vscode.Position | null = null;

		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];

			// Check for LaTeX block patterns
			const latexStartMatch = line.match(/^(\s*)\{\{tex:\s*(.*)$/);
			const latexEndMatch = line.match(/^(\s*)\}\}\s*$/);

			// Check for Python block patterns
			const pythonStartMatch = line.match(/^(\s*)\{\{py:\s*(.*)$/);
			const pythonEndMatch = line.match(/^(\s*)\}\}\s*$/);

			if (latexStartMatch && !inLatexBlock && !inPythonBlock) {
				// Starting LaTeX block
				inLatexBlock = true;

				// Add markdown region up to this point (if any content exists)
				const latexStartColumn = latexStartMatch[1].length; // Indentation length
				const blockStart = new vscode.Position(lineNumber, latexStartColumn);

				if (currentMarkdownStart.isBefore(blockStart)) {
					const markdownRegion: ContentRegion = {
						start: currentMarkdownStart,
						end: blockStart,
						type: 'markdown'
					};
					regions.push(markdownRegion);
					markdownRegions.push(markdownRegion);
				}

				blockStartPos = blockStart;
			} else if (pythonStartMatch && !inLatexBlock && !inPythonBlock) {
				// Starting Python block
				inPythonBlock = true;

				// Add markdown region up to this point (if any content exists)
				const pythonStartColumn = pythonStartMatch[1].length; // Indentation length
				const blockStart = new vscode.Position(lineNumber, pythonStartColumn);

				if (currentMarkdownStart.isBefore(blockStart)) {
					const markdownRegion: ContentRegion = {
						start: currentMarkdownStart,
						end: blockStart,
						type: 'markdown'
					};
					regions.push(markdownRegion);
					markdownRegions.push(markdownRegion);
				}

				blockStartPos = blockStart;
			} else if (latexEndMatch && inLatexBlock && blockStartPos) {
				// Ending LaTeX block
				inLatexBlock = false;
				const endColumn = latexEndMatch[1].length + 2; // Indentation + "}}"
				const blockEnd = new vscode.Position(lineNumber, endColumn);

				const latexRegion: ContentRegion = {
					start: blockStartPos,
					end: blockEnd,
					type: 'latex'
				};
				regions.push(latexRegion);
				latexBlocks.push(latexRegion);

				// Next markdown region starts after this block
				currentMarkdownStart = blockEnd;
				blockStartPos = null;
			} else if (pythonEndMatch && inPythonBlock && blockStartPos) {
				// Ending Python block
				inPythonBlock = false;
				const endColumn = pythonEndMatch[1].length + 2; // Indentation + "}}"
				const blockEnd = new vscode.Position(lineNumber, endColumn);

				const pythonRegion: ContentRegion = {
					start: blockStartPos,
					end: blockEnd,
					type: 'python'
				};
				regions.push(pythonRegion);
				pythonBlocks.push(pythonRegion);

				// Next markdown region starts after this block
				currentMarkdownStart = blockEnd;
				blockStartPos = null;
			}
		}

		// Add final markdown region if document doesn't end in a block
		if (!inLatexBlock && !inPythonBlock) {
			const documentEnd = new vscode.Position(lines.length, 0);
			if (currentMarkdownStart.isBefore(documentEnd)) {
				const markdownRegion: ContentRegion = {
					start: currentMarkdownStart,
					end: documentEnd,
					type: 'markdown'
				};
				regions.push(markdownRegion);
				markdownRegions.push(markdownRegion);
			}
		}

		return {
			regions,
			latexBlocks,
			pythonBlocks,
			markdownRegions
		};
	}

	/**
	 * Check if a position is within a LaTeX block
	 */
	static isPositionInLatexBlock(position: vscode.Position, content: DocumentContent): boolean {
		return content.latexBlocks.some(block =>
			this.isPositionInRegion(position, block)
		);
	}

	/**
	 * Check if a position is within a Python block
	 */
	static isPositionInPythonBlock(position: vscode.Position, content: DocumentContent): boolean {
		return content.pythonBlocks.some(block =>
			this.isPositionInRegion(position, block)
		);
	}

	/**
	 * Check if a position is within a markdown region
	 */
	static isPositionInMarkdownRegion(position: vscode.Position, content: DocumentContent): boolean {
		return content.markdownRegions.some(block =>
			this.isPositionInRegion(position, block)
		);
	}

	/**
	 * Check if a range intersects with any LaTeX blocks
	 */
	static rangeIntersectsLatexBlocks(range: vscode.Range, content: DocumentContent): boolean {
		return content.latexBlocks.some(block =>
			this.rangeIntersectsRegion(range, block)
		);
	}

	/**
	 * Check if a range intersects with any Python blocks
	 */
	static rangeIntersectsPythonBlocks(range: vscode.Range, content: DocumentContent): boolean {
		return content.pythonBlocks.some(block =>
			this.rangeIntersectsRegion(range, block)
		);
	}

	/**
	 * Filter out text content that falls within LaTeX or Python blocks
	 */
	static filterMarkdownContent(text: string, document: vscode.TextDocument, content: DocumentContent): string {
		const lines = text.split('\n');
		const filteredLines: string[] = [];

		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];
			const lineStart = new vscode.Position(lineNumber, 0);
			const lineEnd = new vscode.Position(lineNumber, line.length);
			const lineRange = new vscode.Range(lineStart, lineEnd);

			// If line doesn't intersect with LaTeX or Python blocks, include it
			if (!this.rangeIntersectsLatexBlocks(lineRange, content) &&
				!this.rangeIntersectsPythonBlocks(lineRange, content)) {
				filteredLines.push(line);
			} else {
				// Replace with empty line to maintain line numbers
				filteredLines.push('');
			}
		}

		return filteredLines.join('\n');
	}

	private static isPositionInRegion(position: vscode.Position, region: ContentRegion): boolean {
		return position.isAfterOrEqual(region.start) && position.isBefore(region.end);
	}

	private static rangeIntersectsRegion(range: vscode.Range, region: ContentRegion): boolean {
		// Check if ranges overlap
		return !(range.end.isBefore(region.start) || range.start.isAfterOrEqual(region.end));
	}
}