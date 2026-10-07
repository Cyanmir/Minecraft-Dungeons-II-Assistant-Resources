# MCD2A 展示资源

Minecraft Dungeons II Assistant 的装备图标、品质框纹理与游戏内译名。资源与本体分别更新；本体版本不由资源 revision 决定。

- `manifest.json`：客户端读取的当前资源清单。
- `packages/<sha256>.bin.gz`：不可变的完整显示资源包，供 MCD2A 下载。
- `icons/`：装备图标、效果图标、原始品质框背景与标记纹理。
- `locales/`：19 种游戏语言的装备、词条和货币名称，装备/词条按原始标签索引，货币以 `Currency_*` 键索引。
- `catalogue.json`：六界面语言显示名称、图标对应关系、原始译名标识和哈希。

当前资源修订 **2026.10.08.1**，含 384 张装备图标、77 张效果图标、8 张界面纹理及 19 种语言的名称。这里的“词条”指装备效果；图标按原始效果引用精确关联，缺图不补造。

本批数据对应游戏构建 **1.1.1.0**。香港和台湾繁体界面使用游戏提供的同一份 `zh-Hant`；客户端不自行翻译。缺少的原始译文在 `fallbackLanguages` 中记录，显示英文原译名或精确标签。本包只负责显示，不作为铁匠可刷新词条全集、最高等级或概率的证据。

品质框由原始背景/标记纹理在 MCD2A 中着色组成。Unreal 的动态材质效果并未直接移植。品质和风暴状态来自游戏读数，不通过图标或颜色猜测槽位数。

更新资源时，用自己的合法本地解析数据运行：

```text
python build_resources.py --assets <assets目录> --localization <解析译名目录> --effect-table <本地DT_EffectDefinition.json> --revision <新的数字版本>
```

`assets` 包含 `inventory-resources.json` 和 `icons/`，同级 `catalogs/item-definition-icons.json` 提供原始 UI 纹理引用。`--effect-table` 是可选的本地输入，只将有译名效果行的精确图标引用关联到已解码 PNG；不上传该原始数据表，也不推测候选池、最高等级或继承规则。先上传新包、图标和译名，再更新清单；旧哈希包保持不变。不上传游戏存档、凭据、SDK、模型、音频或整套拆包。

客户端仅从此仓库下载，校验包大小、SHA256、内部图标哈希、结构与大小边界后原子替换缓存。首次需要网络；之后断网保留已缓存资源。资源更新不调用游戏原生刷新或出售接口。

游戏贴图和原始译名归 Mojang / Microsoft 及相应权利人所有，本仓库不将它们声明为 MIT。构建脚本为 MCD2A 原创代码，采用 MIT；见 `LICENSE` 和 `THIRD_PARTY_NOTICES.md`。
