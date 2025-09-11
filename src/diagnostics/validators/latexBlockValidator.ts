import * as vscode from 'vscode';
import { Validator } from '../index';

export class LaTeXBlockValidator implements Validator {
	async validate(document: vscode.TextDocument): Promise<vscode.Diagnostic[]> {
		const diagnostics: vscode.Diagnostic[] = [];
		const text = document.getText();
		const lines = text.split('\n');

		// Find LaTeX/TeX code blocks and inline expressions
		let inTexBlock = false;
		let blockStartLine = -1;
		let blockContent = '';
		let blockLines: string[] = [];
		let environmentStack: Array<{name: string, line: number}> = [];

		for (let lineNumber = 0; lineNumber < lines.length; lineNumber++) {
			const line = lines[lineNumber];

			// TeX block patterns matching rxiv-maker syntax
			const blockStartMatch = line.match(/^\s*\{\{tex:\s*(.*)$/);
			const blockEndMatch = line.match(/^\s*\}\}\s*$/);
			const inlineMatch = line.match(/\{\{tex:\s*([^}]+)\}\}/g);

			if (blockStartMatch && !inTexBlock) {
				// Start of TeX block
				inTexBlock = true;
				blockStartLine = lineNumber;
				blockContent = '';
				blockLines = [];
				
				// Check if there's LaTeX code on the same line as the opening {{tex:
				const inlineCode = blockStartMatch[1].trim();
				if (inlineCode && !inlineCode.endsWith('}}')) {
					blockContent += inlineCode + '\n';
					blockLines.push(inlineCode);
				}
			} else if (blockEndMatch && inTexBlock) {
				// End of TeX block - validate the entire block content
				inTexBlock = false;
				
				if (blockContent.trim()) {
					this.validateTexBlock(blockContent, blockStartLine, blockLines, environmentStack, diagnostics);
				}
				
				// Check for unclosed environments at end of block
				this.checkUnclosedenvironments(environmentStack, lineNumber, diagnostics);
				environmentStack = [];
				blockStartLine = -1;
				blockContent = '';
				blockLines = [];
			} else if (inTexBlock && blockStartLine !== -1) {
				// Inside TeX block - accumulate content
				const latexCode = line.trim();
				if (latexCode && !latexCode.includes('}}')) {
					blockContent += latexCode + '\n';
					blockLines.push(latexCode);
				}
			}

			// Check inline TeX expressions
			if (inlineMatch) {
				for (const match of inlineMatch) {
					const codeMatch = match.match(/\{\{tex:\s*([^}]+)\}\}/);
					if (codeMatch) {
						const code = codeMatch[1];
						const matchIndex = line.indexOf(match);
						const tempStack: Array<{name: string, line: number}> = [];
						this.validateLaTeXSyntax(code, lineNumber, matchIndex, tempStack, diagnostics);
					}
				}
			}

			// Also check for inline LaTeX math expressions and commands outside blocks
			if (!inTexBlock) {
				this.validateInlineLaTeXElements(line, lineNumber, diagnostics);
			}
		}

		// Check for unclosed TeX blocks
		if (inTexBlock) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(blockStartLine, 0, blockStartLine, lines[blockStartLine].length),
				'Unclosed TeX block - missing "}}"',
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'unclosed-tex-block';
			diagnostics.push(diagnostic);
		}

		return diagnostics;
	}

	private validateTexBlock(
		blockContent: string,
		blockStartLine: number,
		blockLines: string[],
		environmentStack: Array<{name: string, line: number}>,
		diagnostics: vscode.Diagnostic[]
	): void {
		// Validate the entire block content for brace matching
		const braceIssues = this.findBraceIssues(blockContent);
		for (const issue of braceIssues) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(blockStartLine, 0, blockStartLine + blockLines.length, 0),
				issue.message,
				issue.severity
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = issue.code;
			diagnostics.push(diagnostic);
		}

		// Validate each line for environments and other syntax
		for (let i = 0; i < blockLines.length; i++) {
			const line = blockLines[i];
			const lineNumber = blockStartLine + i + (blockStartLine === 0 ? 0 : 1); // Adjust for block start
			this.trackLaTeXEnvironments(line, lineNumber, environmentStack, diagnostics);
		}
	}

	private findBraceIssues(content: string): Array<{
		message: string;
		severity: vscode.DiagnosticSeverity;
		code: string;
	}> {
		const issues: Array<{
			message: string;
			severity: vscode.DiagnosticSeverity;
			code: string;
		}> = [];

		// Check for unmatched braces across the entire block
		let braceCount = 0;
		let inString = false;
		let stringChar = '';

		for (let i = 0; i < content.length; i++) {
			const char = content[i];
			const prevChar = i > 0 ? content[i-1] : '';

			// Handle string literals
			if (inString) {
				if (char === stringChar && prevChar !== '\\') {
					inString = false;
				}
				continue;
			}

			if ((char === '"' || char === "'") && prevChar !== '\\') {
				inString = true;
				stringChar = char;
				continue;
			}

			// Count braces (ignore escaped braces)
			if (char === '{' && prevChar !== '\\') {
				braceCount++;
			} else if (char === '}' && prevChar !== '\\') {
				braceCount--;
			}

			// Early detection of negative brace count
			if (braceCount < 0) {
				issues.push({
					message: 'Unmatched closing brace in LaTeX code',
					severity: vscode.DiagnosticSeverity.Error,
					code: 'unmatched-closing-brace'
				});
				break;
			}
		}

		// Check for unmatched opening braces
		if (braceCount > 0) {
			issues.push({
				message: 'Unmatched opening brace in LaTeX code',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'unmatched-opening-brace'
			});
		}

		return issues;
	}

	private validateLaTeXSyntax(
		code: string,
		lineNumber: number,
		startColumn: number,
		environmentStack: Array<{name: string, line: number}>,
		diagnostics: vscode.Diagnostic[]
	): void {
		if (!code.trim()) { return; }

		// Track LaTeX environments
		this.trackLaTeXEnvironments(code, lineNumber, environmentStack, diagnostics);

		// Check for common LaTeX syntax errors
		const issues = this.findLaTeXSyntaxIssues(code);
		
		for (const issue of issues) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(lineNumber, startColumn + issue.column, lineNumber, startColumn + issue.column + issue.length),
				issue.message,
				issue.severity
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = issue.code;
			diagnostics.push(diagnostic);
		}
	}

	private validateInlineLaTeXElements(line: string, lineNumber: number, diagnostics: vscode.Diagnostic[]): void {
		// Check inline math expressions $...$ and $$...$$
		const mathExpressions = [
			...line.matchAll(/\$\$([^$]+)\$\$/g),
			...line.matchAll(/(?<!\$)\$([^$\n]+)\$(?!\$)/g)
		];

		for (const match of mathExpressions) {
			const mathContent = match[1];
			const startIndex = match.index!;
			
			// Basic math expression validation
			const issues = this.findMathExpressionIssues(mathContent);
			for (const issue of issues) {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(lineNumber, startIndex, lineNumber, startIndex + match[0].length),
					issue.message,
					issue.severity
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = issue.code;
				diagnostics.push(diagnostic);
			}
		}

		// Check for common LaTeX commands in text
		const commandMatches = line.matchAll(/\\([a-zA-Z]+)(\*?)\{([^}]*)\}/g);
		for (const match of commandMatches) {
			const command = match[1];
			const starred = match[2];
			const content = match[3];
			const startIndex = match.index!;
			
			this.validateLaTeXCommand(command, starred, content, lineNumber, startIndex, diagnostics);
		}
	}

	private trackLaTeXEnvironments(
		code: string,
		lineNumber: number,
		environmentStack: Array<{name: string, line: number}>,
		diagnostics: vscode.Diagnostic[]
	): void {
		// Find \begin{environment} and \end{environment} commands
		const beginMatches = [...code.matchAll(/\\begin\{([^}]+)\}/g)];
		const endMatches = [...code.matchAll(/\\end\{([^}]+)\}/g)];

		// Process in order of appearance
		const allMatches = [
			...beginMatches.map(m => ({type: 'begin', env: m[1], index: m.index!})),
			...endMatches.map(m => ({type: 'end', env: m[1], index: m.index!}))
		].sort((a, b) => a.index - b.index);

		for (const match of allMatches) {
			if (match.type === 'begin') {
				environmentStack.push({name: match.env, line: lineNumber});
			} else if (match.type === 'end') {
				if (environmentStack.length === 0) {
					const diagnostic = new vscode.Diagnostic(
						new vscode.Range(lineNumber, match.index, lineNumber, match.index + `\\end{${match.env}}`.length),
						`Unexpected \\end{${match.env}} - no matching \\begin`,
						vscode.DiagnosticSeverity.Error
					);
					diagnostic.source = 'rxiv-markdown';
					diagnostic.code = 'unmatched-end-environment';
					diagnostics.push(diagnostic);
				} else {
					const lastEnv = environmentStack.pop()!;
					if (lastEnv.name !== match.env) {
						const diagnostic = new vscode.Diagnostic(
							new vscode.Range(lineNumber, match.index, lineNumber, match.index + `\\end{${match.env}}`.length),
							`Environment mismatch: \\end{${match.env}} does not match \\begin{${lastEnv.name}} on line ${lastEnv.line + 1}`,
							vscode.DiagnosticSeverity.Error
						);
						diagnostic.source = 'rxiv-markdown';
						diagnostic.code = 'mismatched-environment';
						diagnostics.push(diagnostic);
					}
				}
			}
		}
	}

	private checkUnclosedenvironments(
		environmentStack: Array<{name: string, line: number}>,
		currentLine: number,
		diagnostics: vscode.Diagnostic[]
	): void {
		for (const env of environmentStack) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(env.line, 0, env.line, 0),
				`Unclosed LaTeX environment '${env.name}' - missing \\end{${env.name}}`,
				vscode.DiagnosticSeverity.Error
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'unclosed-environment';
			diagnostics.push(diagnostic);
		}
	}

	private findLaTeXSyntaxIssues(code: string): Array<{
		message: string;
		severity: vscode.DiagnosticSeverity;
		code: string;
		column: number;
		length: number;
	}> {
		const issues: Array<{
			message: string;
			severity: vscode.DiagnosticSeverity;
			code: string;
			column: number;
			length: number;
		}> = [];

		// Note: Brace matching is now handled by findBraceIssues for entire blocks
		// Only check braces for inline TeX expressions here
		const isInlineExpression = !code.includes('\n');
		if (isInlineExpression) {
			let braceCount = 0;
			let lastOpenBrace = -1;
			for (let i = 0; i < code.length; i++) {
				const char = code[i];
				if (char === '{' && (i === 0 || code[i-1] !== '\\')) {
					braceCount++;
					if (braceCount === 1) { lastOpenBrace = i; }
				} else if (char === '}' && (i === 0 || code[i-1] !== '\\')) {
					braceCount--;
				}
			}

			if (braceCount > 0) {
				issues.push({
					message: 'Unmatched opening brace in LaTeX code',
					severity: vscode.DiagnosticSeverity.Error,
					code: 'unmatched-brace',
					column: lastOpenBrace,
					length: 1
				});
			} else if (braceCount < 0) {
				issues.push({
					message: 'Unmatched closing brace in LaTeX code',
					severity: vscode.DiagnosticSeverity.Error,
					code: 'unmatched-brace',
					column: 0,
					length: code.length
				});
			}
		}

		// Check for common LaTeX command issues
		const invalidCommands = code.match(/\\[0-9]/g);
		if (invalidCommands) {
			for (const invalid of invalidCommands) {
				const index = code.indexOf(invalid);
				issues.push({
					message: `Invalid LaTeX command '${invalid}' - commands cannot start with numbers`,
					severity: vscode.DiagnosticSeverity.Error,
					code: 'invalid-command',
					column: index,
					length: invalid.length
				});
			}
		}

		// Check for incomplete commands (backslash at end of line)
		if (code.endsWith('\\') && !code.endsWith('\\\\')) {
			issues.push({
				message: 'Incomplete LaTeX command at end of line',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'incomplete-command',
				column: code.length - 1,
				length: 1
			});
		}

		return issues;
	}

	private findMathExpressionIssues(mathContent: string): Array<{
		message: string;
		severity: vscode.DiagnosticSeverity;
		code: string;
	}> {
		const issues: Array<{
			message: string;
			severity: vscode.DiagnosticSeverity;
			code: string;
		}> = [];

		// Check for empty math expressions
		if (!mathContent.trim()) {
			issues.push({
				message: 'Empty math expression',
				severity: vscode.DiagnosticSeverity.Warning,
				code: 'empty-math'
			});
		}

		// Check for unbalanced delimiters in math mode
		const leftDelims = (mathContent.match(/\\left[(\[\{|]/g) || []).length;
		const rightDelims = (mathContent.match(/\\right[)\]\}|]/g) || []).length;
		
		if (leftDelims !== rightDelims) {
			issues.push({
				message: 'Unbalanced \\left and \\right delimiters in math expression',
				severity: vscode.DiagnosticSeverity.Error,
				code: 'unbalanced-delimiters'
			});
		}

		return issues;
	}

	private validateLaTeXCommand(
		command: string,
		starred: string,
		content: string,
		lineNumber: number,
		startIndex: number,
		diagnostics: vscode.Diagnostic[]
	): void {
		// Common LaTeX commands that should have non-empty content
		const commandsRequiringContent = ['textbf', 'textit', 'emph', 'caption', 'label'];
		
		if (commandsRequiringContent.includes(command) && !content.trim()) {
			const diagnostic = new vscode.Diagnostic(
				new vscode.Range(lineNumber, startIndex, lineNumber, startIndex + `\\${command}${starred}{}`.length),
				`LaTeX command '\\${command}${starred}' should not be empty`,
				vscode.DiagnosticSeverity.Warning
			);
			diagnostic.source = 'rxiv-markdown';
			diagnostic.code = 'empty-command-content';
			diagnostics.push(diagnostic);
		}

		// Check for invalid label formats
		if (command === 'label') {
			if (!content.match(/^(fig|table|eq|sfig|stable|snote):[a-zA-Z0-9_-]+$/)) {
				const diagnostic = new vscode.Diagnostic(
					new vscode.Range(lineNumber, startIndex, lineNumber, startIndex + `\\label{${content}}`.length),
					`Invalid label format '${content}'. Expected format: type:name (e.g., fig:my-figure)`,
					vscode.DiagnosticSeverity.Warning
				);
				diagnostic.source = 'rxiv-markdown';
				diagnostic.code = 'invalid-label-format';
				diagnostics.push(diagnostic);
			}
		}
	}
}