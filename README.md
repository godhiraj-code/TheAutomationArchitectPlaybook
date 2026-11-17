# The Automation Architect's Playbook

A practical guide for test engineers who want to move from single test scripts to
automation systems they can trust. It explains how browsers really behave, why
tests flake, and how to fix waiting, visual checks, login cost, Shadow DOM, AI
features and reporting, with open source Python tools you can install today.

**Read it online:** https://www.dhirajdas.dev/automation-book

That web edition is the maintained one. This repository keeps the source:
`book_final.md` (Markdown) and `index.html` (the styled web page, which points
search engines to the web edition with a canonical link).

## Contents

**Part I: Foundations**

1. How browsers actually work
2. The anatomy of a flaky test
3. Waitless: intelligent stability detection
4. Visual Guard: visual regression testing

**Part II: Access: login and bot detection**

5. The hidden cost of authentication
6. Selenium Teleport: browser state restoration
7. Understanding modern bot detection
8. SB Stealth Wrapper

**Part III: Modern web architectures**

9. Understanding Shadow DOM
10. Lumos ShadowDOM

**Part IV: AI and intelligent automation**

11. Selector Scout: AI-generated locators (preview, not yet published)
12. Testing GenAI chatbots with Selenium
13. pytest-mockllm: testing AI features without API costs

**Part V: Proving what happened**

14. Visual Sonar: automating remote desktops
15. Project Vandal: UI mutation testing
16. pytest-glow-report

**Part VI: Building and running a framework**

17. The four-layer architecture
18. CI/CD integration patterns
19. Effort estimation for automation projects
20. SQL for automation testers
21. Legacy lessons from UFT/QTP

**Part VII: Testing AI systems and agents**

22. Testing AI systems in three layers
23. The Sentinel: toward autonomous quality agents
24. Constellation-based automation: the Milky Way strategy

Appendix A lists every tool with its install name, source code and article.

## Check and build

You need Python 3 (CI uses 3.11). The scripts use only the standard library and
make no network requests.

Check the book:

```bash
python scripts/book.py check
```

This checks that Markdown code fences are balanced, local links and images
exist, HTML ids are unique, internal anchors resolve, every chapter in the
Markdown is in the web page, and the page has an HTML5 doctype.

Build the static site:

```bash
python scripts/book.py build --output dist
```

The build runs the checks, copies `index.html` and `assets/` into a new or
empty folder, and writes `build-manifest.json` with SHA-256 hashes. It refuses
folders that are not empty, and inside the repository it only writes to
`./dist`. Two builds of the same commit are identical. CI runs the same steps
on every push and pull request.

To preview the result, serve the folder:

```bash
python -m http.server --directory dist 8000
```
