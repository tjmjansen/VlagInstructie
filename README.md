# Dutch Flag Instruction (Vlaginstructie Nederland)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/use/custom_repositories/)

A Home Assistant integration that fetches the official Dutch flag instruction from the [Government of the Netherlands](https://www.rijksoverheid.nl/onderwerpen/grondwet-en-statuut/vraag-en-antwoord/wanneer-kan-ik-de-vlag-uithangen-en-wat-is-de-vlaginstructie).

It tells you when to raise the Dutch flag, whether it should be flown at half-mast, and when to use the orange pennant.

## Features

- Today's flag instruction: `sensor.vlaginstructie_today`
- Tomorrow's flag instruction: `sensor.vlaginstructie_tomorrow`
- Next upcoming flag day: `sensor.next_flag_day`
- Binary sensors for today and tomorrow:
  - `binary_sensor.vlag_uithangen_today`
  - `binary_sensor.vlag_halfstok_today`
  - `binary_sensor.vlag_uithangen_tomorrow`
  - `binary_sensor.vlag_halfstok_tomorrow`
  - `binary_sensor.oranje_wimpel_today`
  - `binary_sensor.oranje_wimpel_tomorrow`
- Automatically calculates variable days such as Veteranendag and Prinsjesdag
- Caches the official government flag instruction page

## Installation

### HACS custom repository

1. Open HACS in Home Assistant.
2. Go to **Integrations**.
3. Open **Custom repositories**.
4. Add this repository as an integration.
5. Search for **Vlaginstructie Nederland** and install it.

### Manual installation

1. Download this repository as a ZIP.
2. Copy `custom_components/vlaginstructie/` into your Home Assistant `custom_components/` directory.
3. Restart Home Assistant.

## Configuration

This integration uses the Home Assistant UI.

1. Go to **Settings > Devices & services**.
2. Select **Add integration**.
3. Search for **Vlaginstructie Nederland**.
4. Finish the setup flow.

No `configuration.yaml` setup is needed.

## Entities

### Sensors

- `sensor.vlaginstructie_today`
- `sensor.vlaginstructie_tomorrow`
- `sensor.next_flag_day`

Each sensor exposes these attributes when a flag instruction exists:

| Attribute | Description |
| --- | --- |
| `reason` | The occasion, for example `Dodenherdenking` or `Koningsdag` |
| `date` | The ISO date of the flag instruction |
| `scope` | Whether the instruction is nationwide or specific |
| `wimpel` | `true` if the orange pennant should be used |
| `halfstok` | `true` if the flag should be flown at half-mast |

### Binary sensors

- `binary_sensor.vlag_uithangen_today`
- `binary_sensor.vlag_halfstok_today`
- `binary_sensor.vlag_uithangen_tomorrow`
- `binary_sensor.vlag_halfstok_tomorrow`
- `binary_sensor.oranje_wimpel_today`
- `binary_sensor.oranje_wimpel_tomorrow`

The `oranje_wimpel_*` sensors are `on` on days where the official instruction includes an orange pennant, such as Koningsdag and birthdays of members of the Royal House.

## Lovelace example

### Markdown card

```yaml
type: markdown
title: Vlaginstructie
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

### Entities card

```yaml
type: entities
title: Vlaginstructie
entities:
  - entity: sensor.vlaginstructie_today
    name: Today
  - entity: sensor.vlaginstructie_tomorrow
    name: Tomorrow
  - entity: sensor.next_flag_day
    name: Next flag day
```

## Special rules

On 4 May (Dodenherdenking), the flag is flown at half-mast until 18:00. After 18:00, the half-mast binary sensor turns off.

## Troubleshooting

- Requires Home Assistant 2025.7.0 or newer.
- If fetching the government page fails, the last cached data is used.
- If the government page structure changes, the integration logs a warning and keeps using cached data when available.

## Credits

Data source: Government of the Netherlands.
