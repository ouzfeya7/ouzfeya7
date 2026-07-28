# Security Policy

## Supported Versions

This repository contains my personal GitHub profile configuration. All scripts and workflows in the `main` branch are currently supported.

## Reporting a Vulnerability

If you discover a security vulnerability within this repository (such as a leaked token or a flaw in the GitHub Actions configuration), please do not open a public issue.

Instead, please contact me privately via the email address listed on my GitHub profile. I will endeavor to respond to and address the issue as quickly as possible.

## Best Practices Implemented

- **Workflow Restrictions**: GitHub Actions are restricted to only run on the `main` branch, preventing execution from potentially malicious pull requests or branches.
- **Dependency Management**: Dependabot is configured to monitor and automatically update GitHub Actions to their latest secure versions.
- **Principle of Least Privilege**: Workflows use the minimal required token scopes to function. The default `GITHUB_TOKEN` is used for repository checkouts, and custom API queries use explicitly defined environment variables.
