# HACS default store submission

Checklist for adding `doodersrage/thermaltrace-home-assistant` to [hacs/default](https://github.com/hacs/default).

## Repository requirements

- [x] Public GitHub repo with single integration under `custom_components/thermaltrace/`
- [x] Valid `manifest.json` (domain, name, version, documentation, issue_tracker, codeowners)
- [x] Root `hacs.json` with `name`
- [x] Brand assets under `custom_components/thermaltrace/brand/icon.png`
- [x] GitHub Actions: `hacs/action` + `home-assistant/actions/hassfest`
- [x] GitHub **Release** matching manifest version

## Links for PR body

- Repository: https://github.com/doodersrage/thermaltrace-home-assistant
- Latest release: https://github.com/doodersrage/thermaltrace-home-assistant/releases/latest
- CI actions: https://github.com/doodersrage/thermaltrace-home-assistant/actions/workflows/validate.yaml
- Product guide: https://thermaltrace.dev/integrations/home-assistant

## Custom install (until default merge)

```
https://github.com/doodersrage/thermaltrace-home-assistant
```

Category: **Integration**

## After merge

- Switch `HACS_BADGE_URL` in the web app from Custom → Default badge.
