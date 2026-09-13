from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".deps"))

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


OUTPUT = ROOT / "paper" / "AI工具使用说明.docx"


def set_run_font(run, east_asia="宋体", latin="Times New Roman", size=10.5, bold=False):
    run.font.name = latin
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor(0, 0, 0)
    fonts = run._element.get_or_add_rPr().get_or_add_rFonts()
    fonts.set(qn("w:ascii"), latin)
    fonts.set(qn("w:hAnsi"), latin)
    fonts.set(qn("w:eastAsia"), east_asia)


def set_paragraph_format(paragraph, first_line=True, before=0, after=0):
    fmt = paragraph.paragraph_format
    fmt.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    fmt.line_spacing = 1.3
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.first_line_indent = Cm(0.74) if first_line else Cm(0)
    fmt.keep_together = True


def add_body(doc, text, first_line=True):
    paragraph = doc.add_paragraph()
    set_paragraph_format(paragraph, first_line=first_line)
    set_run_font(paragraph.add_run(text))
    return paragraph


def add_section_heading(doc, text):
    paragraph = doc.add_paragraph()
    set_paragraph_format(paragraph, first_line=False, before=6, after=2)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.keep_with_next = True
    set_run_font(paragraph.add_run(text), east_asia="黑体", size=10.5, bold=True)
    return paragraph


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for node in (begin, instr, separate, text, end):
        run._r.append(node)
    set_run_font(run, size=10.5)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(10.5)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    title_style = doc.styles["Title"]
    title_style.font.name = "Times New Roman"
    title_style.font.size = Pt(16)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(0, 0, 0)
    title_style._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
    title_style_ppr = title_style._element.get_or_add_pPr()
    title_border = title_style_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_style_ppr.remove(title_border)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(10)
    title.paragraph_format.keep_with_next = True
    title_ppr = title._p.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)
    set_run_font(title.add_run("AI工具使用说明"), east_asia="黑体", size=16, bold=True)

    add_body(
        doc,
        "本参赛队在竞赛过程中使用了人工智能工具，主要用于题意梳理、候选方法比较、程序辅助、结果核查、图表与文档排版以及语言润色。模型方案、参数选择、实验结果和论文表述均由参赛队结合题目附件、程序运行记录与结果文件审查后确认，参赛队对最终提交内容承担责任。",
    )

    add_section_heading(doc, "一  使用的AI工具")
    add_body(
        doc,
        "使用的工具为OpenAI ChatGPT与Codex，使用平台在线提供的GPT-5系列模型及其代码辅助能力。由于在线服务会持续更新，具体子版本以相应会话和平台记录为准。",
    )

    add_section_heading(doc, "二  使用目的与环节")
    add_body(
        doc,
        "AI主要参与以下辅助环节：第一，整理四个问题之间的依赖关系，比较确定性优化、非前视预测优化、滚动调整和历史价格情景鲁棒优化等候选方案；第二，辅助编写和调试Python程序，检查单位换算、储能状态转移、能量平衡、非前视边界与输出格式；第三，协助汇总实验结果，生成图表初稿并检查论文中的符号、数值和文件名称是否一致；第四，对论文草稿进行语言润色和Word排版。AI未替代原始数据、实际程序运行结果或参赛队对最终方案的确认。",
    )

    add_section_heading(doc, "三  主要提示方式与使用过程")
    add_body(
        doc,
        "使用过程中，参赛队按任务逐步提供题面、附件数据、已确定的建模口径和阶段性结果，并通过限定输入、输出和验证条件约束AI。典型提示包括：解读题面并梳理各问的目标与约束；比较候选模型的适用性、可解释性和竞赛实现成本；根据给定数据生成可复现的程序框架；检查未来信息是否进入当前决策；依据已经冻结的实验数字撰写结果分析；核对图表、正文与结果文件之间的一致性。对于影响建模结论的内容，采用“提出候选方案—运行程序—核对结果—修改表述”的方式迭代处理。",
    )

    add_section_heading(doc, "四  采纳 修改与核验情况")
    add_body(
        doc,
        "AI输出主要作为分析建议、代码草稿和文字初稿使用。参赛队对纳入论文的内容进行了必要修改和核验：依据题目附件修正变量定义、时间尺度和结算规则；通过程序运行、单元测试和结果工作簿核对目标函数值、储能边界、能量平衡与关键统计量；对问题2至问题4检查非前视信息边界，对问题3的安全裕度参数进行费用与供能缺口权衡，对问题4区分可实施历史价格情景与仅供事后比较的真实价格参照；对论文中的数字、图表、符号和结论进行交叉核对，并保留适用范围、数据年份和外推限制。语言润色类建议在不改变技术含义的前提下采用，无法由数据或计算结果支持的表述未作为结论使用。",
    )

    add_body(
        doc,
        "本说明依据《全国大学生数学建模竞赛人工智能工具使用规定（2026年试行）》编制，用于公开披露本作品中AI工具的使用情况。",
    )

    add_page_number(section.footer.paragraphs[0])
    core = doc.core_properties
    core.title = "AI工具使用说明"
    core.subject = "数学建模竞赛论文AI工具使用披露"
    core.author = "参赛队"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
