ARTICLE_TEMPLATE = """Напиши {content_type} на тему: «{topic}»

{h1_section}
{keywords_section}
{thematic_section}
{highlight_section}
Желаемый объём: {word_count} символов без пробелов

{structure_section}
{aeo_section}
{meta_section}
{competitors_section}
{additional_instructions}
"""


def build_prompt(
    topic: str,
    content_type: str,
    main_keywords: str,
    h1: str = "",
    thematic_words: str = "",
    highlight_words: str = "",
    word_count: int = 3000,
    structure: str = "",
    aeo_questions: str = "",
    meta_title: str = "",
    meta_description: str = "",
    competitors: str = "",
    additional: str = "",
) -> str:
    content_type_map = {
        "article": "информационную статью в блог",
        "service": "продающую страницу услуги (с блоками: определение, причины, симптомы, диагностика, лечение в Центре, преимущества)",
        "disease": "страницу заболевания/расстройства (с блоками: что это, причины, формы/стадии, симптомы, осложнения, диагностика, лечение в Центре, почему важно обратиться, преимущества)",
        "faq": "FAQ-страницу",
    }

    # H1
    h1_section = ""
    if h1.strip():
        h1_section = f"H1 заголовок (НЕ включай в текст статьи, только для ориентира): {h1}"

    # Keywords with frequency
    keywords_section = _build_keywords_section(main_keywords)

    # Thematic words
    thematic_section = ""
    if thematic_words.strip():
        thematic_section = (
            "Тематические слова (используй в любой удобной форме, органично по тексту):\n"
            f"{thematic_words}"
        )

    # Highlight words
    highlight_section = ""
    if highlight_words.strip():
        highlight_section = (
            "Слова из подсветки в поисковой выдаче (постарайся включить в текст):\n"
            f"{highlight_words}"
        )

    structure_section = ""
    if structure.strip():
        structure_section = f"Желаемая структура:\n{structure}"

    aeo_section = ""
    if aeo_questions.strip():
        aeo_section = (
            f"AEO-оптимизация — обязательно включи FAQ-блок в конце статьи с ответами на эти вопросы:\n{aeo_questions}"
        )

    meta_section = ""
    if meta_title.strip() or meta_description.strip():
        parts = []
        if meta_title.strip():
            parts.append(f"Используй этот Meta Title: {meta_title}")
        if meta_description.strip():
            parts.append(f"Используй этот Meta Description: {meta_description}")
        meta_section = "Мета-теги:\n" + "\n".join(parts)

    competitors_section = ""
    if competitors.strip():
        competitors_section = (
            f"Ссылки на конкурентов для анализа (учти их структуру и полноту):\n{competitors}"
        )

    additional_instructions = ""
    if additional.strip():
        additional_instructions = f"Дополнительные инструкции:\n{additional}"

    return ARTICLE_TEMPLATE.format(
        content_type=content_type_map.get(content_type, content_type),
        topic=topic,
        h1_section=h1_section,
        keywords_section=keywords_section,
        thematic_section=thematic_section,
        highlight_section=highlight_section,
        word_count=word_count,
        structure_section=structure_section,
        aeo_section=aeo_section,
        meta_section=meta_section,
        competitors_section=competitors_section,
        additional_instructions=additional_instructions,
    )


def _build_keywords_section(main_keywords: str) -> str:
    """Parse keywords with optional frequency and build prompt section."""
    lines = [l.strip() for l in main_keywords.strip().split("\n") if l.strip()]

    has_frequency = any("—" in l or "-" in l for l in lines)

    if has_frequency:
        result = "Ключевые фразы (используй в ТОЧНОЙ форме, строго указанное количество раз):\n"
        for line in lines:
            # Parse "ключ — N" or "ключ - N" format
            for sep in ["—", "–", "-"]:
                if sep in line:
                    parts = line.rsplit(sep, 1)
                    if len(parts) == 2 and parts[1].strip().isdigit():
                        keyword = parts[0].strip()
                        count = parts[1].strip()
                        result += f"- «{keyword}» — {count} раз\n"
                        break
            else:
                # No separator found, treat as keyword without count
                result += f"- «{line}»\n"
    else:
        # Old format: comma-separated keywords
        keywords = [k.strip() for k in main_keywords.split(",") if k.strip()]
        result = "Основные ключевые слова:\n"
        for kw in keywords:
            result += f"- {kw}\n"

    return result.strip()
