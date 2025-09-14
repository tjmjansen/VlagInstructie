# 🇳🇱 Dutch Flag Instruction (Vlaginstructie Nederland)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/use/custom_repositories/)

A Home Assistant integration that automatically fetches the official **Dutch flag instruction** from the [Government of the Netherlands](https://www.rijksoverheid.nl/onderwerpen/grondwet-en-statuut/vraag-en-antwoord/wanneer-kan-ik-de-vlag-uithangen-en-wat-is-de-vlaginstructie).  
It tells you exactly when to raise the Dutch flag, whether it should be flown at half-mast, and when to use the orange pennant.

---

## ✨ Features

- ✅ Sensor `sensor.vlaginstructie` → name of the occasion or “No flag instruction”
- ✅ Binary sensor `binary_sensor.vlag_uithangen_today` → true if today is a flag day
- ✅ Binary sensor `binary_sensor.vlag_halfstok_today` → true if the flag should be flown at half-mast
- ✅ Automatic scraping & caching of official government website
- ✅ Calculates variable days (Veterans Day and Prinsjesdag)

---

## 📦 Installation

### Via HACS (Custom Repository)
1. Open HACS in Home Assistant
2. Go to **Integrations**
3. Click **⋮ → Custom repositories**
4. Add this repository as an integration
5. Search for **Dutch Flag Instruction** in HACS and install

### Manual installation
1. Download this repository as a ZIP
2. Copy the folder `custom_components/vlaginstructie/` into your Home Assistant `custom_components/` directory
3. Restart Home Assistant

---

## ⚙️ Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: vlaginstructie

binary_sensor:
  - platform: vlaginstructie

```

### Restart Home Assistant. You’ll then have:
```
sensor.vlaginstructie
binary_sensor.vlag_uithangen_today
binary_sensor.vlag_halfstok_today
```

## 🛠 Troubleshooting

1. Requires Home Assistant 2025.7.0 or newer (see hacs.json)
2. If scraping fails, the last cached data will be used

## 📜 Credits
Data: Government of the Netherlands