ARTICLE_TEMPLATE = """Напиши {content_type} на тему: «{topic}»

Основные ключевые слова: {main_keywords}
LSI-ключи: {lsi_keywords}
Желаемый объём: {word_count} слов

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
    lsi_keywords: str = "",
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
        "service": "продающую страницу услуги",
        "faq": "FAQ-страницу",
    }

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
        main_keywords=main_keywords,
        lsi_keywords=lsi_keywords or "не указаны",
        word_count=word_count,
        structure_section=structure_section,
        aeo_section=aeo_section,
        meta_section=meta_section,
        competitors_section=competitors_section,
        additional_instructions=additional_instructions,
    )
