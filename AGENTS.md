# Public feed working rules

- Branch and PR for source changes. This is a public repository: domain list
  sources and build code only, never populated device configs or credentials.
- Standard-library Python only. Pin action revisions. PR jobs cannot publish.
- Publication belongs to GitHub Actions on main; feed is generated output.
- Keep input-size, parser, protected-domain and previous-build drift checks.
- No local cron, device background builder, MITM certificate or DNS replacement.
