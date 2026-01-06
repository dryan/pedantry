#!/usr/bin/env python3
"""Set up pedantry configs in your project via symlinks."""

import shutil
from pathlib import Path
from typing import Annotated
from urllib.request import urlopen

import typer

app = typer.Typer(help="Set up pedantry configs in your project via symlinks.")


def create_symlink(source: Path, target: Path) -> None:
    """Create a symlink from source to target."""
    if target.exists() or target.is_symlink():
        typer.secho(f"  Skipping {target} (already exists)", fg=typer.colors.YELLOW)
    else:
        target.symlink_to(source)
        typer.secho(f"  ✓ Linked {target}", fg=typer.colors.GREEN)


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
        for f in {staged_files}; do
          [ ! -L "$f" ] && npx prettier --write "$f"
        done || true
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
      run: npx eslint --fix {staged_files}
      stage_fixed: true

"""

    # Stylelint - css, django
    if has_type(project_types, "css") or has_type(project_types, "django"):
        content += """    # Lint CSS
    stylelint:
      glob: "*.css"
      run: npx stylelint --fix {staged_files}
      stage_fixed: true

"""

    # Ruff - python, django
    if has_type(project_types, "python") or has_type(project_types, "django"):
        content += """    # Format and lint Python (if Python files exist)
    ruff-format:
      glob: "*.py"
      run: ruff format {staged_files}
      stage_fixed: true

    ruff-check:
      glob: "*.py"
      run: ruff check --fix {staged_files}
      stage_fixed: true

"""

    # Vulture - python, django
    if has_type(project_types, "python") or has_type(project_types, "django"):
        content += """    # Check for dead/unused code in Python
    vulture:
      glob: "*.py"
      run: uv run vulture {staged_files}
      stage_fixed: false # vulture only reports, doesn't fix

"""

    # Django upgrade - django only
    if has_type(project_types, "django"):
        content += """    # Upgrade Django code patterns (only for Django projects)
    django-upgrade:
      glob: "*.py"
      run: uv run django-upgrade --target-version 5.1 {staged_files}
      stage_fixed: true

"""

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
    """Set up pedantry configs in your project via symlinks.

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
    create_symlink(pedantry_path / ".editorconfig", Path(".editorconfig"))
    create_symlink(pedantry_path / ".prettierrc.json5", Path(".prettierrc.json5"))
    create_symlink(pedantry_path / ".prettierignore", Path(".prettierignore"))
    generate_gitignore(project_types)
    generate_lefthook(project_types)

    # VS Code settings
    typer.echo("\nSetting up VS Code configs...")
    ensure_dir(Path(".vscode"))
    create_symlink(
        Path("..") / pedantry_path / ".vscode" / "settings.json",
        Path(".vscode") / "settings.json",
    )
    create_symlink(
        Path("..") / pedantry_path / ".vscode" / "extensions.json",
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
        create_symlink(pedantry_path / "eslint.config.js", Path("eslint.config.js"))
        create_symlink(pedantry_path / "tsconfig.json", Path("tsconfig.json"))
        create_symlink(pedantry_path / "vitest.config.ts", Path("vitest.config.ts"))
        create_symlink(
            pedantry_path / "web-test-runner.config.js",
            Path("web-test-runner.config.js"),
        )
        create_symlink(pedantry_path / "rollup.config.js", Path("rollup.config.js"))
        create_symlink(
            pedantry_path / "custom-elements-manifest.config.js",
            Path("custom-elements-manifest.config.js"),
        )

    if has_type(project_types, "css"):
        typer.echo("\nSetting up CSS configs...")
        create_symlink(
            pedantry_path / "stylelint.config.mjs", Path("stylelint.config.mjs")
        )

    if has_type(project_types, "python") or has_type(project_types, "django"):
        typer.echo("\nSetting up Python configs...")
        create_symlink(pedantry_path / "pyproject.toml", Path("pyproject.toml"))

    if has_type(project_types, "django"):
        typer.echo("\nSetting up Django configs...")
        # Django-specific CSS/JS if not already set up
        if not has_type(project_types, "css"):
            create_symlink(
                pedantry_path / "stylelint.config.mjs", Path("stylelint.config.mjs")
            )
        if not has_type(project_types, "typescript") and not has_type(
            project_types, "javascript"
        ):
            create_symlink(pedantry_path / "eslint.config.js", Path("eslint.config.js"))

    typer.secho("\n✓ Pedantry setup complete!\n", fg=typer.colors.GREEN)

    # Next steps
    typer.secho("Next steps:", fg=typer.colors.YELLOW)

    if (
        has_type(project_types, "typescript")
        or has_type(project_types, "javascript")
        or has_type(project_types, "css")
        or has_type(project_types, "django")
    ):
        typer.echo(
            f"1. Merge devDependencies from {pedantry_path}/package.json "
            f"into your package.json"
        )
        typer.echo("2. Run: npm install")

    if has_type(project_types, "python") or has_type(project_types, "django"):
        typer.echo("3. Run: uv sync")

    typer.echo("4. Run: lefthook install")
    typer.echo("5. Commit the changes:")
    typer.echo(f"   git add .gitmodules {pedantry_path} <symlinked-files> lefthook.yml")
    typer.echo("   git commit -m '➕ Add pedantry config submodule'")

    typer.secho("\nTo update pedantry later:", fg=typer.colors.YELLOW)
    typer.echo(f"  git submodule update --remote {pedantry_path}")
    typer.echo(f"  git add {pedantry_path}")
    typer.echo("  git commit -m '⬆️ Update pedantry configs'")


if __name__ == "__main__":
    app()
