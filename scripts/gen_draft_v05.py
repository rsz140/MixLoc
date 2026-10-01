# -*- coding: utf-8 -*-
"""论文底稿 v0.5 — 全面结构重构（按 2026-09-30 负责人 14 条修改指令）"""
import os, re, json
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = r"E:\生成式视频水印技术\AI_text_detection_papers\论文中文底稿_v0.6.docx"
_B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bench_results")
def _load(n):
    p = os.path.join(_B, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
FR = _load("full_results.json"); SR = _load("results.json"); LA = _load("language_f1_full.json")
AT = _load("attack_results.json"); HO = _load("cross_results.json")
def _f3(x): return "—" if x is None else f"{x:.3f}"

# palette
C_PRIMARY = RGBColor(0x1F, 0x4E, 0x79); C_BODY = RGBColor(0x33, 0x33, 0x33)
C_PLACE = RGBColor(0xC0, 0x00, 0x00); C_NOTE = RGBColor(0x7F, 0x7F, 0x7F)
C_HBG = "1F4E79"; C_HFG = RGBColor(0xFF, 0xFF, 0xFF)

doc = Document()
sec = doc.sections[0]
sec.top_margin = sec.bottom_margin = Cm(2.54); sec.left_margin = sec.right_margin = Cm(3.17)
normal = doc.styles["Normal"]; normal.font.name = "Times New Roman"; normal.font.size = Pt(12)
normal.font.color.rgb = C_BODY; normal.element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
normal.paragraph_format.line_spacing = 1.3
for lv, sz in [("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 12.5)]:
    st = doc.styles[lv]; st.font.name = "Times New Roman"; st.font.size = Pt(sz)
    st.font.bold = True; st.font.color.rgb = C_PRIMARY
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
_r = fp.add_run(); _f1 = OxmlElement("w:fldChar"); _f1.set(qn("w:fldCharType"), "begin")
_it = OxmlElement("w:instrText"); _it.set(qn("xml:space"), "preserve"); _it.text = r"PAGE \* ARABIC"
_f2 = OxmlElement("w:fldChar"); _f2.set(qn("w:fldCharType"), "end")
_r._r.append(_f1); _r._r.append(_it); _r._r.append(_f2); _r.font.size = Pt(9); _r.font.color.rgb = C_NOTE

PLACE_RE = re.compile(r"(【[^】]*】)")
def _sr(p, text, size=12, bold=False, color=C_BODY, east="宋体"):
    for seg in PLACE_RE.split(text):
        if not seg: continue
        r = p.add_run(seg); r.font.name = "Times New Roman"
        r._element.rPr.rFonts.set(qn("w:eastAsia"), east); r.font.size = Pt(size)
        r.font.bold = bold or PLACE_RE.fullmatch(seg) is not None
        r.font.color.rgb = C_PLACE if PLACE_RE.fullmatch(seg) else color
def H1(t, pb=False):
    p = doc.add_heading(level=1); _sr(p, t, 16, True, C_PRIMARY, "黑体")
    p.paragraph_format.space_before = Pt(18); p.paragraph_format.space_after = Pt(8)
    if pb: p.paragraph_format.page_break_before = True
def H2(t):
    p = doc.add_heading(level=2); _sr(p, t, 14, True, C_PRIMARY, "黑体")
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(6)
def H3(t):
    p = doc.add_heading(level=3); _sr(p, t, 12.5, True, C_PRIMARY, "黑体")
def B(t, indent=True):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.3
    if indent: p.paragraph_format.first_line_indent = Pt(24)
    _sr(p, t)
def BL(t):
    p = doc.add_paragraph(style="List Bullet"); p.paragraph_format.line_spacing = 1.3; _sr(p, t)
def CAP(t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4); p.paragraph_format.space_after = Pt(4)
    _sr(p, t, 10.5, True, C_PRIMARY, "黑体")
def NT(t):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.3; _sr(p, t, 10.5, False, C_NOTE, "楷体")
def _shade(c, h):
    tc = c._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:fill"), h); tc.append(s)
def TBL(headers, rows, caption=None, note=None):
    if caption: CAP(caption)
    t = doc.add_table(rows=1+len(rows), cols=len(headers)); t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        c = t.cell(0, j); c.text = ""; _sr(c.paragraphs[0], h, 10.5, True, C_HFG, "黑体")
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER; _shade(c, C_HBG)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            c = t.cell(i+1, j); c.text = ""; c.paragraphs[0].paragraph_format.line_spacing = 1.15
            _sr(c.paragraphs[0], str(v), 10.5)
            if i % 2 == 1: _shade(c, "F2F6FA")
    if note: NT(note)
def FIG(png, cap):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.add_run().add_picture(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", png), width=Cm(15.2))
    CAP(cap)
def FIGA(path, cap):
    if not path or not os.path.exists(path):
        NT("【图片待插入：" + cap[:30] + "...】"); return
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.add_run().add_picture(path, width=Cm(15.2)); CAP(cap)

# ======================== 标题区 ========================
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_before = Pt(24)
_sr(p, "MixLoc", 14, True, C_PLACE, "黑体")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
_sr(p, "面向人机混写文本检测与字符级定位的\n大规模多语言基准数据集", 22, True, C_PRIMARY, "黑体")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
_sr(p, "A Large-Scale Multilingual Benchmark for Mixed Human–AI Authorship Detection and Character-Level Localization", 12, False, C_NOTE)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
_sr(p, "—— 论文中文底稿 v0.5（2026-09-30 结构重构版）——", 11, False, C_NOTE, "楷体")
NT("本版按负责人 14 条修改指令全面重构：章节结构、贡献提炼、术语统一、数据/算法分离。红色【】为占位符。")

# ======================== 摘要 ========================
H1("摘要")
_abs = ("以大语言模型为代表的生成式人工智能使\u201c一段文字中有多少内容由 AI 产生\u201d成为学术出版、教学评估与内容治理共同面对的现实问题，"
        "而真实场景中的滥用形态已从整篇生成转向人机接力混写。本文构建了一个面向人机混写检测与字符级定位的大规模多语言基准数据集："
        "覆盖 20 种语言，共 601,846 行已切分文档（人类 300,963 / 人机混写 190,085 / 全文生成 110,798），"
        "其中 180,971 篇受控生成文档通过五类局部人机混写操作（句级替换、句级插入、多句插入、风格约束改写、续写）"
        "在真实人类文本的句子边界上程序化构造，AI 片段的字符区间在文档组装过程中直接记录，"
        "由统一来源信息推导字符、句子和文档三级标签。"
        "基准采用 2 个已见生成器→6 个未见生成器的固定留出设计，同时控制同源家族泄漏与 AI 覆盖率分布。")
if FR:
    _mf = max(v["macro_f1"] for v in FR["doc3"].values())
    _au = max(v["auroc"] for v in FR["binary"].values())
    _abs += (f" 在统一评测协议下，六个来自 ACL、ICLR、ICML、NAACL 的开源检测算法在全量测试集上的文档三分类宏 F1 最高 {_mf:.3f}，"
             f"二分类 AUROC 最高 {_au:.3f}；评测进一步揭示了低 AI 覆盖率（<5%）下监督检测近乎失效、"
             "英语为最难检测语言、GPT-2 类零样本方法在西里尔文上方向反转等系统性发现。")
B(_abs)
B("关键词：人机混写文本检测；基准数据集；字符级定位；跨生成器泛化；多语言", indent=False)

# ======================== 1 Introduction ========================
H1("1 引言", pb=True)
B("生成式人工智能的普及正在改变文本的生产方式，大语言模型生成文本的流畅性与类人性也使机器生成内容的可靠识别"
  "成为自然语言处理中的重要问题 [15, 16, 23]。已有研究表明，现有检测方法在跨生成器、文本改写和不同语言背景下"
  "仍存在明显的可靠性与泛化挑战 [24-26]。在学术写作、教学评估、内容平台与法律取证等场景中，"
  "现实的内容生产日益呈现人机接力形态：作者撰写初稿后令模型改写某句、在论证薄弱处插入一段补充、或在搁笔处续写——"
  "最终文本既非纯人类撰写也非纯机器生成，而是多次人机交接的产物 [7, 16, 20]。"
  "文档级“人类 / AI”二分类难以完整刻画这种作者来源（authorship provenance），"
  "也无法回答实务中更细粒度的问题：“这段话里，究竟哪些部分是 AI 写的？”")
B("然而，现有公开数据资产难以同时满足上述要求（表 1）。文档级检测基准（HC3 [1]、M4 [2]、TuringBench [3]、RAID [4]、MULTITuDE [5]）"
  "提供了多语言、多生成器的人机对照语料，但仅携带文档级标签；面向混写与定位的数据集（RoFT [6]、MixSet [7]、LLMTrace [8]、HACo-Det [9]）"
  "开始进入混合作者身份场景，但规模较小、语种覆盖较窄，或定位粒度止于词级/边界级，且真值多依赖人工标注或上游编辑记录。")
B("本文的核心目标是构建一个面向人机混写场景的细粒度检测与定位基准，使研究者能够在统一数据框架下同时评估 AI 参与检测、"
  "AI 片段字符级定位及跨生成条件泛化能力。为获得边界明确且可追溯的细粒度真值，我们采用受控人机混写构造："
  "以人类文本为基底，通过替换、插入、改写和续写等操作程序化引入 AI 生成内容，并在文档组装过程中直接记录 AI 字符区间。")
B("本文的主要贡献如下：")
BL("（1）混合作者身份基准——构建一个面向人机混写检测与定位的大规模多语言基准，覆盖 20 种语言、601,846 行文档，"
   "同时支持 HUMAN / PARTIAL_AI / FULL_AI 文档判别和 AI 片段字符级定位。")
BL("（2）构造过程派生的细粒度来源真值——通过五类局部人机混写操作与全文生成对照程序化构造 AI 参与文档，"
   "并在组装过程中直接记录 Unicode 字符区间，由统一来源信息推导字符、句子和文档三级标签。")
BL("（3）泛化导向的基准设计——采用 2 个已见生成器→6 个未见生成器的固定留出设计，"
   "同时控制同源家族泄漏、AI 覆盖率和操作类型，使跨生成器及低 AI 占比等现实困难可以独立分析。")
BL("（4）系统性基准表征——通过代表性监督、统计和零样本检测器对基准进行技术验证，"
   "并从 AI 覆盖率、混写操作、生成器、语言、来源及字符边界等维度刻画现有检测方法的能力边界。")

# ======================== 2 Related Work ========================
H1("2 相关工作")
H2("2.1 文档级检测数据集")
B("早期机器生成文本检测研究主要将任务定义为文档级人类/机器二分类，并围绕特定生成器、领域或任务构建评测数据。"
  "TuringBench [3] 面向神经文本生成环境下的图灵测试与生成器归因；"
  "HC3 [1] 构建了人类专家与 ChatGPT 针对相同问题的对照回答，并形成中英文人机文本检测语料。"
  "此后，研究开始由单一生成器或任务转向更加复杂的跨模型、跨领域和多语言设置。"
  "MGTBench [17] 系统比较了多类机器生成文本检测方法；"
  "M4 [2] 从多生成器、多领域和多语言三个维度扩展黑盒检测评测；"
  "MULTITuDE [5] 进一步关注多语言机器生成文本检测；"
  "M4GT-Bench [18] 则面向黑盒机器生成文本检测建立更系统的评测基准。"
  "RAID [4] 进一步将采样策略、生成模型和对抗扰动纳入统一鲁棒性评测框架，"
  "其数据覆盖 11 个生成模型、8 个领域、4 种解码策略和 11 类对抗攻击。"
  "近年来，CUDRT [16] 从文本生成操作出发，"
  "将 Create、Update、Delete、Rewrite 和 Translate 纳入中英文统一评测框架，"
  "进一步表明生成任务类型本身也是影响检测性能的重要因素。"
  "另有工作从规模较小但受控的数据集出发研究人类与 AI 文本的可分性 [15]。"
  "上述工作推动了 AI 生成文本检测从单一数据分布下的二分类向跨生成器、跨领域、多语言及鲁棒性评测发展，"
  "但其监督信号总体仍以文档级标签为主，难以直接支持混写文本中 AI 内容的字符级定位。")
H2("2.2 人机混写与细粒度定位基准")
B("随着 AI 辅助写作由全文生成逐渐扩展至改写、补全和局部编辑，研究开始从文档级二分类转向混合作者身份与细粒度来源识别。"
  "RoFT [6] 提出检测文本由人类撰写向机器生成发生转换的位置；"
  "MixSet [7] 系统研究人类撰写与机器生成内容混合后的检测问题，并覆盖续写、改写等多种混合形式；"
  "SeqXGPT [19] 将检测粒度推进至句子级，通过语言模型概率表示进行 AI 生成文本识别；"
  "HC3 Plus [20] 则在 HC3 基础上引入翻译、摘要和改写等语义保持操作。"
  "进一步地，LLMTrace [8] 提供英俄双语语料并支持分类与细粒度区间定位，"
  "HACo-Det [9] 面向 Human-AI Coauthoring 场景研究更细粒度的来源归因。"
  "这些工作共同表明，AI 生成文本检测正在从“整篇是否由 AI 生成”转向“AI 以何种方式参与以及具体参与了哪些内容”。"
  "然而，现有混写与定位资源仍受限于规模、语种覆盖或真值粒度，"
  "且部分定位真值依赖人工判断或上游编辑记录，难以同时提供大规模、多语言且穷尽的字符级来源真值。")
H2("2.3 AI 生成文本检测方法")
B("现有 AI 生成文本检测方法大体可分为基于统计信号的零样本方法和基于监督学习的方法 [23]。"
  "前者利用生成模型概率分布中的统计规律进行判别，例如 GLTR [11] 根据 token 排名与生成概率分析文本，"
  "DetectGPT [21] 利用模型对数概率函数的局部曲率进行零样本检测，"
  "Fast-DetectGPT [12] 进一步以条件概率曲率提高检测效率，"
  "DetectLLM [14] 利用 log-rank 信息实现无需额外训练的检测，"
  "Binoculars [13] 则利用两个语言模型之间的内在概率关系进行黑盒检测。"
  "监督方法通常在标注的人类/机器文本上微调预训练语言模型，"
  "例如基于 RoBERTa/XLM-R 的分类器 [10, 22]，以及面向句级检测的 SeqXGPT [19]。"
  "虽然监督方法在同分布测试中通常具有较强性能，"
  "但其结果高度依赖训练数据的生成器、语言和任务分布，"
  "跨模型和跨分布泛化仍是重要挑战 [24, 30]。")

H2("2.4 基准缺口与本文定位")
B("表 1 从发表信息、语言覆盖、生成器构成、混写支持、真值粒度与泛化设计七个维度对比代表性数据集 [1-9, 15-18, 20]。"
  "在本文调研范围内，尚无公开数据集同时满足\u201c多语言 × 大规模 × 穷尽字符级来源真值 × 多类型受控人机混写操作 × 跨生成器留出设计\u201d这一组合。"
  "在代表性数据集中，本基准将较广的多语言覆盖和较大规模与穷尽字符级来源真值及受控混合作者身份构造相结合。")
B("图 1 以数据集版图的形式直观呈现上述格局：横轴为规模（对数刻度），纵轴为语言数，点径编码生成器数量，"
  "形状区分文档级与混合作者数据集，虚线外圈标记支持字符/词级细粒度来源真值。本基准位于右上区域，"
  "在规模、语言覆盖与细粒度真值三个维度上同时越出现有公开基准的覆盖范围。")
FIGA(os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures", "fig_landscape.png"),
     "图 1  AIGT 检测与定位数据集版图（点径=生成器数；方块=混合作者；虚线外圈=细粒度来源真值）")
TBL(
    ["数据集", "Venue / 年份", "语言", "生成器", "混写", "字符级真值", "构造式", "留出"],
    [
        ["HC3 [1]", "arXiv, 2023", "英/中", "1", "无", "无", "—", "无"],
        ["M4 [2]", "EACL, 2024", "7 语", "多", "无", "无", "—", "无"],
        ["TuringBench [3]", "EMNLP-F, 2021", "英", "20", "无", "无", "—", "无"],
        ["RAID [4]", "ACL, 2024", "英", "11", "改写", "无", "—", "部分"],
        ["MULTITuDE [5]", "EMNLP, 2023", "11 语", "多", "无", "无", "—", "无"],
        ["RoFT [6]", "EMNLP-D, 2020", "英", "少", "边界", "无", "部分", "无"],
        ["MixSet [7]", "NAACL-F, 2024", "英", "少", "词/句", "无", "部分", "无"],
        ["LLMTrace [8]", "arXiv, 2025", "英/俄", "多", "区间", "部分", "部分", "无"],
        ["HACo-Det [9]", "ACL, 2025", "英", "少", "词级", "无", "部分", "无"],
        ["本文", "—", "20 语", "8+12", "五类+全文", "穷尽", "是", "是"],
    ],
    caption="表 1  与现有 AIGT 检测/定位数据集的对比",
)

# ======================== 3 Benchmark Design ========================
H1("3 基准设计")
H2("3.1 设计目标")
B("基准设计遵循四条目标。（1）细粒度来源真值：AI 参与文档的每一个 AI 产生字符都有精确的区间标注，"
  "由构造过程直接记录，不做事后人工标注，使字符级定位评测具有零标注者分歧的真值基础。"
  "（2）混合作者真实性：混写文档通过受控人机混写操作在真实人类文本的句子边界上构造，对应真实的人机协作写作形态。"
  "（3）泛化可测性：泛化压力由数据划分结构而非事后实验给出——测试集为跨生成器留出，同源家族不跨切分。"
  "（4）可复现与可审计：构建管线确定性执行，全量树哈希冻结，质量审计记录随数据开源。")
H2("3.2 主要基准任务")
B("基准正式支持两个主要任务。")
B("任务 A——文档级混合作者身份检测（Document-level Mixed-authorship Detection）：给定文档文本，"
  "判定 HUMAN / PARTIAL_AI / FULL_AI 三类。三分类标签由字符区间覆盖率推导（覆盖率=0 / (0,1) / =1），"
  "保证分类与定位真值严格自洽。", indent=False)
B("任务 B——字符级 AI 内容定位（Character-level AI-content Localization）：输出 AI 产生内容的字符区间集合 [s,e)，"
  "以半开区间、Unicode 码点偏移表示。评测指标在字符空间计算，包括字符级精确率/召回率/F1、区间完全匹配 F1、IoU@0.5-F1 与边界误差。", indent=False)
B("派生诊断量——AI 内容覆盖率（AI-content Coverage）：定义为 Coverage(x) = Σ(eₖ−sₖ)/|x|，由任务 B 的区间直接计算。"
  "覆盖率作为分析变量而非独立任务，用于分层评测（见 6.4 节）。", indent=False)
H2("3.3 多粒度来源表示")
B("真值体系分为三个自洽粒度，由同一份构造过程来源信息推导：")
BL("字符级：gold_machine_spans = [(s₁,e₁), (s₂,e₂), ...]，半开区间，Unicode 码点偏移。")
BL("句级：sentence_labels = [0, 1, 0, ...]，由字符区间与句边界对齐推导。")
BL("文档级：HUMAN（区间为空）/ PARTIAL_AI（0 < 覆盖率 < 1）/ FULL_AI（覆盖率 = 1），由字符区间覆盖率推导。")
B("三种粒度由同一来源（构造过程记录的 AI 字符区间）推导，不存在粒度间冲突。")
H2("3.4 泛化导向的基准设计")
B("基准在设计层面将泛化压力与混淆因素控制为可独立分析的维度：")
BL("生成器留出：训练/验证仅包含 2 个生成器（DeepSeek-V4-Flash、MiniMax-M2.5），测试集 AI 参与文档全部来自 6 个未见生成器。")
BL("同源家族控制：切分按 source_group_hash 分组构造，同源文档不跨切分。")
BL("覆盖率分层：混写文档按 AI 区间覆盖率逐桶配额（C1–C11），使各覆盖率区间样本充足（构造方法见 4.5 节）。")
BL("操作类型分层：五类局部人机混写操作各自保留完整分布，支持按操作类型独立分析。")

# ======================== 4 Dataset Construction ========================
H1("4 数据集构建")
B("本章按\u201c人类源收集→生成器选择→受控混写构造→来源真值记录→覆盖率控制→外部资源整合→切分\u201d的主线描述构建管线（图 2）。", indent=False)
FIGA(os.path.join(os.path.dirname(os.path.abspath(__file__)), "框架图.png"), "图 2  数据集构建管线总览")

H2("4.1 人类源收集与来源说明")
B("人类源共 153,116 行，覆盖 20 种语言，来源包括 Wiki-Lingua（多语言 howto）、SeqXGPT 语料 [19]、"
  "多领域新闻/问答/论文/作文/影评语料、SemEval 人类文本与 LLMTrace 人类文本 [8]，全部带版本化句边界标注与准入分层。"
  "人类源承担双重角色：人类负类样本与受控生成的人类基底文本。另附 27,868 行知乎中文长文补充（2019–2022，仅研究用途）。")
B("人类源被视为 human-authored 的依据包括三类证据。"
  "（1）时间先验：知乎补充子集的时间范围为 2019–2022 年，明确早于 ChatGPT（2022 年 11 月）及后续大模型的广泛可用性；"
  "Wiki-Lingua 语料来自 wikiHow 社区贡献者撰写的指南文章，其内容创建与平台发布均早于大语言模型时代。"
  "（2）来源审核机制：Wiki-Lingua 的 wikiHow 平台采用社区编辑审核流程；cred-* 系列来自经审核的新闻、问答、论文、作文与影评渠道。"
  "（3）上游数据集声明：SemEval-2024 Task 8 与 LLMTrace 的人类文本行继承其上游数据集的 human-authored 标注与验证流程。"
  "我们承认，对于部分来源（如 SeqXGPT 和 cred-* 系列），缺乏逐行的时间戳验证，无法完全排除后 LLM 时代内容混入的可能性。"
  "这一残余污染风险作为已知局限在 9.3 节披露。")

H2("4.2 生成器选择与分配")
B("受控生成侧选用 8 个当代前沿大模型，覆盖多个模型家族与提供方：国际侧 GPT-5.5、Gemini-3.7-Flash，"
  "国内侧 DeepSeek-V4-Flash、MiniMax-M2.5、GLM-5.3、Kimi-K2.7-Code、Qwen3.6-35B-A3B、HY3。")
B("选择多个模型家族的目的在于使基准能够评估检测器对\u201c未见生成器\u201d的泛化能力：训练/验证仅使用 2 个生成器，"
  "测试集 AI 参与文档全部来自 6 个未见生成器，逐行核验零交集。这一 2→6 分配使测试集分数本身即为跨生成器泛化压力测试。")
B("")
TBL(
    ["生成器", "受控生成文档数", "进入切分", "角色"],
    [
        ["DeepSeek-V4-Flash", "39,191", "train 35,300 / val 3,891", "训练/验证侧"],
        ["MiniMax-M2.5", "30,883", "train 28,489 / val 2,394", "训练/验证侧"],
        ["GPT-5.5", "23,072", "test 23,072", "测试留出"],
        ["Gemini-3.7-Flash", "22,399", "test 22,399", "测试留出"],
        ["GLM-5.3", "17,934", "test 17,934", "测试留出"],
        ["HY3", "17,518", "test 17,518", "测试留出"],
        ["Kimi-K2.7-Code", "15,322", "test 15,322", "测试留出"],
        ["Qwen3.6-35B-A3B", "14,652", "test 14,652", "测试留出"],
    ],
    caption="表 2  受控生成侧 8 个生成器及其切分归属",
)
B("图 3 汇总了所选模型家族在 OpenRouter 平台上的公开统计：面板 (A) 展示 2026 年 7 月至 9 月的逐日 token 处理量趋势，"
  "面板 (B) 展示截至 2026 年 9 月 29 日的 30 天滚动 token 总量。所选模型家族横跨多个提供方，全部具有可观的可观测调用量。")
FIG("fig3_adoption.png", "图 3  所选生成模型家族的真实采用度背景（OpenRouter 官方统计）")

H2("4.3 受控人机混写操作")
B("受控生成以人类源文档为基底：在句边界上选定操作对象（替换哪些句、在何处插入、从何处续写），"
  "以受控提示调用生成器产出目标片段，程序化拼装成文档并记录区间。"
  "五类局部人机混写操作为：句级替换、句级插入、多句插入、风格约束改写、续写，另有全文生成作为对照。")
B("操作类型作为字段逐行保留，使\u201c哪类混写操作更难检测/定位\u201d成为可分层分析的实证问题。")
TBL(
    ["人机混写操作", "train", "val", "test", "合计"],
    [
        ["句级替换 replacement", "20,281", "2,006", "36,626", "58,913"],
        ["句级插入 insertion", "18,395", "1,811", "31,210", "51,416"],
        ["风格约束改写 rewrite", "7,733", "775", "14,577", "23,085"],
        ["续写 continuation", "8,809", "887", "12,399", "22,095"],
        ["多句插入 multi-insertion", "6,081", "640", "9,257", "15,978"],
        ["（对照）全文生成 full generation", "2,490", "166", "6,828", "9,484"],
    ],
    caption="表 3  五类人机混写操作的分布",
)

H2("4.4 构造过程派生的字符级来源真值")
B("AI 片段的字符区间在文档组装时以半开区间 [s, e)、Unicode 码点偏移直接记录（gold_machine_spans），"
  "同时产出人类区间（gold_human_spans）与句级标签（sentence_labels）。"
  "由于操作锚定于句边界，区间端点天然落在句边界上；文档三分类由区间覆盖率推导，与定位真值严格自洽。")
B("这一\u201c构造过程派生真值\u201d的路线使真值不依赖标注者判断，不存在标注者间分歧，穷尽覆盖每个 AI 字符，"
  "可直接支撑区间完全匹配与边界误差等严格指标。每行同时保留 route_provenance（API 端点与模型标识）、"
  "prompt_version、task_id 与 variant_index，实现全链路生成溯源。")
B("图 4 展示了受控混写操作如何产生混合作者身份文档及其构造过程派生的字符级来源真值："
  "人类原文的某一句被选定后，前沿大模型生成替换内容，程序化拼装成混写文档，"
  "AI 片段的字符区间 [s, e) 在组装时直接记录。由同一份区间信息可推导字符来源序列、"
  "句级标签和文档级三分类，三种粒度严格自洽。")
FIG("fig_provenance.png", "图 4  受控混写操作与构造过程派生的字符级来源真值")


H2("4.5 覆盖率受控采样")
B("若不加控制，受控混写产生的 AI 区间覆盖率天然向低占比倾斜，检测器可能利用分布捷径获得虚高性能。"
  "为此，构建管线对混写文档的覆盖率实施 C1–C11（1%–99%）逐桶精确配额：以 min-max→min-Σ² 为目标求解最优分配"
  "（附最优性证书），并在\u201cAI 区间逐字符不变、文档文本为原文连续子串\u201d的硬约束下执行。"
  "最终各切分在全部覆盖率桶内样本充足，使覆盖率分层评测具有统计可靠性。")

H2("4.6 外部资源整合")
B("外部引入资源共 240,000 行，作为独立档案与受控生成侧可分可合："
  "SemEval-2024 Task 8-A 多语数据 170,702 行、LLMTrace 54,309 行、Wiki-Lingua 人类文本 14,989 行。"
  "外部行保留上游生成器、许可与样本定位字段；按切分纪律，外部数据不进入测试集。")

H2("4.7 泄漏感知切分")
B("切分遵循三条纪律。其一，测试集为受控生成侧专属留出，AI 参与文档全部来自训练/验证未见生成器。"
  "其二，外部引入不进入测试集。其三，切分按同源家族（source_group_hash）分组构造，同源文档不跨切分。"
  "构建期共有 87 行因来源无效或区间修复风险被永久隔离。"
  "最终切分为 train 366,618 / val 32,466 / test 202,762 行。")

# ======================== 5 Dataset Quality and Characterization ========================
H1("5 数据集质量与特征")
B("本章仅描述数据本身的质量与统计特征，不涉及任何检测算法的性能表现（算法评测见第 7 章）。", indent=False)

H2("5.1 质量控制")
TBL(
    ["质量门", "内容", "执行情况"],
    [
        ["逐任务硬门", "长度/句数/终止标点/拒绝复制/标记符号", "全部生成波次执行"],
        ["区间句对齐门", "AI 区间端点须落在句边界", "通过（构造保证）"],
        ["语言一致性门", "NFC 功能词 + 文字系统域校验", "约 6% 输出语言≠任务语言行，保留并披露"],
        ["全局精确去重", "NFC + SHA-256，跨波次全局", "已执行"],
        ["覆盖率配额门", "C1–C11 逐桶精确配额", "逐桶精确达成"],
    ],
    caption="表 4  构建期质量门",
)
H2("5.2 泄漏与重复审计")
TBL(
    ["审计类型", "结果"],
    [
        ["生成器重叠（train/val ∩ test）", "0"],
        ["同源家族跨切分", "0"],
        ["跨切分精确文本重复", "0（train-test: 0; train-val: 0; val-test: 0）"],
        ["构造期永久隔离", "87 行"],
    ],
    caption="表 5  泄漏审计结果",
)
H2("5.3 数据规模与标签分布")
TBL(
    ["项目", "数值"],
    [
        ["文档总数", "601,846"],
        ["切分", "366,618 / 32,466 / 202,762"],
        ["标签分布", "HUMAN 300,963 · PARTIAL_AI 190,085 · FULL_AI 110,798"],
        ["受控生成文档", "180,971（全部带字符级来源真值）"],
        ["外部引入资源", "240,000（独立档案，不进测试集）"],
    ],
    caption="表 6  数据集统计总卡",
)
H2("5.4 语言与生成器分布")
B("受控生成侧覆盖 20 种语言（测试集 18 语），训练集语言构成见图 5(a)。生成器构成见图 5(b)："
  "训练/验证侧 2 个生成器与测试留出侧 6 个生成器的规模一目了然。")
FIG("fig_language_generator.png", "图 5  语言与生成器构成：(a) 训练集语言分布；(b) 生成器分配")
H2("5.5 AI 覆盖率与文档长度分布")
B("混写文档的 AI 区间覆盖率经配额控制后各桶均衡，低、中、高占比混写均有充足样本。"
  "文档长度呈长尾分布，训练集中位数约 1,487 字符，最长 840k 字符。")
B("覆盖率经 C1–C11 逐桶配额后各桶均衡（图 8(A)），低、中、高占比混写均有充足样本，"
  "为覆盖率分层评测提供了统计可靠的基础。检测性能随覆盖率的变化见图 8(B)（第 7.3 节）。")
H2("5.6 可复现性与可审计性")
B("构建管线为确定性管线，全量编译双跑一致并以树哈希冻结校验。发布包含全部文件 SHA-256 清单、构建脚本与审计记录，"
  "使用者可核验任何文件副本的完整性。")

# ======================== 6 Evaluation Protocol ========================
H1("6 评测协议")
B("为统一评估检测方法在人机混写场景下的判别、定位与泛化能力，本文建立表 7 所示的评测协议。"
  "评测以文档级混合作者身份检测和字符级 AI 内容定位两个主要任务为核心，"
  "并进一步从 AI 内容覆盖率、人机混写操作、生成器和语言等维度进行分层分析，"
  "同时通过跨数据集迁移、改写扰动与捷径诊断考察方法的跨分布泛化、鲁棒性及对非语义统计特征的依赖。"
  "文档级评测同时采用 HUMAN / PARTIAL_AI / FULL_AI 三分类和 HUMAN / AI-involved 二分类两种设置："
  "前者用于区分完整的作者身份构成，后者将 PARTIAL_AI 与 FULL_AI 合并为 AI-involved，"
  "用于衡量检测器识别任意 AI 参与内容的能力。"
  "字符级定位则直接在 Unicode 字符空间比较预测结果与构造过程记录的 gold_machine_spans，"
  "同时评价 AI 内容覆盖识别、区间重合和边界恢复精度。"
  "所有正式检测方法仅允许以 text 字段作为模型输入；生成器、来源、操作类型、覆盖率及其他溯源元数据均不得作为检测特征。")
TBL(
    ["评测维度", "评测设置", "主要指标", "评测目的"],
    [
        ["文档三分类", "HUMAN / PARTIAL_AI / FULL_AI", "Macro-F1、Acc、逐类 P/R/F1", "整体判别能力"],
        ["AI 参与二分类", "HUMAN vs. AI-involved", "AUROC、BACC、F1(AI)", "是否存在任意 AI 内容"],
        ["字符级定位", "Unicode 字符空间比较", "Char-P / Char-R / Char-F1", "AI 内容整体定位"],
        ["区间与边界", "预测区间与真实区间匹配", "Exact-span F1、IoU@0.5、Boundary MAE", "区间匹配与边界恢复"],
        ["AI 覆盖率分层", "0–5 / 5–20 / 20–50 / 50–80 / 80–100%", "分桶 F1 与定位指标", "低占比检测能力"],
        ["混写操作分层", "五种操作 + 全文生成对照", "分操作 F1 与定位指标", "不同混写方式的难度"],
        ["生成器泛化", "2 已见 → 6 未见", "分生成器 F1、已见/未见差距", "跨生成器泛化"],
        ["语言分析", "按测试集语言分层", "分语言 AUROC、Macro-F1", "语言依赖性"],
        ["跨数据集迁移", "MixLoc 训练 → MixSet / LLMTrace", "F1 / AUROC", "跨分布可迁移性"],
        ["捷径诊断", "多数类、仅长度、仅来源", "Macro-F1", "非语义统计捷径"],
        ["改写鲁棒性", "原始 vs. T5 改写后", "AUROC 变化", "文本改写的影响"],
    ],
    caption="表 7  MixLoc 统一评测协议",
)
B("文档三分类以 Macro-F1 作为主要指标，以避免类别规模差异掩盖 PARTIAL_AI 或 FULL_AI 等类别上的性能退化；"
  "二分类则以 AUROC 衡量跨阈值排序能力，并在验证集确定的操作点报告 BACC、F1(AI) 与 Specificity。"
  "生成器泛化采用基准预定义的 2→6 固定留出设置：训练与验证仅包含 DeepSeek-V4-Flash 和 MiniMax-M2.5，"
  "测试集中的 AI 参与文档来自 6 个训练阶段未见生成器，同时保持 source_group_hash 跨切分零重叠。"
  "覆盖率与混写操作分析均基于预先定义的数据属性进行分层统计，不改变测试样本或模型输入，"
  "从而使不同条件下的性能能够在统一测试框架中直接比较。")
B("字符级定位的权威评测在原始 Unicode 码点空间进行。"
  "Character Precision / Recall / F1 衡量预测 AI 字符集合与真实 AI 字符集合的重合程度；"
  "Exact-span F1 要求预测区间与真实区间的起止位置完全一致；"
  "IoU@0.5-F1 在预测区间与真实区间交并比达到 0.5 时视为匹配；"
  "Boundary MAE 则统计匹配区间起点与终点相对于真实边界的平均绝对偏移。"
  "对于超过模型输入长度的文档，采用统一的长文档窗口化协议："
  "首先对完整文档分词并保证窗口边界落在 token 边界，"
  "对重叠窗口中同一 token 的预测概率进行平均聚合，"
  "再依据 tokenizer 的 offset mapping 将结果投影回原始字符空间，"
  "即遵循“先聚合、后投影”的处理顺序。"
  "所有方法均须报告该官方协议下的结果；"
  "其他窗口策略或定位方式可作为补充结果报告，以保证不同检测方法之间的可比性。")

H1("7 基准评测与分析")
B("本章通过代表性方法对基准进行技术验证，并从多个维度刻画现有检测方法的能力边界。", indent=False)
H2("7.1 基线方法与实验设置")
B("为覆盖监督学习、概率统计与零样本检测等主要技术路线，"
  "本文选择 XLM-R [10]、GLTR [11]、Fast-DetectGPT [12]、Binoculars [13] 和 DetectLLM [14] 作为代表性检测方法。")
TBL(
    ["方法", "类型", "Venue / 年份", "任务"],
    [
        ["多数类 / TF-IDF+LR", "平凡/浅层", "—", "A"],
        ["仅长度 / 仅来源 LR", "捷径诊断", "—", "A"],
        ["XLM-RoBERTa-span [10]", "监督（span 头）", "ACL 2020", "A/B"],
        ["XLM-RoBERTa-CLS [10]", "监督（CLS 头）", "ACL 2020", "A"],
        ["GLTR [11]", "零样本（token 秩）", "ACL 2019-D", "A"],
        ["Fast-DetectGPT [12]", "零样本（概率曲率）", "ICLR 2024", "A"],
        ["Binoculars [13]", "零样本（双模型困惑度，改编版）", "ICML 2024", "A"],
        ["DetectLLM-LRR [14]", "零样本（对数秩）", "EMNLP 2023-F", "A"],
    ],
    caption="表 7  基线方法",
    note="注：监督模型经完整微调（分层抽样 22,500 篇，单轮全遍历 2,813 步）。",
)
H2("7.2 整体检测性能")
B("图 6 汇总了全部方法在全量测试集上的文档级检测性能：面板 (A) 为二分类 AUROC，面板 (B) 为平衡准确率，面板 (C) 为三分类宏 F1 与捷径诊断基线。图 7 展示了监督模型的混淆矩阵。")
FIG("fig_main_results.png", "图 6  文档级基准检测结果（全量测试集 n=202,762）：(A) AUROC；(B) BACC；(C) 三分类 + 捷径诊断")
FIG("fig_confusion.png", "图 7  三分类混淆矩阵（行归一化，全量测试集）")
if FR:
    TBL(["方法", "Acc", "Macro-F1", "Weighted-F1"],
        [[m, _f3(v["acc"]), _f3(v["macro_f1"]), _f3(v["weighted_f1"])] for m, v in FR["doc3"].items()],
        caption="表 8  文档三分类结果（全量测试集）")
    TBL(["方法", "AUROC", "BACC", "F1(AI)", "Spec"],
        [[m, _f3(v["auroc"]), _f3(v["bacc"]), _f3(v["f1"]), _f3(v.get("specificity"))] for m, v in FR["binary"].items()],
        caption="表 9  二分类结果（全量测试集，BACC 调优操作点）")
H2("7.3 不同 AI 覆盖率下的检测性能")
FIG("fig4_coverage.png", "图 8  覆盖率配额设计 (A) 与检测性能 vs 覆盖率 (B)")
if SR:
    cov = SR["stratified"]["XLM-R-span"]["coverage"]
    parts = ", ".join(f"{k}% 桶 F1={v['f1']:.2f}" for k, v in cov.items())
    B(f"监督模型在低 AI 覆盖率区间表现出显著的性能下降：XLM-R-span 逐桶结果为 {parts}。"
      "低占比混写检测的困难性是本基准揭示的核心发现之一。")
H2("7.4 不同人机混写操作下的性能")
if SR:
    ops = SR["stratified"]["XLM-R-span"]["operation"]
    B("按操作类型的分层分析显示，句级替换与风格约束改写在当前评测中表现出较低的检测性能；"
      "上下文保持可能是解释之一，但仍需进一步控制实验验证。")
H2("7.5 对未见生成器的泛化")
FIG("fig_generator_heatmap.png", "图 9  各方法按生成器的二分类 F1（虚线左侧为训练已见生成器，右侧为测试未见生成器）")
if SR:
    g = SR["generator_gap"]
    a = "；".join(f"{m}：已见 {v['val_seen_gen_f1']:.3f} → 未见 {v['test_unseen_gen_f1']:.3f}" for m, v in g.items())
    B("图 9 展示了按生成器的三分类 F1 分解。关键发现：PARTIAL_AI 检测在已见生成器上 F1 为 0.78–0.80，"
  "而在 6 个未见生成器上骤降至 0.55–0.64——泛化差距约 0.15–0.25。"
  "HUMAN F1 在所有生成器子集上均较高（0.79–0.87），但 FULL_AI F1 在全部生成器上接近零（0.00–0.09），"
  "表明现有检测器几乎无法区分混写与全文 AI。整体 Macro-F1 在所有生成器上仅 0.49–0.55，"
  "远低于同一模型在全文级基准上的 0.99+ 水平。")
H2("7.6 字符级定位")
if SR:
    L = SR["localization"]
    B(f"字符级定位结果（n={L['n_docs']} 混写窗口）：字符精确率 {L['char_precision']:.3f}、召回率 {L['char_recall']:.3f}、"
      f"F1 {L['char_f1']:.3f}；区间完全匹配 F1 {L['span_exact_f1']:.3f}、IoU@0.5 F1 {L['span_iou50_f1']:.3f}；"
      f"边界误差（MAE）总体 {L['boundary_mae_overall']:.1f} 字符。区间完全匹配 F1 明显低于字符级 F1，"
      "说明精确边界定位仍是开放难题。")
H2("7.7 捷径与混淆诊断")
if SR:
    d = SR["shortcut_diagnostic"]
    B(f"捷径诊断结果：多数类 mF1={d['Majority']['macro_f1']:.3f}、仅长度 mF1={d['Length-only LR']['macro_f1']:.3f}、"
      f"仅来源 mF1={d['Source-only LR']['macro_f1']:.3f}。长度特征构成真实的统计捷径，来源特征在训练可见时可达到约 0.98 mF1——"
      "这一发现直接支持了本基准采用 text-only 输入纪律与来源感知切分的必要性。")
H2("7.8 跨数据集泛化")
if HO:
    rows = [[k, f"{v['n']:,}", _f3(v["XLM-R-span"]["auroc"]), _f3(v["XLM-R-CLS"]["auroc"]), _f3(v["Fast-DetectGPT"]["auroc"])]
            for k, v in HO.items()]
    TBL(["外部数据集", "n", "XLM-R-span", "XLM-R-CLS", "Fast-DetectGPT"], rows,
        caption="表 10  跨数据集迁移（本基准训练 → MixSet / LLMTrace）")
H2("7.9 附加鲁棒性分析")
FIG("fig_attack.png", "图 10  改写攻击前后 AUROC 对比（英语子集 n=800）")
if AT:
    B("文本改写与释义已被证明可能显著改变 AI 生成文本检测器的判别结果 [24, 26]。改写攻击实验（英语子集 n=800）显示，T5 改写未降低监督检测器的性能，反而使检测更容易——"
      "可能因为改写工具自身引入了新的可检测特征。零样本方法中 GLTR 受改写影响最大（AUROC 从 0.55 降至 0.41）。")
if LA:
    B("分语言 AUROC 分析揭示了显著的语言依赖性：日语最易检测（多数方法 0.93+），"
      "英语为最难语言（各方法 AUROC 接近随机），基于 token 秩的零样本方法在俄语上出现方向反转。")
    FIG("fig_lang_f1_full.png", "图 11  分语言三分类 Macro-F1 热力图（全量测试集 n=202,762）")

# ======================== 8 Data Records, Availability and Usage ========================
H1("8 数据记录、可用性与使用指南")
H2("8.1 数据记录")
B("数据集以两个语义并列的档案发布：（1）受控生成档案——含 180,971 篇 AI 参与文档及全量人类源、外部引入资源；"
  "（2）最终切分——train/val/test 三个 JSONL 文件，共 601,846 行。发布文件结构：（1）mixloc_v1_train.jsonl.gz / mixloc_v1_val.jsonl.gz / mixloc_v1_test.jsonl.gz（最终切分）；（2）mixloc_external_pool.jsonl.gz（外部引入档案，240,000 行）；（3）mixloc_generation_archive.jsonl.gz（受控生成全量档案，180,971 行）。")
H2("8.2 数据模式（字段表）")
TBL(
    ["字段", "类型", "说明"],
    [
        ["text", "string", "文档全文（Unicode）"],
        ["label", "enum", "HUMAN / PARTIAL_AI / FULL_AI"],
        ["gold_machine_spans", "list[[int,int]]", "AI 字符区间（半开，Unicode 码点偏移）"],
        ["gold_human_spans", "list[[int,int]]", "人类字符区间"],
        ["sentence_labels", "list[int]", "句级 0/1 标签"],
        ["language", "string", "ISO 639-1 语言代码"],
        ["generator", "string", "生成器标识（自建行）"],
        ["operation", "string", "人机混写操作类型"],
        ["coverage", "float", "AI 字符占比（由区间推导）"],
        ["source_group_hash", "string", "同源泄漏控制单元"],
        ["route_provenance", "string", "API 端点与模型标识"],
        ["split", "enum", "train / val / test"],
    ],
    caption="表 11  数据模式（核心字段）",
)
H2("8.3 推荐使用指南")
BL("官方切分不可变更；任何自拟再划分须按 source_group_hash 分组。")
BL("检测器输入只允许 text 字段；一切溯源字段排除在特征之外。")
BL("Unicode 偏移解析：区间为半开 [s, e)，基于 Unicode 码点（非字节/UTF-16 码元）。")
BL("外部引入档案可独立使用或与受控生成侧组合，但不进入测试集。")
H2("8.4 代码、校验与版本")
B("构建代码、评测协议参考实现与全量 SHA-256 校验清单一并发布。"
  "发布平台：GitHub（代码与评测协议）+ HuggingFace Datasets（数据）。"
  "许可证：CC BY-NC-SA 4.0（研究用途，非商业）。知乎子集仅限研究用途、不得再分发。"
  "版本号 v1.0，数据卡随发布提供。")

# ======================== 9 Ethics, Biases and Limitations ========================
H1("9 伦理声明、偏差与局限性")
H2("9.1 伦理与许可")
B("全部人工源来自公开可获取渠道并逐行保留许可信息；知乎子集仅限研究用途并保留原文链接以支持撤除请求；"
  "受控生成经由正规 API 路由完成并完整留痕。数据集可能被用于训练更难检测的生成或改写工具，"
  "我们通过将混写操作类型、生成器与提示策略全部显式化，使对抗性使用的痕迹本身可被研究。")
H2("9.2 偏差与混淆因素")
B("（1）来源偏差：来源元数据单特征可达约 0.98 mF1，须按 6.7 节纪律使用。"
  "（2）语言不均衡：英语占训练集约 42%，其他语言样本量差异较大。既有研究表明，AI 文本检测器可能对不同语言背景的作者产生系统性性能差异 [25]。"
  "（3）生成器不均衡：训练侧仅 2 个生成器，测试侧 6 个，各类别支撑数不同。"
  "（4）覆盖率受控分布改变了生成后的自然长度分布。"
  "（5）约 6% 生成行输出语言与任务语言不一致（保留并披露）。")
H2("9.3 局限性")
B("（1）人工源的 LLM 污染无法完全排除。"
  "（2）受控混写逼近但无法完全复现自然发生的人机协作编辑。"
  "（3）生成器集合将随时间快速迭代，已有研究也表明基于训练数据的检测方法在面对未见生成器时可能出现明显的泛化退化 [24, 30]。"
  "（4）20 种语言不覆盖全球所有语言。"
  "（5）字符级来源真值精确，不意味着自然写作行为完全真实。")

# ======================== 10 Conclusion ========================
H1("10 结论")
B("本文构建并发布了一个面向人机混写检测与字符级定位的大规模多语言基准。"
  "通过受控人机混写操作在文档组装过程中直接记录 AI 字符区间，基准提供了构造过程派生的穷尽字符级来源真值；"
  "通过 2→6 生成器留出与同源家族零重叠切分将泛化内建于数据结构；"
  "通过覆盖率逐桶配额阻断分布捷径。"
  "我们期望该基准推动检测研究从\u201c整篇是否 AI\u201d走向\u201c哪一段是 AI、在什么条件下仍然可靠\u201d的更精细问题形态。")

# ======================== 参考文献 ========================
H1("参考文献", pb=True)
REFS = [
    "[1]  Guo B, Zhang X, Wang Z, et al. How Close is ChatGPT to Human Experts? Comparison Corpus, Evaluation, and Detection. arXiv:2301.07597, 2023.",
    "[2]  Wang Y, Mansurov J, Ivanov P, et al. M4: Multi-generator, Multi-domain, and Multi-lingual Black-Box Machine-Generated Text Detection. Proc. EACL, 2024.",
    "[3]  Uchendu A, Le T, Shu K, Lee D. TuringBench: A Benchmark Environment for Turing Test in the Age of Neural Text Generation. Findings of EMNLP, 2021.",
    "[4]  Dugan L, Hwang A, Trhlik F, et al. RAID: A Shared Benchmark for Robust Evaluation of Machine-Generated Text Detectors. Proc. ACL, 2024, 12463-12492.",
    "[5]  Macko D, Moro R, Uchendu A, et al. MULTITuDE: Large-Scale Multilingual Machine-Generated Text Detection Benchmark. Proc. EMNLP, 2023, 9960-9987.",
    "[6]  Dugan L, Ippolito D, Kirubarajan A, Callison-Burch C. RoFT: A Tool for Evaluating Human Detection of Machine-Generated Text. Proc. EMNLP: System Demonstrations, 2020, 189-196.",
    "[7]  Zhang Q, Gao C, Chen D, et al. LLM-as-a-Coauthor: Can Mixed Human-Written and Machine-Generated Text Be Detected? Findings of NAACL, 2024, 409-436.",
    "[8]  Tolstykh I, et al. LLMTrace: A Corpus for Classification and Fine-Grained Localization of LLM-Generated Text. arXiv:2509.21269, 2025.",
    "[9]  Su Z, et al. HACo-Det: Fine-Grained Machine-Generated Text Detection under Human-AI Coauthoring. Proc. ACL, 2025.",
    "[10] Conneau A, Khandelwal K, Goyal N, et al. Unsupervised Cross-lingual Representation Learning at Scale. Proc. ACL, 2020, 8440-8451.",
    "[11] Gehrmann S, Strobelt H, Rush A. GLTR: Statistical Detection and Visualization of Generated Text. Proc. ACL: System Demonstrations, 2019, 111-116.",
    "[12] Bao G, Zhao Y, Teng Z, et al. Fast-DetectGPT: Efficient Zero-Shot Detection of Machine-Generated Text via Conditional Probability Curvature. ICLR, 2024.",
    "[13] Hans A, Schwarzschild A, Cherepanova V, et al. Spotting AI's Touch: Identifying LLM-Generated Text Through Intrinsic Contextual Contrast. ICML, 2024.",
    "[14] Su J, Zhuo T, Wang D, Nakov P. DetectLLM: Leveraging Log Rank Information for Zero-Shot Detection of Machine-Generated Text. Findings of EMNLP, 2023, 12395-12412.",
    "[15] Al Bataineh A, Sickler R, Kurcz K, Pedersen K. AI-Generated vs. Human Text: Introducing a New Dataset for Benchmarking and Analysis. IEEE Trans. on Artificial Intelligence, 2025.",
    "[16] Tao Z, Chen Y, Xi D, Li Z, Xu W. Towards Reliable Detection of LLM-Generated Texts: A Comprehensive Evaluation Framework with CUDRT. arXiv:2406.09056, 2024.",
    "[17] He X, Shen X, Chen Z, Backes M, Zhang Y. MGTBench: Benchmarking Machine-Generated Text Detection. arXiv:2303.14822, 2023.",
    "[18] Wang Y, Mansurov J, Ivanov P, et al. M4GT-Bench: Evaluation Benchmark for Black-Box Machine-Generated Text Detection. Proc. ACL, 2024, 3964-3992.",
    "[19] Wang P, Li L, Ren K, et al. SeqXGPT: Sentence-Level AI-Generated Text Detection. Proc. EMNLP, 2023, 1144-1156.",
    "[20] Su Z, Wu X, Zhou W, et al. HC3 Plus: A Semantic-Invariant Human ChatGPT Comparison Corpus. arXiv:2309.02731, 2023.",
    "[21] Mitchell E, Lee Y, Khazatsky A, Manning C D, Finn C. DetectGPT: Zero-Shot Machine-Generated Text Detection Using Probability Curvature. Proc. ICML, 2023, 24950-24962.",
    "[22] Liu X, Zhang Z, Wang Y, et al. CoCo: Coherence-Enhanced Machine-Generated Text Detection Under Low Resource With Contrastive Learning. Proc. EMNLP, 2023, 16167-16188.",
    "[23] Crothers E, Japkowicz N, Viktor H L. Machine-Generated Text: A Comprehensive Survey of Threat Models and Detection Methods. IEEE Access, 2023.",
    "[24] Sadasivan V S, Kumar A, Balasubramanian S, et al. Can AI-Generated Text Be Reliably Detected? ICLR, 2024.",
    "[25] Liang W, Yuksekgonul M, Mao Y, Wu E, Zou J. GPT Detectors Are Biased Against Non-Native English Writers. Patterns, 4: 100779, 2023.",
    "[26] Mitrovic S, Andreoletti D, Ayoub O. ChatGPT or Human? Detect and Explain. arXiv:2301.13852, 2023.",
    "[27] Zellers R, Holtzman A, Rashkin H, et al. Defending Against Neural Fake News. NeurIPS, 32, 2019.",
    "[28] Hayawi K, Shahriar S, Mathew S S. The Imitation Game: Detecting Human and AI-Generated Texts in the Era of Large Language Models. arXiv:2307.12166, 2023.",
    "[29] Peng X, Zhou Y, He B, et al. Hidding the Ghostwriters: An Adversarial Evaluation of AI-Generated Student Essay Detection. arXiv:2402.00412, 2024.",
    "[30] Xu H, Ren J, He P, et al. On the Generalization of Training-Based ChatGPT Detection Methods. arXiv:2310.01307, 2023.",
]
for ref in REFS:
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(3)
    _sr(p, ref, 10, False, C_BODY)

doc.save(OUT)
print("SAVED:", OUT)
