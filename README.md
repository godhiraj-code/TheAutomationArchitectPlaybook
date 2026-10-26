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

**Part II: Visual testing**

4. Visual Guard: visual regression testing

**Part III: Authentication optimization**

5. The hidden cost of authentication
6. Selenium Teleport: browser state restoration

**Part IV: Stealth and bot detection**

7. Understanding modern bot detection
8. SB Stealth Wrapper

**Part V: Modern web architectures**

9. Understanding Shadow DOM
10. Lumos ShadowDOM

**Part VI: AI and intelligent automation**

11. Selector Scout: AI generated locators (design sketch, not yet published)
12. Testing GenAI chatbots with Selenium
13. pytest-mockllm: testing AI features without API costs

**Part VII: Visual automation**

14. Visual Sonar: automating remote desktops
15. Project Vandal: UI mutation testing

**Part VIII: Reporting**

16. pytest-glow-report

**Part IX: Enterprise patterns**

17. The four layer architecture
18. CI/CD integration patterns

**Part X: Specialized environments**

19. Windows Virtual Desktop

**Part XI: Advanced topics**

20. Effort estimation for automation projects
21. SQL for automation testers
22. Legacy lessons from UFT/QTP
23. AI powered testing with privacy first local SLMs
24. The Sentinel: toward autonomous quality agents
25. Constellation based automation: the Milky Way strategy

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
