import { defineConfig } from '@vscode/test-cli';

export default defineConfig({
	label: 'unitTests',
	files: 'out/test/**/*.test.js',
	// Pin to the minimum supported VS Code (matches engines.vscode in
	// package.json) so tests run against the floor we claim to support and
	// CI is not silently affected by stable-channel updates.
	version: '1.101.0',
	mocha: {
		ui: 'tdd',
		timeout: 20000,
	},
});
