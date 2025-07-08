# Test Rxiv-Maker Syntax Highlighting

This is a test file to demonstrate the syntax highlighting features of the rxiv-maker VS Code extension.

## Cross-references

Figure references: @fig:test-figure, @sfig:supplement-figure
Table references: @table:data-table, @stable:supplement-table  
Equation references: @eq:main-equation
Supplementary notes: @snote:additional-info

## Citations

Single citation: @smith2023
Multiple citations: [@smith2023;@jones2022;@brown2021]

## Math expressions

Inline math: $E = mc^2$
Block math: $$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$$

Labeled equation:
$$\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}$$ {#eq:gauss-law}

## Scientific notation

Water molecule: H~2~O
Energy equation: E=mc^2^
Chemical formula: CO~2~

## Document control

<newpage>
<clearpage>

## Figure metadata

![Figure caption](figure.png){#fig:test-figure width="50%" tex_position="t"}

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
{#table:data-table}