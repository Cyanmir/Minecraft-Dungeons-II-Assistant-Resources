"""中文维护说明：从用户自己的本地解析数据制作最小展示包；不收集存档、SDK、模型或整套拆包。"""
from pathlib import Path
import argparse, gzip, hashlib, json, struct

def build(assets, localization, output, revision):
    source = json.loads((assets / 'inventory-resources.json').read_text(encoding='utf-8-sig'))
    tables = {}
    for file in localization.glob('*.json'):
        rows = json.loads(file.read_text(encoding='utf-8-sig'))
        if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict) or 'namespace' not in rows[0]:
            continue
        tables[file.stem] = {(r['namespace'], r['key'], r['sourceHash']): r['text'] for r in rows}
    six = ['zh-Hans', 'en', 'ja-JP', 'ko-KR', 'zh-Hant', 'zh-Hant']
    names = {tag: value for tag, value in source['names'].items()
             if tag.startswith(('SW.Item.', 'SW.Effect.', 'SW.Enchantment.'))}
    items, files, fallback = {}, set(), {}
    local_dir = output / 'locales'
    local_dir.mkdir(parents=True, exist_ok=True)
    for lang, table in sorted(tables.items()):
        localized = {}
        for tag, value in names.items():
            identity = (value['namespace'], value['key'], value['sourceHash'])
            if identity in table: localized[tag] = table[identity]
        (local_dir / (lang + '.json')).write_text(json.dumps(localized, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    for tag, value in sorted(names.items()):
        identity = (value['namespace'], value['key'], value['sourceHash'])
        english = tables['en'].get(identity, tag)
        labels = [tables[l].get(identity, english) for l in six]
        missing = [l for l in set(six) if identity not in tables[l]]
        if missing: fallback[tag] = sorted(missing)
        icons = source['icons'].get(tag, [])
        files.update(icons)
        items[tag] = {'names': labels, 'icons': icons, 'namespace': identity[0], 'key': identity[1], 'sourceHash': identity[2]}
    keys = ['Equipment_Melee', 'Equipment_Ranged', 'Equipment_Helmet', 'Equipment_Chest', 'Equipment_Leggings', 'Equipment_Boots', 'Equipment_Artifact', 'header_power', 'header_gear_power', 'inventory_sort_rarity', 'tag_equipped', 'Label_Enchanted', 'SW_Rarity_Common', 'SW_Rarity_Rare', 'SW_Rarity_Special', 'SW_Rarity_Unique']
    terms = {}
    for key in keys:
        matches = [i for i in tables['en'] if i[0] == 'Text/Release/InventoryLabels.csv' and i[1] == key]
        if len(matches) != 1: raise ValueError('Ambiguous localization identity: ' + key)
        terms[key] = [tables[l].get(matches[0], tables['en'][matches[0]]) for l in six]
    # UI 品质框来自原始纹理引用；只复制白名单，不遍历整套游戏资源。
    index = json.loads((assets.parent / 'catalogs' / 'item-definition-icons.json').read_text(encoding='utf-8-sig'))
    wanted = {'slotBackground': 'T_UI_Slot_Background', 'rarityMarkers': 'T_UI_SlotRarity_Markers',
              'soulMarkers': 'T_UI_SlotRarity_Markers_Soul', 'stormPip': 'T_UI_Icon_SoulStormPip',
              'rarityCommon': 'T_UI_Rarity_Common', 'rarityRare': 'T_UI_Rarity_Rare',
              'raritySpecial': 'T_UI_Rarity_Special', 'rarityUnique': 'T_UI_Rarity_Unique'}
    ui = {}
    for key, name in wanted.items():
        matches = [r for r in index['textures'] if r['package'].endswith('/' + name)]
        if len(matches) != 1: raise ValueError('Ambiguous UI texture: ' + name)
        ui[key] = matches[0]['file']
        files.add(matches[0]['file'])
    icons_dir = output / 'icons'
    icons_dir.mkdir(exist_ok=True)
    icon_hashes = {}
    for name in sorted(files):
        if Path(name).name != name or not name.endswith('.png'): raise ValueError('Invalid icon name')
        png = (assets / 'icons' / name).read_bytes()
        icon_hashes[name] = hashlib.sha256(png).hexdigest()
        (icons_dir / name).write_bytes(png)
    catalogue = {'format': 'MCD2.EquipmentPresentation.v1', 'revision': revision, 'gameBuild': '1.1.1.0', 'languages': six,
                 'availableLanguages': sorted(tables), 'items': items, 'terms': terms, 'iconSHA256': icon_hashes, 'uiTextures': ui,
                 'fallbackLanguages': fallback, 'origin': 'Original game artwork/localization; respective owners retain rights. Presentation only, not a reroll catalogue.'}
    raw = json.dumps(catalogue, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    body = bytearray(b'M2EQ' + struct.pack('<I', len(raw)) + raw + struct.pack('<I', len(files)))
    for name in sorted(files):
        key, png = name.encode('utf-8'), (icons_dir / name).read_bytes()
        body += struct.pack('<H', len(key)) + key + struct.pack('<I', len(png)) + png
    payload = gzip.compress(bytes(body), compresslevel=9, mtime=0)
    digest = hashlib.sha256(payload).hexdigest()
    packages = output / 'packages'
    packages.mkdir(exist_ok=True)
    (packages / (digest + '.bin.gz')).write_bytes(payload)
    (output / 'catalogue.json').write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    manifest = {'format': 'MCD2A.Resources.v1', 'revision': revision, 'gameBuild': '1.1.1.0', 'sha256': digest,
                'bytes': len(payload), 'package': 'packages/' + digest + '.bin.gz', 'entries': len(items), 'icons': len(files), 'languages': sorted(tables)}
    (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--assets', type=Path, required=True)
    parser.add_argument('--localization', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--revision', required=True)
    args = parser.parse_args()
    build(args.assets, args.localization, args.output, args.revision)
