"""
Centralized loguru configuration for the MAGUS DM engine.

Log files:
  logs/app.log    — INFO+  : request summaries, NPC gen results, token counts
  logs/claude.log — DEBUG  : full Claude prompts, responses, token breakdown
  logs/stats.log  — DEBUG  : stat calculation step-by-step details

Usage:
    from engine.magus.core.logger import get_logger, log_claude_call

    logger = get_logger(__name__)
    logger.info("Something happened")
    logger.debug("Detailed data: {data}", data=my_dict)

Level control via LOG_LEVEL env var (default: INFO).
Set LOG_LEVEL=DEBUG to see everything in the console.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from loguru import logger

ROOT     = Path(__file__).parent.parent.parent.parent
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

_CONSOLE_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
_CONFIGURED    = False


def _setup() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    logger.remove()

    # Console — level controlled by LOG_LEVEL env var
    logger.add(
        sys.stderr,
        level=_CONSOLE_LEVEL,
        colorize=True,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> - <level>{message}</level>",
    )

    # app.log — INFO+: requests, NPC results, token counts
    logger.add(
        LOGS_DIR / "app.log",
        level="INFO",
        rotation="10 MB",
        retention="14 days",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name} - {message}",
    )

    # claude.log — DEBUG: full prompts + responses
    logger.add(
        LOGS_DIR / "claude.log",
        level="DEBUG",
        rotation="20 MB",
        retention="7 days",
        encoding="utf-8",
        filter=lambda r: r["extra"].get("log_target") == "claude",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )

    # stats.log — DEBUG: stat calculation details
    logger.add(
        LOGS_DIR / "stats.log",
        level="DEBUG",
        retention="7 days",
        rotation="10 MB",
        encoding="utf-8",
        filter=lambda r: r["extra"].get("log_target") == "stats",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    )


_setup()

claude_logger = logger.bind(log_target="claude")
stats_logger  = logger.bind(log_target="stats")


def get_logger(name: str):
    """Return a logger bound to a module name."""
    return logger.bind(name=name)


# ---------------------------------------------------------------------------
# Claude API helper
# ---------------------------------------------------------------------------

def log_claude_call(
    *,
    stage: str,
    model: str,
    system_blocks: list[dict] | None = None,
    messages: list[dict] | None = None,
    response=None,
    error: Exception | None = None,
) -> None:
    """
    Log a Claude API call at two levels:
      - INFO  → app.log  : stage, model, token counts with billed breakdown
      - DEBUG → claude.log : full prompt + response content
    """
    if error:
        logger.error("Claude API error | stage={stage} | {error}", stage=stage, error=error)
        return

    usage = getattr(response, "usage", None)
    input_tokens   = getattr(usage, "input_tokens", 0) or 0
    output_tokens  = getattr(usage, "output_tokens", 0) or 0
    cache_read     = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_creation = getattr(usage, "cache_creation_input_tokens", 0) or 0
    # Ténylegesen számlázott input = teljes input - cache találat
    billed_input   = input_tokens - cache_read

    logger.info(
        "Claude [{stage}] "
        "input={input} (számlázott={billed} | cache_hit={cr} | cache_write={cw}) "
        "output={output}",
        stage=stage,
        input=input_tokens,
        billed=billed_input,
        cr=cache_read,
        cw=cache_creation,
        output=output_tokens,
    )

    # Full detail → claude.log
    if system_blocks:
        total_sys_chars = sum(len(b.get("text", "")) for b in system_blocks)
        claude_logger.debug(
            "=== {stage} SYSTEM ({n} blocks, ~{chars} chars) ===\n{blocks}",
            stage=stage,
            n=len(system_blocks),
            chars=total_sys_chars,
            blocks="\n---\n".join(
                f"[block {i} cache={b.get('cache_control')}]\n{b.get('text','')[:2000]}"
                for i, b in enumerate(system_blocks)
            ),
        )

    if messages:
        claude_logger.debug(
            "=== {stage} MESSAGES ===\n{msgs}",
            stage=stage,
            msgs="\n---\n".join(
                f"[{m['role']}] {str(m.get('content',''))[:2000]}"
                for m in messages
            ),
        )

    if response:
        content_text = ""
        for block in getattr(response, "content", []):
            if hasattr(block, "text"):
                content_text += block.text[:2000]
            elif hasattr(block, "input"):
                import json
                content_text += json.dumps(block.input, ensure_ascii=False)[:2000]

        claude_logger.debug(
            "=== {stage} RESPONSE (stop={stop}) ===\n{content}\n"
            "tokens: input={input} output={output} cache_read={cr} cache_write={cw}",
            stage=stage,
            stop=getattr(response, "stop_reason", "?"),
            content=content_text,
            input=input_tokens,
            output=output_tokens,
            cr=cache_read,
            cw=cache_creation,
        )


# ---------------------------------------------------------------------------
# Stat calculation helper
# ---------------------------------------------------------------------------

def log_stat_calc(
    *,
    kaszt: str,
    szint: int,
    props: dict,
    result: dict,
    details: dict | None = None,
) -> None:
    """Log stat calculation to stats.log with step-by-step breakdown at DEBUG."""
    r = result
    d = details or {}

    prop_line = "  ".join(f"{k[:3]}={v}" for k, v in props.items())

    # Bonus components (passed from combat.py)
    gy  = d.get("gy", "?")
    ue  = d.get("ue", "?")
    er  = d.get("er", "?")
    eg  = d.get("eg", "?")
    int_b = d.get("int_bonus", "?")

    ke_bonus_str = f" +ke_bonus({d['ke_bonus']})" if d.get("ke_bonus") else ""

    stats_logger.debug(
        "╔══ STAT CALC | {kaszt} {szint}. szint ══╗\n"
        "  Props:  {props}\n"
        "  ─── Bónuszok (érték - 10, min 0) ───\n"
        "  gy={gy}  üe={ue}  er={er}  eg={eg}  int={int_b}\n"
        "  ─── Harci értékek ───\n"
        "  KÉ  = alap({ake}) + gy({gy}) + üe({ue}){ke_b} = {ke}\n"
        "  TÉ  = alap({ate}) + er({er}) + üe({ue}) + gy({gy}) + köt_hm({khte}×{szint}) + szabad_hm({hfte}) = {te}\n"
        "  VÉ  = alap({ave}) + üe({ue}) + gy({gy}) + köt_hm({khve}×{szint}) + szabad_hm({hfve}) = {ve}\n"
        "  ─── Pont értékek ───\n"
        "  ÉP  = alap({aep}) + eg({eg}) = {ep}\n"
        "  FP  = alap({afp}) + {szint}×dobás({fpf}) = {fp}  [dobások: {rolls}]\n"
        "  KP  = alap({akp}) + int({int_b}) + üe({ue}) + {kps}×{szint} = {kp}\n"
        "  HM  = {hm_per}/szint × {szint} szint = {hm_ossz} (kötelező te={khte} ve={khve} | szabad={shm})\n"
        "╚══════════════════════════════════════╝",
        kaszt=kaszt,
        szint=szint,
        props=prop_line,
        gy=gy, ue=ue, er=er, eg=eg, int_b=int_b,
        ke_b=ke_bonus_str,
        ake=r.get("alap_ke"), ke=r.get("ke"),
        ate=r.get("alap_te"), te=r.get("te"),
        ave=r.get("alap_ve"), ve=r.get("ve"),
        aep=d.get("alap_ep","?"), ep=r.get("ep"),
        afp=d.get("alap_fp","?"), fpf=r.get("fp_formula_str"), fp=r.get("fp"), rolls=r.get("fp_rolls"),
        akp=r.get("alap_kp"), kps=r.get("alap_kp_per_szint"), kp=r.get("kp"),
        khte=r.get("kotelezo_hm_te"), khve=r.get("kotelezo_hm_ve"),
        hfte=r.get("hm_free_te"), hfve=r.get("hm_free_ve"),
        hm_per=d.get("hm_per_szint","?"), hm_ossz=r.get("szabad_hm_ossz"),
        shm=r.get("szabad_hm_per_szint"),
    )
