---
connector: superpowers
active: false
installed: false
---
## Config
install_command: claude plugin install superpowers@claude-plugins-official
## Notes
Set active: true once Superpowers is installed.
orchestrate will check this file before invoking superpowers skills.
If installed: false, orchestrate will offer to install on first use.
Install via the official registry only — never git clone from an arbitrary URL.
