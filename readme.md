# Custom Hideout Recipe Format

Reference documentation for creating **custom hideout crafting recipes**.

---

# Requirements

* All recipe files **must be placed inside the `recipes` folder**
* Each recipe **must be a separate `.json` file**
* File name **does not matter**
* `_id` **must be unique per recipe**

---

# Resources

Item IDs can be located using the SPT database:

* [https://db.sp-tarkov.com/search](https://db.sp-tarkov.com/search)

---

# Example Recipe

```json
{
  "_id": "CHR_Recipe_01",

  "areaType": 6,
  "requiredLevel": 1,
  "productionTime": 60,

  "endProduct": "5c94bbff86f7747ee735c08f",
  "count": 1,

  "needFuelForAllProductionTime": true,

  "inputs": [
    { "tpl": "5755356824597772cb798962", "count": 1 },
    { "tpl": "544fb45d4bdc2dee738b4568", "count": 1 }
  ],

  "tools": [
    { "tpl": "590c2d8786f774245b1f03f3", "count": 1 }
  ]
}
```

---

# Recipe Fields

| Field                          | Description                                       |
| ------------------------------ | ------------------------------------------------- |
| `_id`                          | Unique recipe identifier                          |
| `areaType`                     | Hideout station where the craft occurs            |
| `requiredLevel`                | Required station level                            |
| `productionTime`               | Craft time (seconds)                              |
| `endProduct`                   | Item template ID of produced item                 |
| `count`                        | Quantity produced                                 |
| `needFuelForAllProductionTime` | Requires generator fuel for entire craft duration |
| `inputs`                       | Items consumed during crafting                    |
| `tools`                        | Tools required but not consumed (optional)        |

---

# Inputs Format

```json
"inputs": [
  { "tpl": "ITEM_ID", "count": 1 },
  { "tpl": "ITEM_ID", "count": 1 }
]
```

---

# Tools Format (Optional)

```json
"tools": [
  { "tpl": "ITEM_ID", "count": 1 }
]
```

If tools are not required, remove the entire `"tools"` section.

---

# Copy-Paste Recipe Template

```json
{
  "_id": "CHR_Recipe_XX",

  "areaType": 0,
  "requiredLevel": 1,
  "productionTime": 60,

  "endProduct": "ITEM_ID",
  "count": 1,

  "needFuelForAllProductionTime": true,

  "inputs": [
    { "tpl": "ITEM_ID", "count": 1 }
  ],

  "tools": [
    { "tpl": "ITEM_ID", "count": 1 }
  ]
}
```

---

# Minimal Recipe Template (No Tools)

```json
{
  "_id": "CHR_Recipe_XX",

  "areaType": 0,
  "requiredLevel": 1,
  "productionTime": 60,

  "endProduct": "ITEM_ID",
  "count": 1,

  "needFuelForAllProductionTime": true,

  "inputs": [
    { "tpl": "ITEM_ID", "count": 1 }
  ]
}
```

---

# Hideout Area Types

<details>
<summary>Show AreaType Reference</summary>

| AreaType | Station                 |
| -------- | ----------------------- |
| 0        | Vents                   |
| 1        | Security                |
| 2        | Lavatory                |
| 4        | Generator               |
| 5        | Heating                 |
| 6        | Water Collector         |
| 7        | Med Station             |
| 8        | Nutrition Unit          |
| 9        | Rest Space              |
| 10       | Workbench               |
| 11       | Intelligence Center     |
| 12       | Shooting Range          |
| 13       | Library                 |
| 14       | Scav Case               |
| 15       | Illumination            |
| 16       | Hall Of Fame            |
| 17       | Air Filtering Unit      |
| 18       | Solar Power             |
| 19       | Booze Generator         |
| 20       | Bitcoin Farm            |
| 21       | Christmas Tree          |
| 23       | Gym                     |
| 24       | Weapon Stand            |
| 25       | Weapon Stand Secondary  |
| 26       | Equipment Presets Stand |
| 27       | Cult Circle             |

</details>
