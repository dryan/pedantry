#!/usr/bin/env bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
PROJECT_TYPE=""
PEDANTRY_DIR=".pedantry"

# Usage function
usage() {
    cat << EOF
Usage: $0 --type <project-type> [options]

Set up pedantry configs in your project via symlinks.

Options:
    --type TYPE         Project type: hybrid, python, typescript, javascript (required)
    --pedantry-dir DIR  Path to pedantry directory (default: .pedantry)
    --help             Show this help message

Examples:
    $0 --type hybrid
    $0 --type python
    $0 --type typescript --pedantry-dir ../pedantry

EOF
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --type)
            PROJECT_TYPE="$2"
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

# Validate project type
if [[ -z "$PROJECT_TYPE" ]]; then
    echo -e "${RED}Error: --type is required${NC}"
    usage
fi

if [[ ! "$PROJECT_TYPE" =~ ^(hybrid|python|typescript|javascript)$ ]]; then
    echo -e "${RED}Error: Invalid project type '$PROJECT_TYPE'${NC}"
    echo "Valid types: hybrid, python, typescript, javascript"
    exit 1
fi

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

echo -e "${GREEN}Setting up pedantry configs for $PROJECT_TYPE project...${NC}\n"

# Common configs for all project types
echo "Setting up common configs..."
create_symlink "$PEDANTRY_DIR/.editorconfig" ".editorconfig"
create_symlink "$PEDANTRY_DIR/lefthook.yml" "lefthook.yml"

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
case $PROJECT_TYPE in
    hybrid)
        echo -e "\nSetting up JavaScript/TypeScript configs..."
        create_symlink "$PEDANTRY_DIR/eslint.config.js" "eslint.config.js"
        create_symlink "$PEDANTRY_DIR/tsconfig.json" "tsconfig.json"
        create_symlink "$PEDANTRY_DIR/stylelint.config.mjs" "stylelint.config.mjs"
        create_symlink "$PEDANTRY_DIR/.prettierrc.json5" ".prettierrc.json5"
        create_symlink "$PEDANTRY_DIR/.prettierignore" ".prettierignore"
        create_symlink "$PEDANTRY_DIR/vitest.config.ts" "vitest.config.ts"
        create_symlink "$PEDANTRY_DIR/web-test-runner.config.js" "web-test-runner.config.js"
        create_symlink "$PEDANTRY_DIR/rollup.config.js" "rollup.config.js"
        create_symlink "$PEDANTRY_DIR/custom-elements-manifest.config.js" "custom-elements-manifest.config.js"

        echo -e "\nSetting up Python configs..."
        create_symlink "$PEDANTRY_DIR/pyproject.toml" "pyproject.toml"
        ;;

    python)
        echo -e "\nSetting up Python configs..."
        create_symlink "$PEDANTRY_DIR/pyproject.toml" "pyproject.toml"
        ;;

    typescript|javascript)
        echo -e "\nSetting up JavaScript/TypeScript configs..."
        create_symlink "$PEDANTRY_DIR/eslint.config.js" "eslint.config.js"
        create_symlink "$PEDANTRY_DIR/tsconfig.json" "tsconfig.json"
        create_symlink "$PEDANTRY_DIR/stylelint.config.mjs" "stylelint.config.mjs"
        create_symlink "$PEDANTRY_DIR/.prettierrc.json5" ".prettierrc.json5"
        create_symlink "$PEDANTRY_DIR/.prettierignore" ".prettierignore"
        create_symlink "$PEDANTRY_DIR/vitest.config.ts" "vitest.config.ts"
        create_symlink "$PEDANTRY_DIR/web-test-runner.config.js" "web-test-runner.config.js"
        create_symlink "$PEDANTRY_DIR/rollup.config.js" "rollup.config.js"
        create_symlink "$PEDANTRY_DIR/custom-elements-manifest.config.js" "custom-elements-manifest.config.js"
        ;;
esac

echo -e "\n${GREEN}✓ Pedantry setup complete!${NC}\n"

# Next steps
echo -e "${YELLOW}Next steps:${NC}"

if [[ "$PROJECT_TYPE" == "hybrid" ]] || [[ "$PROJECT_TYPE" == "typescript" ]] || [[ "$PROJECT_TYPE" == "javascript" ]]; then
    echo "1. Merge devDependencies from $PEDANTRY_DIR/package.json into your package.json"
    echo "2. Run: npm install"
fi

if [[ "$PROJECT_TYPE" == "hybrid" ]] || [[ "$PROJECT_TYPE" == "python" ]]; then
    echo "3. Run: uv sync"
fi

echo "4. Run: lefthook install"
echo "5. Commit the changes:"
echo "   git add .gitmodules $PEDANTRY_DIR <symlinked-files>"
echo "   git commit -m '➕ Add pedantry config submodule'"

echo -e "\n${YELLOW}To update pedantry later:${NC}"
echo "  git submodule update --remote $PEDANTRY_DIR"
echo "  git add $PEDANTRY_DIR"
echo "  git commit -m '⬆️ Update pedantry configs'"
