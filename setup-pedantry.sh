#!/usr/bin/env bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PROJECT_TYPES=()
PEDANTRY_DIR=".pedantry"

# Usage function
usage() {
    cat << EOF
Usage: $0 --type <project-type> [--type <project-type>...] [options]

Set up pedantry configs in your project via symlinks.

Options:
    --type TYPE         Project type: python, typescript, javascript, css, django (can be specified multiple times)
    --pedantry-dir DIR  Path to pedantry directory (default: .pedantry)
    --help             Show this help message

Examples:
    $0 --type python
    $0 --type typescript --type css
    $0 --type python --type django
    $0 --type typescript --pedantry-dir ../pedantry

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            PROJECT_TYPES+=("$2")
            shift 2
            ;;
        --pedantry-dir)
            PEDANTRY_DIR="$2"
            shift 2
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Validate project types
if [[ ${#PROJECT_TYPES[@]} -eq 0 ]]; then
    echo -e "${RED}Error: At least one --type is required${NC}"
    usage
fi

VALID_TYPES="python typescript javascript css django"
for type in "${PROJECT_TYPES[@]}"; do
    if [[ ! " $VALID_TYPES " =~ " $type " ]]; then
        echo -e "${RED}Error: Invalid project type '$type'${NC}"
        echo "Valid types: $VALID_TYPES"
        exit 1
    fi
done

# Check if pedantry directory exists
if [[ ! -d "$PEDANTRY_DIR" ]]; then
    echo -e "${RED}Error: Pedantry directory not found: $PEDANTRY_DIR${NC}"
    echo "Have you added the submodule? Run:"
    echo "  git submodule add https://github.com/yourusername/pedantry.git $PEDANTRY_DIR"
    exit 1
fi

# Function to create symlink
create_symlink() {
    local source="$1"
    local target="$2"

    if [[ -e "$target" ]] || [[ -L "$target" ]]; then
        echo -e "${YELLOW}  Skipping $target (already exists)${NC}"
    else
        ln -sf "$source" "$target"
        echo -e "${GREEN}  ✓ Linked $target${NC}"
    fi
}

# Function to create directory if needed
ensure_dir() {
    local dir="$1"
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        echo -e "${GREEN}  ✓ Created directory $dir${NC}"
    fi
}

# Function to check if a project type is enabled
has_type() {
    local type="$1"
    for t in "${PROJECT_TYPES[@]}"; do
        if [[ "$t" == "$type" ]]; then
            return 0
        fi
    done
    return 1
}

# Function to generate lefthook.yml based on project types
generate_lefthook() {
    echo "Generating lefthook.yml..."
    cat > lefthook.yml << 'EOF'
pre-commit:
  parallel: false
  commands:
EOF

    # Prettier - always included
    cat >> lefthook.yml << 'EOF'
    # Format files
    prettier:
      glob: "*.{js,ts,json,css,html,md,yml,yaml}"
      run: for f in {staged_files}; do [ ! -L "$f" ] && npx prettier --write "$f"; done || true
      stage_fixed: true

EOF

    # ESLint - ts, js, django
    if has_type "typescript" || has_type "javascript" || has_type "django"; then
        cat >> lefthook.yml << 'EOF'
    # Lint JavaScript/TypeScript
    eslint:
      glob: "*.{js,ts,json}"
      run: npx eslint --fix {staged_files}
      stage_fixed: true

EOF
    fi

    # Stylelint - css, django
    if has_type "css" || has_type "django"; then
        cat >> lefthook.yml << 'EOF'
    # Lint CSS
    stylelint:
      glob: "*.css"
      run: npx stylelint --fix {staged_files}
      stage_fixed: true

EOF
    fi

    # Ruff - python, django
    if has_type "python" || has_type "django"; then
        cat >> lefthook.yml << 'EOF'
    # Format and lint Python (if Python files exist)
    ruff-format:
      glob: "*.py"
      run: ruff format {staged_files}
      stage_fixed: true

    ruff-check:
      glob: "*.py"
      run: ruff check --fix {staged_files}
      stage_fixed: true

EOF
    fi

    # Vulture - python, django
    if has_type "python" || has_type "django"; then
        cat >> lefthook.yml << 'EOF'
    # Check for dead/unused code in Python
    vulture:
      glob: "*.py"
      run: uv run vulture {staged_files}
      stage_fixed: false # vulture only reports, doesn't fix

EOF
    fi

    # Django upgrade - django only
    if has_type "django"; then
        cat >> lefthook.yml << 'EOF'
    # Upgrade Django code patterns (only for Django projects)
    django-upgrade:
      glob: "*.py"
      run: uv run django-upgrade --target-version 5.1 {staged_files}
      stage_fixed: true

EOF
    fi

    echo -e "${GREEN}  ✓ Generated lefthook.yml${NC}"
}

echo -e "${GREEN}Setting up pedantry configs for: ${PROJECT_TYPES[*]}${NC}\n"

# Common configs for all project types
echo "Setting up common configs..."
create_symlink "$PEDANTRY_DIR/.editorconfig" ".editorconfig"
generate_lefthook

# VS Code settings
echo -e "\nSetting up VS Code configs..."
ensure_dir ".vscode"
create_symlink "../$PEDANTRY_DIR/.vscode/settings.json" ".vscode/settings.json"
create_symlink "../$PEDANTRY_DIR/.vscode/extensions.json" ".vscode/extensions.json"

# GitHub Copilot instructions
echo -e "\nSetting up GitHub Copilot instructions..."
ensure_dir ".github"
create_symlink "../$PEDANTRY_DIR/.github/copilot-instructions.md" ".github/copilot-instructions.md"

# Type-specific configs
if has_type "typescript" || has_type "javascript"; then
    echo -e "\nSetting up JavaScript/TypeScript configs..."
    create_symlink "$PEDANTRY_DIR/eslint.config.js" "eslint.config.js"
    create_symlink "$PEDANTRY_DIR/tsconfig.json" "tsconfig.json"
    create_symlink "$PEDANTRY_DIR/.prettierrc.json5" ".prettierrc.json5"
    create_symlink "$PEDANTRY_DIR/.prettierignore" ".prettierignore"
    create_symlink "$PEDANTRY_DIR/vitest.config.ts" "vitest.config.ts"
    create_symlink "$PEDANTRY_DIR/web-test-runner.config.js" "web-test-runner.config.js"
    create_symlink "$PEDANTRY_DIR/rollup.config.js" "rollup.config.js"
    create_symlink "$PEDANTRY_DIR/custom-elements-manifest.config.js" "custom-elements-manifest.config.js"
fi

if has_type "css"; then
    echo -e "\nSetting up CSS configs..."
    create_symlink "$PEDANTRY_DIR/stylelint.config.mjs" "stylelint.config.mjs"
fi

if has_type "python" || has_type "django"; then
    echo -e "\nSetting up Python configs..."
    create_symlink "$PEDANTRY_DIR/pyproject.toml" "pyproject.toml"
fi

if has_type "django"; then
    echo -e "\nSetting up Django configs..."
    # Django-specific CSS/JS if not already set up
    if ! has_type "css"; then
        create_symlink "$PEDANTRY_DIR/stylelint.config.mjs" "stylelint.config.mjs"
    fi
    if ! has_type "typescript" && ! has_type "javascript"; then
        create_symlink "$PEDANTRY_DIR/eslint.config.js" "eslint.config.js"
        create_symlink "$PEDANTRY_DIR/.prettierrc.json5" ".prettierrc.json5"
        create_symlink "$PEDANTRY_DIR/.prettierignore" ".prettierignore"
    fi
fi

echo -e "\n${GREEN}✓ Pedantry setup complete!${NC}\n"

# Next steps
echo -e "${YELLOW}Next steps:${NC}"

if has_type "typescript" || has_type "javascript" || has_type "css" || has_type "django"; then
    echo "1. Merge devDependencies from $PEDANTRY_DIR/package.json into your package.json"
    echo "2. Run: npm install"
fi

if has_type "python" || has_type "django"; then
    echo "3. Run: uv sync"
fi

echo "4. Run: lefthook install"
echo "5. Commit the changes:"
echo "   git add .gitmodules $PEDANTRY_DIR <symlinked-files> lefthook.yml"
echo "   git commit -m '➕ Add pedantry config submodule'"

echo -e "\n${YELLOW}To update pedantry later:${NC}"
echo "  git submodule update --remote $PEDANTRY_DIR"
echo "  git add $PEDANTRY_DIR"
echo "  git commit -m '⬆️ Update pedantry configs'"
