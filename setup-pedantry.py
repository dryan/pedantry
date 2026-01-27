#!/usr/bin/env python3
"""Set up pedantry configs in your project by copying files."""

import json
import re
import shutil
from pathlib import Path
from typing import Annotated
from urllib.request import urlopen

import typer

app = typer.Typer(help="Set up pedantry configs in your project by copying files.")



def ensure_dir(directory: Path) -> None:
    """Create directory if it doesn't exist."""
    if not directory.exists():
        directory.mkdir(parents=True)
        typer.secho(f"  ✓ Created directory {directory}", fg=typer.colors.GREEN)


def copy_file(source: Path, target: Path) -> None:
    """Copy a file from source to target."""
    if target.exists():
        typer.secho(f"  Skipping {target} (already exists)", fg=typer.colors.YELLOW)
    else:
        shutil.copy2(source, target)
        typer.secho(f"  ✓ Copied {target}", fg=typer.colors.GREEN)


def copy_pyproject_with_project_name(source: Path, target: Path) -> None:
    """Copy pyproject.toml and set project name from the current directory."""
    if target.exists():
        typer.secho(f"  Skipping {target} (already exists)", fg=typer.colors.YELLOW)
        return

    if not source.exists():
        typer.secho(
            f"  Warning: Template pyproject.toml not found at {source}",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return

    project_name = Path.cwd().name
    content = source.read_text()

    pattern = re.compile(r"(\[project\][^\[]*?name\s*=\s*\")([^\"]+)(\")", re.DOTALL)
    match = pattern.search(content)
    if match:
        updated_content = (
            content[: match.start(2)] + project_name + content[match.end(2) :]
        )
    else:
        # Fallback to replacing the first occurrence of the name assignment.
        updated_content = content.replace(
            'name = "pedantry"', f'name = "{project_name}"', 1
        )

    target.write_text(updated_content)
    typer.secho(
        f"  ✓ Copied {target} (project name set to {project_name})",
        fg=typer.colors.GREEN,
    )


def create_eslint_config(pedantry_path: Path, target: Path) -> None:
    """Create a local ESLint config that extends the pedantry config."""
    if target.exists():
        typer.secho(f"  Skipping {target} (already exists)", fg=typer.colors.YELLOW)
        return

    # Calculate relative path from target to pedantry eslint config
    try:
        relative_path = pedantry_path.resolve() / "eslint.config.ts"
        cwd = Path.cwd().resolve()
        # Calculate relative path
        try:
            rel_path_str = relative_path.relative_to(cwd).as_posix()
        except ValueError:
            # If not relative (different drives on Windows, etc), use absolute
            rel_path_str = relative_path.as_posix()

        # Ensure it starts with ./ if it's a relative path without ..
        if not rel_path_str.startswith(".") and not rel_path_str.startswith("/"):
            rel_path_str = f"./{rel_path_str}"
    except Exception:
        # Fallback to a reasonable default
        rel_path_str = "./node_modules/pedantry/eslint.config.ts"

    content = f"""import type {{ Linter }} from "eslint";
import pedantryConfig from "{rel_path_str}";

const config: Linter.Config[] = [
  ...pedantryConfig,
  // Add your project-specific overrides here
];

export default config;
"""

    target.write_text(content)
    typer.secho(f"  ✓ Created {target}", fg=typer.colors.GREEN)


def get_dev_dependencies(pedantry_path: Path) -> list[str]:
    """Return sorted dev dependency names from the pedantry package.json."""
    package_path = pedantry_path / "package.json"
    if not package_path.exists():
        typer.secho(
            f"Warning: {package_path} not found; cannot suggest npm install command",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return []

    try:
        package_data = json.loads(package_path.read_text())
    except json.JSONDecodeError as exc:
        typer.secho(
            f"Warning: Could not parse {package_path}: {exc}",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return []

    dev_deps = package_data.get("devDependencies", {})
    return sorted(dev_deps.keys())


def has_type(project_types: list[str], type_name: str) -> bool:
    """Check if a project type is enabled."""
    return type_name in project_types


def download_gitignore_template(template_name: str) -> str:
    """Download a .gitignore template from GitHub."""
    url = f"https://raw.githubusercontent.com/github/gitignore/main/{template_name}.gitignore"
    try:
        with urlopen(url) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        typer.secho(
            f"Warning: Could not download {template_name}.gitignore: {e}",
            fg=typer.colors.YELLOW,
            err=True,
        )
        return ""


def generate_gitignore(project_types: list[str]) -> None:
    """Generate .gitignore file based on project types."""
    gitignore_path = Path(".gitignore")

    if gitignore_path.exists():
        typer.secho("  Skipping .gitignore (already exists)", fg=typer.colors.YELLOW)
        return

    typer.echo("Generating .gitignore...")

    templates = []

    # Python projects (includes Django)
    if has_type(project_types, "python") or has_type(project_types, "django"):
        templates.append("Python")

    # TypeScript/JavaScript projects
    if (
        has_type(project_types, "typescript")
        or has_type(project_types, "javascript")
        or has_type(project_types, "css")
    ):
        templates.append("Node")

    if not templates:
        typer.secho(
            "  No .gitignore templates needed for selected types",
            fg=typer.colors.YELLOW,
        )
        return

    content_parts = []
    for template in templates:
        template_content = download_gitignore_template(template)
        if template_content:
            content_parts.append(f"### {template} ###\n{template_content}")

    if content_parts:
        final_content = "\n\n".join(content_parts)
        gitignore_path.write_text(final_content)
        typer.secho("  ✓ Generated .gitignore", fg=typer.colors.GREEN)
    else:
        typer.secho(
            "  Warning: Could not generate .gitignore", fg=typer.colors.YELLOW, err=True
        )


def generate_lefthook(project_types: list[str]) -> None:
    """Generate lefthook.yml based on project types."""
    typer.echo("Generating lefthook.yml...")

    content = """pre-commit:
  parallel: false
  commands:
"""

    # Prettier - always included
    content += """    # Format files
    prettier:
      glob: "*.{js,ts,json,css,html,md,yml,yaml}"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && [ ! -L "$f" ] && echo "$f"
        done)
        echo "Sending to prettier: $FILES"
        [ -z "$FILES" ] || npx prettier --write $FILES
      stage_fixed: true

"""

    # ESLint - ts, js, django
    if (
        has_type(project_types, "typescript")
        or has_type(project_types, "javascript")
        or has_type(project_types, "django")
    ):
        content += """    # Lint JavaScript/TypeScript
    eslint:
      glob: "*.{js,ts,json}"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && echo "$f"
        done)
        [ -z "$FILES" ] || npx eslint --fix $FILES
      stage_fixed: true

"""

    # Stylelint - css, django
    if has_type(project_types, "css") or has_type(project_types, "django"):
        content += """    # Lint CSS
    stylelint:
      glob: "*.css"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && echo "$f"
        done)
        [ -z "$FILES" ] || npx stylelint --fix $FILES
      stage_fixed: true

"""

    # Ruff - python, django
    if has_type(project_types, "python") or has_type(project_types, "django"):
        content += """    # Format and lint Python (if Python files exist)
    ruff-format:
      glob: "*.py"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && echo "$f"
        done)
        [ -z "$FILES" ] || ruff format $FILES
      stage_fixed: true

    ruff-check:
      glob: "*.py"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && echo "$f"
        done)
        [ -z "$FILES" ] || ruff check --fix $FILES
      stage_fixed: true

"""

    # Vulture - python, django
    if has_type(project_types, "python") or has_type(project_types, "django"):
        content += """    # Check for dead/unused code in Python
    vulture:
      glob: "*.py"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && echo "$f"
        done)
        [ -z "$FILES" ] || uv run vulture $FILES
      stage_fixed: false # vulture only reports, doesn't fix

"""

    # Django upgrade - django only
    if has_type(project_types, "django"):
        content += (
            """    # Upgrade Django code patterns """
            """(only for Django projects)
    django-upgrade:
      glob: "*.py"
      run: |
        FILES=$(for f in {staged_files}; do
          [ -f "$f" ] && echo "$f"
        done)
        [ -z "$FILES" ] || """
            """uv run django-upgrade --target-version 5.1 $FILES
      stage_fixed: true

"""
        )

    Path("lefthook.yml").write_text(content)
    typer.secho("  ✓ Generated lefthook.yml", fg=typer.colors.GREEN)


@app.command()
def main(
    types: Annotated[
        list[str],
        typer.Option(
            "--type",
            help="Project type (can be specified multiple times)",
        ),
    ],
    pedantry_dir: Annotated[
        str,
        typer.Option(
            help="Path to pedantry directory",
        ),
    ] = ".pedantry",
) -> None:
    """Set up pedantry configs in your project by copying files.

    Examples:

        uv run --isolated --with typer .pedantry/setup-pedantry.py \
            --type python

        uv run --isolated --with typer .pedantry/setup-pedantry.py \
            --type typescript --type css

        uv run --isolated --with typer .pedantry/setup-pedantry.py \
            --type python --type django
    """
    # Validate types
    valid_types = {"python", "typescript", "javascript", "css", "django"}
    invalid_types = [t for t in types if t not in valid_types]
    if invalid_types:
        typer.secho(
            f"Error: Invalid project type(s): {', '.join(invalid_types)}",
            fg=typer.colors.RED,
            err=True,
        )
        typer.echo(f"Valid types: {', '.join(sorted(valid_types))}")
        raise typer.Exit(1)

    if not types:
        typer.secho(
            "Error: At least one --type is required", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(1)

    project_types = types
    pedantry_path = Path(pedantry_dir)

    # Check if pedantry directory exists
    if not pedantry_path.exists():
        typer.secho(
            f"Error: Pedantry directory not found: {pedantry_path}",
            fg=typer.colors.RED,
            err=True,
        )
        typer.echo("Have you added the submodule? Run:")
        typer.echo(
            f"  git submodule add "
            f"https://github.com/yourusername/pedantry.git {pedantry_path}"
        )
        raise typer.Exit(1)

    typer.secho(
        f"Setting up pedantry configs for: {', '.join(project_types)}\n",
        fg=typer.colors.GREEN,
    )

    # Common configs for all project types
    typer.echo("Setting up common configs...")
    copy_file(pedantry_path / ".editorconfig", Path(".editorconfig"))
    copy_file(pedantry_path / ".prettierrc.json5", Path(".prettierrc.json5"))
    copy_file(pedantry_path / ".prettierignore", Path(".prettierignore"))
    generate_gitignore(project_types)
    generate_lefthook(project_types)

    # VS Code settings
    typer.echo("\nSetting up VS Code configs...")
    ensure_dir(Path(".vscode"))
    copy_file(
        pedantry_path / ".vscode" / "settings.json",
        Path(".vscode") / "settings.json",
    )
    copy_file(
        pedantry_path / ".vscode" / "extensions.json",
        Path(".vscode") / "extensions.json",
    )

    # GitHub Copilot instructions
    typer.echo("\nSetting up GitHub Copilot instructions...")
    ensure_dir(Path(".github"))
    copy_file(
        pedantry_path / ".github" / "copilot-instructions.md",
        Path(".github") / "copilot-instructions.md",
    )

    # Type-specific configs
    if has_type(project_types, "typescript") or has_type(project_types, "javascript"):
        typer.echo("\nSetting up JavaScript/TypeScript configs...")
        create_eslint_config(pedantry_path, Path("eslint.config.ts"))
        copy_file(pedantry_path / "tsconfig.json", Path("tsconfig.json"))
        copy_file(pedantry_path / "vitest.config.ts", Path("vitest.config.ts"))
        copy_file(
            pedantry_path / "web-test-runner.config.js",
            Path("web-test-runner.config.js"),
        )
        copy_file(pedantry_path / "rollup.config.js", Path("rollup.config.js"))
        copy_file(
            pedantry_path / "custom-elements-manifest.config.js",
            Path("custom-elements-manifest.config.js"),
        )

    if has_type(project_types, "css"):
        typer.echo("\nSetting up CSS configs...")
        copy_file(
            pedantry_path / "stylelint.config.mjs", Path("stylelint.config.mjs")
        )

    if has_type(project_types, "python") or has_type(project_types, "django"):
        typer.echo("\nSetting up Python configs...")
        copy_pyproject_with_project_name(
            pedantry_path / "pyproject.toml", Path("pyproject.toml")
        )

    if has_type(project_types, "django"):
        typer.echo("\nSetting up Django configs...")
        # Django-specific CSS/JS if not already set up
        if not has_type(project_types, "css"):
            copy_file(
                pedantry_path / "stylelint.config.mjs", Path("stylelint.config.mjs")
            )
        if not has_type(project_types, "typescript") and not has_type(
            project_types, "javascript"
        ):
            create_eslint_config(pedantry_path, Path("eslint.config.ts"))

    typer.secho("\n✓ Pedantry setup complete!\n", fg=typer.colors.GREEN)

    # Next steps
    typer.secho("Next steps:", fg=typer.colors.YELLOW)

    step_number = 1
    has_frontend_stack = (
        has_type(project_types, "typescript")
        or has_type(project_types, "javascript")
        or has_type(project_types, "css")
        or has_type(project_types, "django")
    )

    if has_frontend_stack:
        dev_deps = get_dev_dependencies(pedantry_path)
        if dev_deps:
            packages_str = " ".join(dev_deps)
            typer.echo(f"{step_number}. Run: npm install --save-dev {packages_str}")
        else:
            typer.echo(
                f"{step_number}. Review {pedantry_path}/package.json and install "
                f"the devDependencies"
            )
        step_number += 1

    if has_type(project_types, "python") or has_type(project_types, "django"):
        typer.echo(f"{step_number}. Run: uv sync")
        step_number += 1

    typer.echo(f"{step_number}. Run: lefthook install")
    step_number += 1
    typer.echo(f"{step_number}. Commit the changes:")
    typer.echo(f"   git add .gitmodules {pedantry_path} <config-files> lefthook.yml")
    typer.echo("   git commit -m '➕ Add pedantry config submodule'")

    typer.secho("\nTo update pedantry later:", fg=typer.colors.YELLOW)
    typer.echo(f"  git submodule update --remote {pedantry_path}")
    typer.echo(f"  git add {pedantry_path}")
    typer.echo("  git commit -m '⬆️ Update pedantry configs'")


if __name__ == "__main__":
    app()
