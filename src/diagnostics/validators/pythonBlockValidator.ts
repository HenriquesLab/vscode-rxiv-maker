import * as vscode from 'vscode';
import { Validator } from '../index';

export class PythonBlockValidator implements Validator {
	async validate(document: vscode.TextDocument): Promise<vscode.Diagnostic[]> {
		const diagnostics: vscode.Diagnostic[] = [];
		const text = document.getText();
		const lines = text.split('\n');

		// Find Python code blocks
		let inPythonBlock = false;
		let blockStartLine = -1;
		let blockIndent = '';

		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];

			// Python block patterns matching rxiv-maker syntax
			const blockStartMatch = line.match(/^\s*\{\{py:\s*(.*)$/);
			const blockEndMatch = line.match(/^\s*\}\}\s*$/);
			const inlineMatch = line.match(/\{py:\s*([^}]+)\}/g);

			if (blockStartMatch && !inPythonBlock) {
				// Start of Python block
				inPythonBlock = true;
				blockStartLine = lineNumber;
				blockIndent = line.match(/^\s*/)?.[0] || '';
				
				// Check if there's code on the same line as the opening {{py:
				const inlineCode = blockStartMatch[1].trim();
				if (inlineCode && !inlineCode.endsWith('}}')) {
					this.validatePythonSyntax(inlineCode, lineNumber, blockStartMatch.index!, diagnostics);
				}
			} else if (blockEndMatch && inPythonBlock) {
				// End of Python block
				inPythonBlock = false;
				blockStartLine = -1;
			} else if (inPythonBlock && blockStartLine !== -1) {
				// Inside Python block - validate the line
				const pythonCode = line.replace(/^\s*/, ''); // Remove leading whitespace
				if (pythonCode.trim() && !pythonCode.includes('}}')) {
					this.validatePythonSyntax(pythonCode, lineNumber, 0, diagnostics);
				}
			}

			// Check inline Python expressions
			if (inlineMatch) {
				for (const match of inlineMatch) {
					const codeMatch = match.match(/\{py:\s*([^}]+)\}/);
					if (codeMatch) {
						const code = codeMatch[1];
						const matchIndex = line.indexOf(match);
						this.validateInlinePython(code, lineNumber, matchIndex, diagnostics);
					}
				}
			}

			// Check Python variable operations
			this.validatePythonVariableOperations(line, lineNumber, diagnostics);
		}

		// Check for unclosed Python blocks
		if (inPythonBlock) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(blockStartLine, 0, blockStartLine, lines[blockStartLine].length),
				'Unclosed Python block - missing "}}"',
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'unclosed-python-block';
			diagnostics.push(diagnostic);
		}

		return diagnostics;
	}

	private validatePythonSyntax(code: string, lineNumber: number, startColumn: number, diagnostics: vscode.Diagnostic[]): void {
		// Basic Python syntax validation
		const trimmedCode = code.trim();
		
		if (!trimmedCode) { return; }

		// Check for common syntax errors
		const issues = this.findBasicSyntaxIssues(trimmedCode);
		
		for (const issue of issues) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + code.length),
				issue.message,
				issue.severity
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = issue.code;
			diagnostics.push(diagnostic);
		}
	}

	private validateInlinePython(code: string, lineNumber: number, startColumn: number, diagnostics: vscode.Diagnostic[]): void {
		const trimmedCode = code.trim();
		
		// Check for invalid inline Python patterns
		if (trimmedCode.includes('\n')) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + code.length + 6), // +6 for {py: }
				'Inline Python expressions cannot contain newlines',
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'multiline-inline-python';
			diagnostics.push(diagnostic);
		}

		// Validate the inline code syntax
		this.validatePythonSyntax(trimmedCode, lineNumber, startColumn + 4, diagnostics); // +4 for {py:
	}

	private validatePythonVariableOperations(line: string, lineNumber: number, diagnostics: vscode.Diagnostic[]): void {
		// rxiv-maker specific Python operations
		const operations = [
			{ pattern: /\{py:set\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)\}/, type: 'set' },
			{ pattern: /\{py:get\s+([a-zA-Z_][a-zA-Z0-9_]*)\}/, type: 'get' },
			{ pattern: /\{py:global\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+)\}/, type: 'global' },
			{ pattern: /\{py:format="([^"]+)"\s+(.+)\}/, type: 'format' },
			{ pattern: /\{py:context="([^"]+)"\s+(.+)\}/, type: 'context' },
			{ pattern: /\{py:if\s+(.+?):\s*"([^"]*?)"\s*else:\s*"([^"]*?)"\}/, type: 'conditional' }
		];

		for (const op of operations) {
			const matches = line.matchAll(new RegExp(op.pattern.source, 'g'));
			for (const match of matches) {
				this.validatePythonOperation(match, op.type, lineNumber, diagnostics);
			}
		}

		// Check import statements
		const importMatches = line.matchAll(/\{py:import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}/g);
		for (const match of importMatches) {
			this.validateImportStatement(match[1], lineNumber, match.index!, diagnostics);
		}

		const fromImportMatches = line.matchAll(/\{py:from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)\}/g);
		for (const match of fromImportMatches) {
			this.validateFromImportStatement(match[1], match[2], lineNumber, match.index!, diagnostics);
		}
	}

	private findBasicSyntaxIssues(code: string): Array<{message: string; severity: vscode.DiagnosticSeverity; code: string}> {
		const issues: Array<{message: string; severity: vscode.DiagnosticSeverity; code: string}> = [];

		// Check for unmatched parentheses
		const openParens = (code.match(/\(/g) || []).length;
		const closeParens = (code.match(/\)/g) || []).length;
		if (openParens !== closeParens) {
			issues.push({
				message: 'Unmatched parentheses in Python code',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'unmatched-parentheses'
			});
		}

		// Check for unmatched brackets
		const openBrackets = (code.match(/\[/g) || []).length;
		const closeBrackets = (code.match(/\]/g) || []).length;
		if (openBrackets !== closeBrackets) {
			issues.push({
				message: 'Unmatched brackets in Python code',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'unmatched-brackets'
			});
		}

		// Check for unmatched braces
		const openBraces = (code.match(/\{/g) || []).length;
		const closeBraces = (code.match(/\}/g) || []).length;
		if (openBraces !== closeBraces) {
			issues.push({
				message: 'Unmatched braces in Python code',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'unmatched-braces'
			});
		}

		// Check for invalid indentation (basic check)
		if (code.includes('\t') && code.includes('    ')) {
			issues.push({
				message: 'Mixed tabs and spaces in Python code',
				severity: vscode.DiagnosticSeverity.Warning,
				code: 'mixed-indentation'
			});
		}

		// Check for basic syntax patterns
		if (code.match(/^\s*def\s+/) && !code.includes(':')) {
			issues.push({
				message: 'Function definition missing colon',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'missing-colon'
			});
		}

		if (code.match(/^\s*(if|elif|else|for|while|try|except|finally|with)\s+/) && !code.includes(':')) {
			issues.push({
				message: 'Control structure missing colon',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'missing-colon'
			});
		}

		return issues;
	}

	private validatePythonOperation(match: RegExpMatchArray, operationType: string, lineNumber: number, diagnostics: vscode.Diagnostic[]): void {
		const fullMatch = match[0];
		const startColumn = match.index!;

		switch (operationType) {
			case 'set':
			case 'global':
				const varName = match[1];
				const value = match[2];
				if (!this.isValidVariableName(varName)) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + fullMatch.length),
						`Invalid variable name '${varName}'`,
						vscode.DiagnosticSeverity.Error
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'invalid-variable-name';
					diagnostics.push(diagnostic);
				}
				break;

			case 'get':
				const getVarName = match[1];
				if (!this.isValidVariableName(getVarName)) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + fullMatch.length),
						`Invalid variable name '${getVarName}'`,
						vscode.DiagnosticSeverity.Error
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'invalid-variable-name';
					diagnostics.push(diagnostic);
				}
				break;

			case 'format':
				const formatSpec = match[1];
				// Basic format specification validation
				if (!formatSpec.trim()) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + fullMatch.length),
						'Empty format specification',
						vscode.DiagnosticSeverity.Warning
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'empty-format-spec';
					diagnostics.push(diagnostic);
				}
				break;
		}
	}

	private validateImportStatement(moduleName: string, lineNumber: number, startColumn: number, diagnostics: vscode.Diagnostic[]): void {
		if (!this.isValidModuleName(moduleName)) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + moduleName.length + 12), // +12 for {py:import }
				`Invalid module name '${moduleName}'`,
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'invalid-module-name';
			diagnostics.push(diagnostic);
		}
	}

	private validateFromImportStatement(moduleName: string, imports: string, lineNumber: number, startColumn: number, diagnostics: vscode.Diagnostic[]): void {
		if (!this.isValidModuleName(moduleName)) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + 20), // Approximate length
				`Invalid module name '${moduleName}'`,
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'invalid-module-name';
			diagnostics.push(diagnostic);
		}

		// Validate import names
		const importNames = imports.split(',').map(name => name.trim());
		for (const importName of importNames) {
			if (!this.isValidVariableName(importName)) {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(lineNumber, startColumn, lineNumber, startColumn + 20), // Approximate length
					`Invalid import name '${importName}'`,
					vscode.DiagnosticSeverity.Error
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'invalid-import-name';
				diagnostics.push(diagnostic);
			}
		}
	}

	private isValidVariableName(name: string): boolean {
		return /^[a-zA-Z_][a-zA-Z0-9_]*$/.test(name);
	}

	private isValidModuleName(name: string): boolean {
		return /^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*$/.test(name);
	}
}