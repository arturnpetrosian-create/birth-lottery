"""
Человекочитаемые объяснения метрик (шаблоны, без LLM).
"""
from __future__ import annotations

from domain.prb_ever_lived import EVER_LIVED_PRB_2022, format_tiny_percent, one_in_reciprocal


def narrative_markdown_ru(
    *,
    country_ru: str,
    year: int,
    pct_world_year: float,
    one_in_world_year: float,
    births_country_year: float,
    births_world_year: float,
    share_prb: float | None,
) -> str:
    """Связный текст для блока «ответ системы»."""
    def fi(x: float) -> str:
        if not (x > 0) or x == float("inf"):
            return "—"
        return f"{x:,.0f}".replace(",", "\u00a0")

    lines: list[str] = []
    lines.append(
        f"Если опираться на оценки **ООН WPP** для **{year} года**, "
        f"в **{country_ru}** родилось порядка **{fi(births_country_year)}** человек из мирового итога "
        f"**~{fi(births_world_year)}** рождений за этот календарный год."
    )
    lines.append(
        f"Доля **{country_ru}** в этом мировом итоге — около **{pct_world_year:.2f}\u202f%**. "
        "Это удобно представить как мысленный эксперимент: *равновероятно выбрать одного "
        "рождённого в мире именно в этом году*"
        + (
            f" — тогда порядок «**1 из {fi(one_in_world_year)}**» по масштабу совпадает с этой долей."
            if fi(one_in_world_year) != "—"
            else "."
        )
    )
    lines.append(
        "Это **не** «вероятность того, что вы родились»: для уже живущего человека такие фразы "
        "статистически некорректны; здесь только **условная доля** по опубликованным рядам рождений."
    )
    if share_prb is not None and share_prb > 0:
        recip = one_in_reciprocal(share_prb)
        if recip < 1e15:
            lines.append(
                f"Отдельно: на шкале оценки PRB (~**{EVER_LIVED_PRB_2022 // 1_000_000_000}\u202fмлрд** "
                "рождений за глубокую историю) эта пара «страна + год» составляет около **"
                f"{format_tiny_percent(share_prb)}\u202f%** — см. раздел §\u202fVI ниже с точными формулами."
            )
    return "\n\n".join(lines)
