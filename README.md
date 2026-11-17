# Nortrix network rules

Public, domain-only ad/tracker feed for Shadowrocket. The builder merges HaGeZi
Multi Pro and anti-AD, removes duplicates/covered children, and excludes protected
public service namespaces. It never reads device configs, proxy credentials or
private network inventory. No HTTPS interception or DNS change is required.

Subscription (DOMAIN-SET, not a complete config):

```ini
DOMAIN-SET,https://raw.githubusercontent.com/nortrix-labs/network-rules/feed/ads.list,REJECT
```

Keep your own main config. Add the subscription before broad AI/shared-service
and FINAL routing, with private network routes and narrow intentional exceptions
preserved. Protected API/login namespaces are excluded from the feed, so their
existing routes keep choosing the intended proxy. Generic telemetry shared by
AI and other apps can still be blocked. Check native rule decisions before use.

GitHub Actions builds daily at 12:23 UTC / 20:23 Hong Kong time, on main pushes,
and by manual dispatch. Schedule times can be delayed by GitHub. Publishing runs
only from main, after tests. Invalid/truncated input, excessive size, large count
drift or failed checks stops publication; the previous feed branch stays usable.
Metadata and input hashes: replace ads.list in the URL with manifest.json.

Shadowrocket: Settings → Update → Config → Auto Background Update → 1 day.
Each device downloads independently. iCloud shares configuration references;
it does not make a powered-off Mac perform the phone's refresh. iOS scheduling
is best effort; reopen the app after reboot/force-quit and refresh before travel.
Neither macOS cron nor a Shadowrocket cron builder is installed.

Development: `python3 -m unittest -v`, then `python3 build.py --output output`.
Source changes use a PR; generated data is published on feed. Review upstream
format or count changes before relaxing validation. To recover a bad rule update,
restore a reviewed feed commit and fix the source/protected list before another
build; clients must then refresh their cached copy. Do not replace a main device
config with this feed. Real-world ad effectiveness and false positives vary.

See SOURCES.md, LICENSE and licenses/ for provenance, modifications and notices.
