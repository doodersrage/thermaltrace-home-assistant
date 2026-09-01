# HACS default store submission

Checklist for adding `doodersrage/thermatrace-HACS-component` to [hacs/default](https://github.com/hacs/default).

## Repository requirements

- [x] Public GitHub repo with single integration under `custom_components/thermaltrace/`
- [x] Valid `manifest.json` (domain, name, version, documentation, issue_tracker, codeowners)
- [x] Root `hacs.json` with `name`
- [x] Brand assets: `custom_components/thermaltrace/icon.png` and `brand/icon.png`
- [x] GitHub Actions: `hacs/action` + `home-assistant/actions/hassfest`
- [x] GitHub **Release** (not tag-only) for version in manifest (`1.0.0`)

## Before opening the PR

1. Confirm the latest [Validate workflow](https://github.com/doodersrage/thermatrace-HACS-component/actions) passes on `main`.
2. Confirm [release v1.0.0](https://github.com/doodersrage/thermatrace-HACS-component/releases) exists and matches manifest version.
3. Fork `hacs/default` from your **personal** GitHub account (org forks are not accepted for editable PRs).

## Open the PR

1. Clone your fork of `hacs/default`.
2. Edit the `integration` file (JSON array of `"owner/repo"` strings).
3. Add `"doodersrage/thermatrace-HACS-component"` in alphabetical order.
4. Open a PR with:
   - Link to integration repo
   - Link to product guide: https://thermaltrace.dev/integrations/home-assistant
   - Note: repo name uses historical `thermatrace` typo; domain is `thermaltrace`.

## After merge

- Update `HACS_BADGE_URL` in `thermaltrace` web app from Custom → Default badge.
- Update HA integration page copy (“default store listing submitted” → “available in HACS default”).

## Custom install (until merged)

Users add custom repository:

```
https://github.com/doodersrage/thermatrace-HACS-component
```

Category: **Integration**
