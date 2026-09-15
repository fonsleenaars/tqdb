# Data contract with tq-db.net

The website copies parser output verbatim and renders it with almost no transformation. This doc records exactly what it depends on, so a parser change can be classified as safe, site-visible, or breaking. First written against the site as of May 2023 and the data files of parser 1.4.5.

## Transfer

- The site's import copies every `output/tqdb.*.json` to a data file per locale, and `output/sprite.css` and `output/sprite.png` beside its styles and images. Nothing else in `output/` is read.
- The locale is the **second dot-separated field** of the filename. `tqdb.en.1.4.5.json` works; anything that moves the locale breaks the import.
- Twelve data files (12 to 14 MB each) plus the sprite are **committed** to the website repo. They are the last known-good parser output and serve as a regression baseline.
- No offline transformation. All reshaping happens at runtime on the site (reverse maps from equipment to creature loot and quest rewards, monster-infrequent de-duplication, per-item links).

## Top-level shape

Six keys, all required:

```json
{
  "affixes":   { "prefixes": { "<tag>": Affix }, "suffixes": { "<tag>": Affix } },
  "creatures": { "<tag>": Creature },
  "equipment": { "<category>": [ Item ] },
  "quests":    { "<tag>": Quest },
  "sets":      { "<tag>": Set },
  "skills":    { "<tag>": Skill }
}
```

`equipment` has 19 category keys that must match the site's category list exactly (e.g. `WeaponMelee_Sword`, `ArmorProtective_Head`, `ItemArtifact`, `ItemRelic`, `ItemCharm`, `OneShot_Scroll`, `ItemArtifactFormula`).

## Fields the site reads

| Entity | Read | Emitted but ignored |
|---|---|---|
| Item | `tag`, `name`, `classification`, `properties`, `bonus[].chance`, `bonus[].option`, `description`, `dropsIn`, `set`, `summons`, `reagent1..3`, `strengthRequirement`, `dexterityRequirement`, `intelligenceRequirement`, `levelRequirement` | `itemLevel`, `act` |
| Set | `tag`, `name`, `items[]`, `properties[]` (one dict per bonus tier) | |
| Skill | `name`, `description`, `properties[level]`, `summons[level]` | |
| Creature | `tag`, `name`, `race`, `level[d]`, `properties[d]`, `abilities[d]`, `loot[d]`, `chest[d]` | `classification` |
| Quest | `name`, `rewards[d]` | |
| Affix | key as tag, `name`, `levelRequirement`, `properties[]`, `equipment` (CSV) | `variants[]` |
| Summon | `name`, `properties`, `abilities[d]` | `classification`, `level`, `race`, `tag` |

`[d]` is a positional difficulty array: index 0 Normal, 1 Epic, 2 Legendary.

Numbers stay numbers only in: `bonus[].chance`, creature and quest loot chances, the four requirements, `creature.level[]`, the affix `levelRequirement` (top-level and per variant), and the granted-skill `level`.

## Load-bearing conventions

These are the parts a rewrite cannot change without a matching website change.

**Property strings are opaque.** `properties` is a dict from DBR variable name to a fully formatted, localized string (`"20% Poison Resistance"`, `"21 ~ 42 Poison Damage over 3.0 Seconds"`). The site renders each one as a list item and never parses numbers out. Only these keys are structured, and the site special-cases each by name:

- `racialBonus*`: list of strings
- `augmentSkillName1/2`, `augmentMasteryName1/2`: `{ name, tag }`
- `itemSkillName`: `{ tag, level, trigger }`; `tag` must exist in `skills` or the page crashes
- `petBonus`: nested property dict (the site also tolerates an array of `{petBonus}` for one item)
- `offensiveGlobalChance`, `retaliationGlobalChance`: `{ chance: "<formatted string>", properties: {...} }`

**Property key names drive grouping and headers.** Ordering comes from prefix matching (`character`, `defensive`, `retaliation`, `racial`, `skill`, `itemSkill`) and a `Modifier` suffix check. Specific keys are pulled into headers: `defensiveProtection`, `offensivePhysical`, `offensivePierceRatio`, `characterAttackSpeed`, `defensiveBlock`, `offensiveBase{Cold,Fire,Lightning,Poison,Life}`, `characterLife`, `characterMana`, `spawnObjectsTimeToLive`, and several `skill*`/`projectile*` keys. Renaming a key silently reshuffles the UI.

**Localized wording is compared byte-for-byte.** `classification` and `dropsIn` are localized display strings, and the site compares them to its own translation files to decide rarity colours and filters (the German data says `"Selten"`, and so must the site's German `rare` string). Category routes are the localized category labels. Changing wording on either side breaks filtering silently.

**Tags carry meaning.** `x2`/`x3`/`x4` prefixes become DLC badges; quest tag prefixes become region labels; `tag === "Placeholder"` is dropped; formulae use the synthetic tag `formula-<artifactTag>` and the site recovers the artifact by stripping the prefix.

**`affix.equipment`** is a CSV of exact tokens: `{head,torso,arm,arms,leg,legs}{mage,melee}`, `amulet`, `ring`, `axe`, `bow`, `club`, `shield`, `spear`, `staff`, `sword`. Unknown tokens render as "unused". The tokens are sorted.

**Affix variants.** An affix is one entry per tag, and `variants` holds one entry per game record that carries the tag, never merged, even when two records have identical properties:

```json
{ "record": "item/lootmagicalaffixes/prefix/default/rare_spellbound_01",
  "levelRequirement": 11, "equipment": "headmage", "properties": { ... } }
```

`record` is the record's path under `database/records`, lowercase, forward slashes, without its `.dbr` extension. Variants are ordered by `levelRequirement`, then by `record` compared bytewise. Per variant, `equipment` is the sorted CSV of the table types that list that record, or `none` when no table does. The fields the site reads are projections of the variants: `properties[i]` is `variants[i].properties`, `levelRequirement` is the first variant's (the lowest), and `equipment` is the sorted union over all variants.

**`description`** still contains the game's `{...}` markup; the site strips it.

**Sprite CSS class names** are `.<itemTag>` for items and `.<classification lowercased>` for formulae. Consumed as a CSS Module by tag.

## Known contract defects (parser side)

- Formula icons never render: class names like `.lesser artifact` contain a space and are invalid selectors, in every locale. Fix by slugifying in the sprite writer and updating the site's lookup.
- Items with `"classification": "UNKNOWN"` match no rarity filter and are invisible in listings.
- Monster-infrequent items can collide on `tag` + `name` + `dropsIn`; the site invents `-1`, `-2` suffixes at load time. Non-MI duplicates are silently dropped.
- `petBonus` is sometimes an array (Spear of Nemetona).
- Any dangling reference (`itemSkillName.tag`, `formula-` artifact, reagents) is an uncaught TypeError on the site. The parser gives no referential-integrity guarantee.
- Website-side, the loot view compares `classification === 'Rare'` in English, so MI loot tables are empty in the 11 other locales.

## Freedom a rewrite has

Safe without touching the site: how values are computed, performance, adding fields the site ignores, dropping `itemLevel`/`act`/creature `classification`, changing the version segment of the filename, fixing the defects above.

Requires a coordinated site change: anything under "Load-bearing conventions". Moving to structured properties (`{ value, unit, template }`) means rewriting the site's property rendering, sorting, and every equipment header. That is a real option, but it is a two-repo project and should be its own decision.
