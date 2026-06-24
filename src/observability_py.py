import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv(override=True)


def _get_env(name_langsmith, name_legacy=None, default=None):
    """Lee variable de entorno probando LANGSMITH_* primero, luego LANGCHAIN_*."""
    val = os.getenv(name_langsmith)
    if val is None and name_legacy:
        val = os.getenv(name_legacy)
    return val if val else default


def get_langsmith_runs(limit=10):
    """Obtiene las últimas ejecuciones desde LangSmith."""
    api_key = _get_env("LANGSMITH_API_KEY", "LANGCHAIN_API_KEY")
    if not api_key:
        return None

    try:
        from langsmith import Client

        client = Client(
            api_key=api_key,
            api_url=_get_env("LANGSMITH_ENDPOINT", "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        )
        project = _get_env("LANGSMITH_PROJECT", "LANGCHAIN_PROJECT", "ingenieria_soluciones_con_ia")
        runs = list(client.list_runs(project_name=project, execution_order=1, limit=limit))
        return [_format_run(r, client, project) for r in runs]
    except Exception as e:
        return {"error": str(e)}


def _format_run(run, client=None, project=None):
    start = run.start_time if hasattr(run, "start_time") else None
    end = run.end_time if hasattr(run, "end_time") else None
    latency = (end - start).total_seconds() if start and end else None

    total_tokens = getattr(run, "total_tokens", None)
    prompt_tokens = getattr(run, "prompt_tokens", None)
    completion_tokens = getattr(run, "completion_tokens", None)

    if total_tokens is None and client is not None:
        try:
            child_llm = list(client.list_runs(
                project_name=project,
                parent_run_id=run.id,
                run_type="llm",
                limit=50,
            ))
            if child_llm:
                total_tokens = sum(
                    getattr(cr, "total_tokens", 0) or 0 for cr in child_llm
                ) or None
                prompt_tokens = sum(
                    getattr(cr, "prompt_tokens", 0) or 0 for cr in child_llm
                ) or None
                completion_tokens = sum(
                    getattr(cr, "completion_tokens", 0) or 0 for cr in child_llm
                ) or None
        except Exception:
            pass

    return {
        "run_id": str(getattr(run, "id", ""))[:8],
        "name": getattr(run, "name", "unknown"),
        "latency": round(latency, 2) if latency else None,
        "total_tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "error": getattr(run, "error", None),
        "start_time": start.isoformat() if start else None,
    }


def get_dashboard_metrics(limit=20):
    """Calcula métricas agregadas desde LangSmith."""
    runs = get_langsmith_runs(limit=limit)
    if runs is None:
        return {"status": "no_api_key", "mensaje": "LANGCHAIN_API_KEY no configurada"}
    if isinstance(runs, dict) and "error" in runs:
        return {"status": "error", "mensaje": runs["error"]}
    if not runs:
        return {"status": "empty", "mensaje": "No hay ejecuciones recientes"}

    latencies = [r["latency"] for r in runs if r["latency"] is not None]
    total_tokens = sum(r["total_tokens"] for r in runs if r["total_tokens"] is not None)
    prompt_tokens = sum(r["prompt_tokens"] for r in runs if r["prompt_tokens"] is not None)
    completion_tokens = sum(r["completion_tokens"] for r in runs if r["completion_tokens"] is not None)
    errores = sum(1 for r in runs if r["error"])

    return {
        "status": "ok",
        "total_ejecuciones": len(runs),
        "latencia_promedio": round(sum(latencies) / len(latencies), 2) if latencies else 0,
        "latencia_min": round(min(latencies), 2) if latencies else 0,
        "latencia_max": round(max(latencies), 2) if latencies else 0,
        "total_tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "ejecuciones_con_error": errores,
    }


def estimar_ahorro_tokens(metricas):
    """Estima el ahorro de tokens vs un baseline sin herramientas."""
    if metricas.get("status") != "ok":
        return None
    total = metricas["total_tokens"]
    prompt = metricas["prompt_tokens"]
    # Estimacion: sin herramientas, el prompt incluiria todo el catalogo (~2000 tokens extra)
    ahorro_estimado = prompt * 0.15  # ~15% de ahorro por no re-enviar historial completo
    return {
        "ahorro_estimado_tokens": int(ahorro_estimado),
        "ahorro_estimado_porcentaje": 15,
        "total_tokens_ejecutados": total,
    }
