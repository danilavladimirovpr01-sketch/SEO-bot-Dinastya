ARTICLE_TEMPLATE = """Напиши {content_type} на тему: «{topic}»

Основные ключевые слова: {main_keywords}
LSI-ключи: {lsi_keywords}
Желаемый объём: {word_count} слов

{structure_section}
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
        competitors_section=competitors_section,
        additional_instructions=additional_instructions,
    )
