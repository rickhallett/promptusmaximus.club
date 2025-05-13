---
description: Guidelines for AI assistant behavior and conventions within the project.
globs: '*'
alwaysApply: true
---

# AI Assistant Conventions

This document outlines specific conventions and expectations for the AI assistant working on this project.

## Commit Messages

-   **Auto-Generation:** The AI assistant is expected to **auto-generate conventional commit messages** for changes it implements or helps implement.
-   **Format:** Commit messages should follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification (e.g., `type(scope): description`).
-   **Clarity:** The generated message should accurately and concisely describe the changes made.
-   **Confirmation:** If the AI is uncertain about an appropriate message (e.g., for complex or multi-faceted changes), it should propose a message and ask the user for confirmation or clarification before committing.

## Workflow Integration

-   The AI should integrate its actions smoothly into the established development workflow (see [`dev_workflow.mdc`](mdc:.cursor/rules/dev_workflow.md)).
-   This includes using project-specific tools and adhering to task management processes where applicable. 