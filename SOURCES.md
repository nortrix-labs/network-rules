# Feed sources and changes

- HaGeZi Multi Pro: https://github.com/hagezi/dns-blocklists (GPL-3.0).
  Input: wildcard/pro-onlydomains.txt. Copyright and source notices remain with
  the upstream project. GPL text is in LICENSE.
- anti-AD: https://github.com/privacy-protection-tools/anti-AD (MIT).
  Input: anti-ad-surge.txt. The upstream MIT notice is in licenses/anti-AD-MIT.txt.

Nortrix modifications: lowercase/IDNA normalization, duplicate and covered-child
removal, protected public service namespaces, domain-only Shadowrocket syntax.
Each build records input SHA256s, counts and the resulting feed SHA256 in
manifest.json. Build source: https://github.com/nortrix-labs/network-rules.
The combined feed and builder are distributed under GPL-3.0, retaining the
upstream MIT notice. Upstream inputs have their own contributing sources; see
their repositories for attribution and source detail.

No device configuration, server identity, private hostname or credential is
accepted as build input. This feed blocks ads/trackers by domain; it is not a
whole-device leak guard or a guarantee to remove same-origin video advertising.
