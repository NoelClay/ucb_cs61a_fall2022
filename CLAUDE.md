# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **CS61A (UC Berkeley) course materials repository** — an educational resource for learning Structure and Interpretation of Computer Programs. The project is built as a Jekyll-based static site that's automatically deployed to GitHub Pages.

## Architecture

### Content Organization
The repository is organized into six main content categories:

- **Learning Materials**: `textbooks/`, `lecture-notes/`, `supplementary-lectures/`, `on-site-lectures/`
- **Assignments & Exams**: `assignments/`, `assignment-solutions/`, `exams/`, `exam-solutions/`
- **Personal Work**: `my-assignments/`, `my-exams/` (for student progress tracking)
- **Website**: `docs/` (Jekyll site for serving textbook as HTML)

Each directory contains a `README.md` explaining its purpose and content structure.

### Build & Deployment

**Technology Stack:**
- **Ruby 3.1** with Bundler for dependency management
- **Jekyll** for static site generation
- **GitHub Pages** for hosting
- **GitHub Actions** for CI/CD pipeline

**Deployment Flow:**
1. Changes pushed to `main` or `master` branch in `docs/` directory trigger GitHub Actions
2. Workflow (`build-deploy.yml`) builds Jekyll site in the `docs/` directory
3. Built site is deployed to GitHub Pages (https://noelclay.github.io/ucb_cs61a_fall2022)
4. The workflow also runs on `claude/*` branches for development/testing purposes

### Key Configuration

- **Jekyll Config**: `docs/_config.yml` — contains site metadata, theme (jekyll-theme-minimal), and GitHub Pages URL configuration
- **Ruby Dependencies**: `Gemfile` — bundles Jekyll, GitHub Pages support, and associated plugins
- **GitHub Workflow**: `.github/workflows/build-deploy.yml` — orchestrates build and deployment
- **Ruby Version**: 3.1 (specified in workflow and compatible with Gemfile)

## Common Commands

### Local Development

```bash
# Install dependencies (run once or after Gemfile changes)
bundle install

# Start local development server with hot-reload
cd docs && bundle exec jekyll serve

# Build for production
cd docs && bundle exec jekyll build
```

**Note**: All Jekyll commands must run from the `docs/` directory since that's where `_config.yml` and the site content are located.

### Deployment

Deployment is **automatic** when you push to `main` or `master` branches with changes in the `docs/` directory. GitHub Actions will:
1. Build the Jekyll site
2. Upload the artifact
3. Deploy to GitHub Pages

To verify the workflow, check `.github/workflows/build-deploy.yml` or visit the GitHub Actions tab.

## Important Notes for Development

### Path Structure
- The Jekyll site root is `docs/`, not the repository root
- Content pages are in `docs/` with `.md` or `.html` extensions
- Layouts are in `docs/_layouts/`
- Assets (CSS, images) are in `docs/assets/`
- The built site output goes to `docs/_site/` (ignored by git)

### Jekyll Build Environment
- **Production builds** set `JEKYLL_ENV=production` in the workflow (affects CSS/JS minification)
- **Local testing** doesn't have this env var, so minification behavior may differ
- Always test locally before pushing to verify rendering

### Markdown Content
- Pages use Jekyll front matter (YAML between `---` markers)
- The `default.html` layout provides the page structure with navigation
- All markdown files are processed through the liquid template engine

### Branching
- `main` and `master` branches trigger deployments automatically
- `claude/*` branches also trigger the build workflow (useful for testing changes)
- Pull requests on `main`/`master` also run builds (without deploying)

## Dependencies Management

If you need to:
- **Add a new Ruby gem**: Edit `Gemfile`, then run `bundle install` locally to generate `Gemfile.lock`
- **Update gems**: Run `bundle update` (ensures compatibility with GitHub Pages)
- **Check gem versions**: Run `bundle show`

Be cautious with major version upgrades, especially Jekyll and GitHub Pages, as they may affect builds.
