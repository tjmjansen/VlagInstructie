# 🇳🇱 Dutch Flag Instruction (Vlaginstructie Nederland)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/use/custom_repositories/)

A Home Assistant integration that automatically fetches the official **Dutch flag instruction** from the [Government of the Netherlands](https://www.rijksoverheid.nl/onderwerpen/grondwet-en-statuut/vraag-en-antwoord/wanneer-kan-ik-de-vlag-uithangen-en-wat-is-de-vlaginstructie).  
It tells you exactly when to raise the Dutch flag, whether it should be flown at half-mast, and when to use the orange pennant.

---

## ✨ Features

- ✅ **Today's flag instruction** (`sensor.vlaginstructie_today`)
- ✅ **Tomorrow's flag instruction** (`sensor.vlaginstructie_tomorrow`)
- ✅ **Next upcoming flag day** (`sensor.next_flag_day`)
- ✅ Binary sensors for today and tomorrow:
    - `binary_sensor.vlag_uithangen_today`
    - `binary_sensor.vlag_halfstok_today`
    - `binary_sensor.vlag_uithangen_tomorrow`
    - `binary_sensor.vlag_halfstok_tomorrow`
- ✅ Automatically calculates **variable days** (Veterans Day, Prinsjesdag)
- ✅ Scrapes and caches the official government flag instruction page

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

This integration is **Config Flow-based** → you can add it via the Home Assistant UI:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Dutch Flag Instruction**
4. Done ✅

No `configuration.yaml` is needed.

---

## 📊 Entities

### Sensors
- `sensor.vlaginstructie_today` → today's flag instruction
- `sensor.vlaginstructie_tomorrow` → tomorrow's flag instruction
- `sensor.next_flag_day` → the name and date of the next flag day

Each of these sensors has the following attributes:

| Attribute | Description |
|-----------|-------------|
| `reason`  | The occasion/holiday (e.g., *Dodenherdenking*, *Bevrijdingsdag*) |
| `date`    | The ISO date of the flag instruction |
| `scope`   | Whether the instruction is nationwide or specific |
| `wimpel`  | `true` if the orange pennant should be used |
| `halfstok`| `true` if the flag should be flown at half-mast |

### Binary Sensors
- `binary_sensor.vlag_uithangen_today`
- `binary_sensor.vlag_halfstok_today`
- `binary_sensor.vlag_uithangen_tomorrow`
- `binary_sensor.vlag_halfstok_tomorrow`

> These are **simple on/off sensors** without extra attributes.

---

## 📊 Lovelace Example

### Markdown Card Example
```yaml
type: markdown
title: 🇳🇱 Flag Instruction
content: |
  **Today ({{ states('sensor.vlaginstructie_today') }})**
  - Reason: {{ state_attr('sensor.vlaginstructie_today', 'reason') }}
  - Date: {{ state_attr('sensor.vlaginstructie_today', 'date') }}
  - Half-mast: {{ state_attr('sensor.vlaginstructie_today', 'halfstok') }}
  - With pennant: {{ state_attr('sensor.vlaginstructie_today', 'wimpel') }}

  **Tomorrow ({{ states('sensor.vlaginstructie_tomorrow') }})**
  - Reason: {{ state_attr('sensor.vlaginstructie_tomorrow', 'reason') }}
  - Date: {{ state_attr('sensor.vlaginstructie_tomorrow', 'date') }}
  - Half-mast: {{ state_attr('sensor.vlaginstructie_tomorrow', 'halfstok') }}
  - With pennant: {{ state_attr('sensor.vlaginstructie_tomorrow', 'wimpel') }}

  **Next flag day ({{ states('sensor.next_flag_day') }})**
  - Reason: {{ state_attr('sensor.next_flag_day', 'reason') }}
  - Date: {{ state_attr('sensor.next_flag_day', 'date') }}
  - Half-mast: {{ state_attr('sensor.next_flag_day', 'halfstok') }}
  - With pennant: {{ state_attr('sensor.next_flag_day', 'wimpel') }}
```

### Entities Card Example
```yaml
type: entities
title: 🇳🇱 Flag Instruction
entities:
- entity: sensor.vlaginstructie_today
  name: Today
  secondary_info: >-
  {{ state_attr('sensor.vlaginstructie_today', 'reason') }}
- entity: sensor.vlaginstructie_tomorrow
  name: Tomorrow
  secondary_info: >-
  {{ state_attr('sensor.vlaginstructie_tomorrow', 'reason') }}
- entity: sensor.next_flag_day
  name: Next Flag Day
  secondary_info: >-
  {{ state_attr('sensor.next_flag_day', 'reason') }}
```

## 📜 Special rules
- On 4 May (Remembrance Day):
  - Flag is half-mast until 18:00
  - From 18:00 onwards → raised to full mast

The binary sensors automatically follow this rule.

## 🛠 Troubleshooting

1. Requires Home Assistant 2025.7.0 or newer (see hacs.json)
2. If scraping fails, the last cached data will be used

## 📜 Credits
Data: Government of the Netherlands