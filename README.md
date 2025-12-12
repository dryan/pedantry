# Pedantry

Opinionated linting and formatting configurations for TypeScript, JavaScript, CSS, HTML, and Python projects. Optimized for Web Components (vanilla and Lit), with support for hybrid Python/JavaScript projects.

## What's Included

### JavaScript/TypeScript

- **ESLint** (flat config) with TypeScript support
- **Prettier** (defaults only)
- **TypeScript** configuration with decorators for Web Components
- Path aliases (`@/*`, `@components/*`, etc.)
- Web Components and Lit optimizations

### CSS

- **Stylelint** with standard config and property ordering
- Web Components Shadow DOM support (`:host`, `::slotted`, `::part`)
- CSS custom properties validation

### Python

- **Ruff** for linting and formatting (replaces Black, isort, flake8, pyupgrade)
- **Pyright** for type checking (via `ty` CLI)
- **Vulture** for dead code detection
- **django-upgrade** for Django code modernization (Django projects only)
- **pytest** configuration
- Type checking with modern Python syntax

### Build & Testing

- **Rollup** configuration for Web Components
- **@web/test-runner** for cross-browser testing
- **Custom Elements Manifest** generation

### Git Hooks

- **Lefthook** for fast, reliable pre-commit hooks
- Auto-formatting and linting on commit

### Editor

- **VS Code** settings and extension recommendations
- **EditorConfig** for consistent formatting
- CSS custom data for Web Components pseudo-elements

## Installation

### Method 1: Git Submodule (Recommended)

Add pedantry as a submodule to stay in sync with updates:

**1. Add the submodule:**

```bash
cd your-project
git submodule add https://github.com/yourusername/pedantry.git .pedantry
```

**2. Run the setup script:**

```bash
# For hybrid Python + TypeScript/JavaScript projects
.pedantry/setup-pedantry.sh --type hybrid

# For Python-only projects
.pedantry/setup-pedantry.sh --type python

# For TypeScript/JavaScript-only projects
.pedantry/setup-pedantry.sh --type typescript
```

The script creates symlinks to all necessary config files.

**3. Merge dependencies:**

Merge `devDependencies` from `.pedantry/package.json` into your `package.json`, then:

```bash
npm install      # Install JavaScript dependencies
uv sync          # Install Python dependencies (if Python project)
lefthook install # Set up git hooks
```

**4. Commit the setup:**

```bash
git add .gitmodules .pedantry <symlinked-files>
git commit -m "➕ Add pedantry config submodule"
```

**Updating pedantry:**

```bash
git submodule update --remote .pedantry
git add .pedantry
git commit -m "⬆️ Update pedantry configs"
```

**Cloning projects with the submodule:**

```bash
git clone --recurse-submodules <your-repo-url>
# or if already cloned:
git submodule update --init --recursive
```

### Method 2: Copy Files Directly

Copy the configuration files you need to your project:

```bash
# Core configs (always needed)
cp package.json tsconfig.json eslint.config.js .prettierrc.json5 .prettierignore .editorconfig lefthook.yml <your-project>/

# CSS (if using)
cp stylelint.config.mjs <your-project>/

# Python (if using)
cp pyproject.toml <your-project>/

# Build tools (if needed)
cp rollup.config.js vitest.config.ts web-test-runner.config.js custom-elements-manifest.config.js <your-project>/

# VS Code settings
cp -r .vscode <your-project>/

# Copilot instructions
cp -r .github <your-project>/
```

Then install dependencies:

```bash
npm install      # Install JavaScript dependencies
uv sync          # Install Python dependencies (if Python project)
lefthook install # Set up git hooks
```

**Python dependencies (if using Python):**

```bash
# Using uv (recommended)
uv add --dev ruff pytest

# Install ty for type checking (globally recommended)
pip install ty
# or via pipx for isolation
pipx install ty

# Or using pip
pip install ruff pytest
```

## Customization

**Update `package.json`:**

- Change `name`, `description`, `author`, `license`
- Remove unused dependencies
- Adjust scripts as needed

**Update `tsconfig.json`:**

- Adjust `target` and `lib` for your browser/Node.js support
- Modify path aliases
- Change `include`/`exclude` patterns
- Add/remove compiler options

**Update `eslint.config.js`:**

- Add framework-specific plugins if needed
- Adjust rules for your preferences
- Modify file patterns and ignores

**Update `pyproject.toml`:**

- Change Python version target
- Adjust Ruff rules
- Modify pytest configuration
- Configure Pyright type checking mode (`basic`, `standard`, or `strict`)
- Adjust Pyright report settings for your strictness preference

## Usage

### Linting

```bash
# Lint everything
npm run lint

# Lint and fix everything
npm run lint:fix

# Lint specific languages
npm run lint:js
npm run lint:css
npm run lint:py

# Fix specific languages
npm run lint:js:fix
npm run lint:css:fix
npm run lint:py:fix

# Python type checking
uv run ty           # Type check Python code
uv run ty --watch   # Watch mode

# Python dead code detection
uv run vulture src/ # Find unused code

# Django code upgrades (Django projects only)
uv run django-upgrade --target-version 5.1 src/**/*.py
```

### Formatting

```bash
# Format all files
npm run format
```

### Testing

```bash
# Run Node.js/TypeScript tests (Vitest)
npm test              # Watch mode
npm run test:run      # Single run
npm run test:coverage # With coverage
npm run test:ui       # Interactive UI

# Run browser-based Web Component tests
npm run test:browser  # @web/test-runner

# Run Python tests
pytest
```

### Building

```bash
# Build with Rollup
npm run build

# Generate Custom Elements Manifest
npm run analyze
```

## TypeScript Path Aliases

The following path aliases are configured by default:

- `@/*` → `src/*`
- `~/*` → `src/*`
- `@components/*` → `src/components/*`
- `@utils/*` → `src/utils/*`
- `@styles/*` → `src/styles/*`
- `@types/*` → `src/types/*`

Adjust these in `tsconfig.json` to match your project structure.

## Test Runners

This configuration includes **two test runners** for different use cases:

### Vitest (Default for Node.js/TypeScript)

**Included by default.** Fast, modern test runner with excellent TypeScript and ESM support.

**Features:**

- Jest-compatible API
- Native TypeScript support
- Fast watch mode with smart re-running
- Built-in coverage (v8)
- Optional UI mode
- Works great even if you're not using Vite for builds

**Usage:**

```bash
npm test              # Watch mode
npm run test:run      # Single run
npm run test:coverage # With coverage report
npm run test:ui       # Interactive UI
```

**Configuration:** `vitest.config.ts`

### @web/test-runner (For Browser-Based Tests)

**For Web Components that need real browser environments.**

**Features:**

- Tests in real browsers (Chromium, Firefox, WebKit)
- Real Shadow DOM and Custom Elements
- Playwright integration
- Cross-browser testing

**Usage:**

```bash
npm run test:browser
```

**Configuration:** `web-test-runner.config.js`

### Alternative Test Runners

If Vitest doesn't fit your needs:

- **Jest** - More mature, wider ecosystem, but slower and ESM is tricky
- **Node.js Test Runner** - Built-in to Node 18+, zero dependencies, minimal features
- **uvu** - Extremely fast, minimal API, tiny footprint

## HTML Linting

HTML linting requirements vary by project type. **Before setting up HTML linting, determine:**

1. **Django projects**: Use `djlint`
2. **11ty projects**: Use `htmlhint` or `html-validate`
3. **Web Components**: HTML is in template literals (covered by ESLint)
4. **Static HTML**: Use `htmlhint` or `html-validate`

**Ask me about your project type and I'll set up appropriate HTML linting!**

## Project Types

This configuration supports:

### Web Components (Vanilla)

- Standard Custom Elements API
- Shadow DOM
- TypeScript with decorators
- No framework dependencies

### Web Components (Lit)

- Lit decorators (`@customElement`, `@property`, etc.)
- Reactive properties
- Template literals with `html` and `css`
- Shadow DOM

### Python Only

- Modern Python (3.11+)
- Type hints with Pyright type checking
- Ruff for linting and formatting
- pytest for testing

### Hybrid Python + JavaScript

- FastAPI + Web Components
- Django + Web Components
- Flask + Web Components
- Any Python backend + JavaScript frontend

## Python Type Checking

This configuration includes **Pyright** for static type checking, accessed through the `ty` CLI.

### What is ty?

`ty` is a lightweight CLI wrapper around Pyright that provides:

- Faster startup than the full Pyright npm package
- Simple, focused interface
- Watch mode for continuous type checking
- Integration with `pyproject.toml` configuration

### Using ty

```bash
# Type check your Python code
uv run ty

# Watch mode (re-check on file changes)
uv run ty --watch

# Check specific files or directories
uv run ty src/
uv run ty src/module.py
```

### Configuration

Type checking is configured in `pyproject.toml` under `[tool.pyright]`:

**Type checking modes:**

- `off` - No type checking
- `basic` - Basic type checking (recommended for most projects)
- `standard` - Default Pyright strictness (included in this config)
- `strict` - Maximum strictness

**Adjusting strictness:**

For stricter checking, uncomment additional report options in `pyproject.toml`:

```toml
[tool.pyright]
typeCheckingMode = "strict"  # or "basic", "standard"

# Uncomment for more strictness
reportConstantRedefinition = true
reportIncompatibleMethodOverride = true
reportUntypedFunctionDecorator = true
```

### VS Code Integration

Pyright is built into the Python extension for VS Code, so type errors will appear inline automatically. The `ty` CLI is useful for:

- CI/CD pipelines
- Pre-commit hooks (if desired)
- Command-line type checking
- Editor-agnostic workflows

## VS Code Extensions

Recommended extensions (see `.vscode/extensions.json`):

- Prettier - Code formatter
- ESLint
- Stylelint
- EditorConfig
- Ruff
- Pylance (includes Pyright for Python type checking)
- lit-html (syntax highlighting)
- lit-plugin (Lit-specific features)

Install them with: `Extensions: Show Recommended Extensions`

## Pre-Commit Hooks

Lefthook runs these on `pre-commit`:

1. **Prettier** - Format staged files
2. **ESLint** - Lint and fix JavaScript/TypeScript
3. **Stylelint** - Lint and fix CSS
4. **Ruff** - Format and lint Python

All fixes are automatically staged.

To skip hooks (not recommended):

```bash
git commit --no-verify
```

## Verification

After setup, verify everything works:

```bash
# Check for issues
npm run lint

# Fix all auto-fixable issues
npm run lint:fix

# Format all files
npm run format

# Type check Python code (if using Python)
uv run ty

# Test git hooks (without committing)
lefthook run pre-commit
```

## Customization Tips

### Adding Framework Support

**For React, Vue, etc. (not recommended for Web Components projects):**

```bash
npm install -D eslint-plugin-react
```

Update `eslint.config.js` accordingly.

### Strict TypeScript

Enable more strict options in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,
    "noPropertyAccessFromIndexSignature": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### Additional Ruff Rules

Enable more rules in `pyproject.toml`:

```toml
[tool.ruff.lint]
select = [
    "E", "W", "F", "I", "N", "UP", "B", "C4", "SIM",
    "TCH",   # flake8-type-checking
    "PTH",   # flake8-use-pathlib
    "RUF",   # Ruff-specific rules
    "PERF",  # Performance linting
]
```

## Troubleshooting

### TypeScript errors about missing modules

If you see "Cannot find module" errors in the config files, this is expected before running `npm install`. The dependencies are listed in `package.json` but not installed yet. Run:

```bash
npm install
```

### Lefthook not running

```bash
lefthook install
```

### ESLint errors with JSON files

Ensure `@eslint/json` is installed and configured in `eslint.config.js`.

### Stylelint errors with Web Components pseudo-elements

The config includes rules for `:host`, `::slotted`, and `::part`. If you see errors, check `stylelint.config.mjs`.

### Python imports not resolving

Ensure you have a virtual environment activated and dependencies installed.

### TypeScript path aliases not working

1. Check `tsconfig.json` `paths` configuration
2. If using a bundler, configure it to resolve the same paths
3. For Rollup, use `@rollup/plugin-alias`

## License

ISC (or adjust to your preference)

## Contributing

This is a personal configuration template. Fork and customize for your own needs!
