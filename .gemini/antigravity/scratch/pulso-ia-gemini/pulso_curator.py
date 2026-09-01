#!/usr/bin/env python3
"""
PULSO a la IA — Curador de noticias
EMPRENDEDORES.LTD

Pipeline: RSS feeds → Codex CLI (OpenAI, clasifica) → borrador .docx → formateador pulso_publisher.py → disco externo + notificación por email
"""

import sys, json, yaml, hashlib, smtplib, logging, subprocess, re, shutil, urllib.request, urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import feedparser
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

# ── Paths relativos al script ──────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent
CONFIG     = BASE_DIR / "config.yaml"
CACHE_FILE = BASE_DIR / "cache" / "seen_articles.json"
LOG_FILE   = BASE_DIR / "logs" / "pulso.log"
OUTPUT_DIR = BASE_DIR / "output"

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

# Detecta fugas multilingües del modelo (chino, japonés, coreano, cirílico, árabe)
# que no deberían aparecer en un borrador redactado en español.
NON_LATIN_RE = re.compile(r"[一-鿿぀-ヿ가-힯Ѐ-ӿ؀-ۿ]")


def load_config():
    with open(CONFIG) as f:
        return yaml.safe_load(f)


def load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text())
    return {}


def save_cache(cache):
    CACHE_FILE.write_text(json.dumps(cache, indent=2))


def article_id(url):
    return hashlib.md5(url.encode()).hexdigest()


def fetch_feeds(cfg, cache):
    """Descarga y filtra artículos nuevos de todos los feeds."""
    lookback = datetime.now() - timedelta(days=cfg.get("lookback_days", 7))
    articles = []
    boost  = [k.lower() for k in cfg.get("boost_keywords", [])]
    suppress = [k.lower() for k in cfg.get("suppress_keywords", [])]

    for feed_cfg in cfg["feeds"]:
        url = feed_cfg["url"]
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                aid = article_id(entry.get("link", entry.get("title", "")))
                if aid in cache:
                    continue
                # Filtro de fecha
                pub = entry.get("published_parsed")
                if pub:
                    pub_dt = datetime(*pub[:6])
                    if pub_dt < lookback:
                        continue
                title   = entry.get("title", "")
                summary = entry.get("summary", entry.get("description", ""))
                text    = (title + " " + summary).lower()
                # Boost / suppress
                score = feed_cfg.get("priority", 2)
                for k in boost:
                    if k in text:
                        score = max(1, score - 1)
                for k in suppress:
                    if k in text:
                        score = 99  # efectivamente excluye
                if score == 99:
                    continue
                articles.append({
                    "id":       aid,
                    "title":    title,
                    "summary":  summary[:600],
                    "url":      entry.get("link", ""),
                    "source":   feed_cfg["name"],
                    "category": feed_cfg.get("category", "tech"),
                    "score":    score,
                })
        except Exception as e:
            log.warning(f"Error en feed {url}: {e}")

    articles.sort(key=lambda x: x["score"])
    return articles[:cfg.get("max_articles", 60)]


def generate_with_codex(articles, cfg, edition_num):
    """Codex CLI (OpenAI) clasifica y redacta el borrador editorial."""
    codex_cfg  = cfg.get("codex", {})
    codex_bin  = codex_cfg.get("binary", "codex")
    model_name = codex_cfg.get("model") or "(login por defecto)"
    timeout    = codex_cfg.get("timeout", 600)

    articles_text = "\n\n".join([
        f"[{i+1}] FUENTE: {a['source']} | CATEGORÍA: {a['category']}\n"
        f"TÍTULO: {a['title']}\nRESUMEN: {a['summary']}\nURL: {a['url']}"
        for i, a in enumerate(articles[:40])
    ])

    today = datetime.now().strftime("%d de %B de %Y")

    prompt = f"""Eres el editor de "PULSO a la IA", publicación semanal de EMPRENDEDORES.LTD para ejecutivos del sector bancario, comercial y agroindustrial en Ecuador y Latinoamérica.

Edición #{edition_num} — {today}

ARTÍCULOS DISPONIBLES:
{articles_text}

Tu tarea: Selecciona los artículos MÁS RELEVANTES para ejecutivos latinoamericanos y redacta el borrador completo de PULSO a la IA en español.

ESTRUCTURA OBLIGATORIA (respeta exactamente estos marcadores):

===RESUMEN_EJECUTIVO===
[Exactamente 2 párrafos bien estructurados (un total de 130-155 palabras para todo el resumen ejecutivo). Debe contener la tesis editorial de la semana y el impacto en banca, comercio o agroindustria en LATAM, redactado con estilo formal de nivel ejecutivo. Aporta profundidad para llenar la página de forma equilibrada.]

===NOTICIAS_DESTACADAS===
---NOTICIA_1---
TÍTULO: [título conciso]
QUÉ PASÓ: [1-2 oraciones]
POR QUÉ IMPORTA: [1-2 oraciones]
TE AFECTA: [impacto concreto para ejecutivo latinoamericano]
RECOMENDACIÓN: [acción concreta]
URL: [url fuente]
---NOTICIA_2---
[igual estructura]
---NOTICIA_3---
[igual estructura]

===MODELOS_DESTACADOS===
---MODELO_1---
TÍTULO: [nombre del modelo/herramienta]
DESCRIPCIÓN: [2-3 oraciones]
RECOMENDACIÓN: [para qué usarlo]
---MODELO_2---
[igual]

===TENDENCIAS_MERCADO===
---TENDENCIA_1---
TÍTULO: [título]
ANÁLISIS: [2-3 oraciones de análisis ejecutivo]
---TENDENCIA_2---
[igual]

===VEREDICTO_ACCIONABLE===
1. [Acción concreta 1 — máx 2 oraciones]
2. [Acción concreta 2]
3. [Acción concreta 3]
4. [Acción concreta 4]
5. [Acción concreta 5]

===HASHTAGS_DINAMICOS===
#Tag1  #Tag2  #Tag3  #Tag4  #Tag5  #Tag6
[6 hashtags sin espacios, en CamelCase, relevantes al contenido de esta edición]

===FIN===

CRITERIOS:
- Priorizar noticias sobre banca, fintech, automatización, regulación IA, modelos de lenguaje
- Lenguaje ejecutivo, no técnico
- Perspectiva latinoamericana cuando sea posible
- Máximo 3 noticias, 2 modelos, 2 tendencias
- Los hashtags deben reflejar los temas específicos de esta edición (empresas, eventos, países, tecnologías mencionadas)
- Responde EXCLUSIVAMENTE en español. No uses caracteres de otros alfabetos (chino, cirílico, árabe, coreano, japonés, etc.) bajo ninguna circunstancia, ni siquiera aislados dentro de una palabra.
- No incluyas URLs en las secciones de Modelos ni de Tendencias — el campo URL solo aplica a Noticias Destacadas.
"""

    import time, tempfile
    log.info(f"Clasificando con Codex CLI (modelo: {model_name})...")

    cmd = [codex_bin, "exec", "-s", "read-only", "--skip-git-repo-check", "--color", "never"]
    if codex_cfg.get("model"):
        cmd += ["-m", codex_cfg["model"]]
    if codex_cfg.get("reasoning_effort"):
        cmd += ["-c", f"model_reasoning_effort={codex_cfg['reasoning_effort']}"]

    max_retries = 3
    for attempt in range(max_retries):
        out_file = None
        try:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
                out_file = tf.name
            proc = subprocess.run(
                cmd + ["-o", out_file, prompt],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode != 0:
                raise RuntimeError(
                    f"codex exec devolvió código {proc.returncode}: {(proc.stderr or '')[-500:].strip()}"
                )
            text = Path(out_file).read_text().strip()
            if not text:
                raise ValueError("codex exec no escribió nada en --output-last-message")
            foreign_chars = NON_LATIN_RE.findall(text)
            if foreign_chars:
                raise ValueError(
                    f"Respuesta contiene caracteres no latinos ({''.join(sorted(set(foreign_chars)))}) "
                    f"— probable fuga multilingüe del modelo"
                )
            return text
        except Exception as e:
            log.warning(f"Intento {attempt+1} falló al llamar a Codex CLI: {e}")
            if attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 4
                log.info(f"Reintentando en {sleep_time} segundos...")
                time.sleep(sleep_time)
            else:
                log.error(f"Error definitivo llamando a Codex CLI después de {max_retries} intentos: {e}")
                sys.exit(1)
        finally:
            if out_file:
                Path(out_file).unlink(missing_ok=True)


def parse_draft(draft_text):
    """Parsea el texto del borrador en secciones estructuradas."""
    data = {
        "resumen_ejecutivo": "",
        "noticias": [],
        "modelos": [],
        "tendencias": [],
        "veredicto": []
    }

    def strip_md(text):
        return re.sub(r"\*\*(.+?)\*\*", r"\1", text)

    def extract_block(text, start_marker, end_marker):
        pattern = rf"{re.escape(start_marker)}(.*?){re.escape(end_marker)}"
        m = re.search(pattern, text, re.DOTALL)
        return strip_md(m.group(1).strip()) if m else ""

    def clean(text):
        return re.sub(r"\n*---+\s*$", "", strip_md(text)).strip()

    def extract_fields(chunk, fields):
        result = {}
        for idx, (field, key) in enumerate(fields):
            next_field_names = [f for f, _ in fields[idx+1:]]
            if next_field_names:
                lookahead = "|".join(re.escape(f + ":") for f in next_field_names)
                pattern = rf"{re.escape(field)}:\s*(.+?)(?={lookahead}|$)"
            else:
                pattern = rf"{re.escape(field)}:\s*(.+?)$"
            m = re.search(pattern, chunk, re.DOTALL)
            result[key] = clean(m.group(1)) if m else ""
        return result

    resumen_raw = extract_block(draft_text, "===RESUMEN_EJECUTIVO===", "===NOTICIAS_DESTACADAS===")
    data["resumen_ejecutivo"] = clean(resumen_raw)

    # Noticias
    noticias_block = extract_block(
        draft_text, "===NOTICIAS_DESTACADAS===", "===MODELOS_DESTACADOS==="
    )
    NOTICIA_FIELDS = [
        ("TÍTULO", "titulo"), ("QUÉ PASÓ", "que_paso"), ("POR QUÉ IMPORTA", "por_que_importa"),
        ("TE AFECTA", "te_afecta"), ("RECOMENDACIÓN", "recomendacion"), ("URL", "url")
    ]
    for chunk in re.split(r"---NOTICIA_\d+---", noticias_block):
        chunk = chunk.strip()
        if not chunk:
            continue
        n = extract_fields(chunk, NOTICIA_FIELDS)
        if n.get("titulo"):
            data["noticias"].append(n)

    # Modelos
    modelos_block = extract_block(
        draft_text, "===MODELOS_DESTACADOS===", "===TENDENCIAS_MERCADO==="
    )
    MODELO_FIELDS = [
        ("TÍTULO", "titulo"), ("DESCRIPCIÓN", "descripcion"), ("RECOMENDACIÓN", "recomendacion")
    ]
    for chunk in re.split(r"---MODELO_\d+---", modelos_block):
        chunk = chunk.strip()
        if not chunk:
            continue
        m = extract_fields(chunk, MODELO_FIELDS)
        if m.get("titulo"):
            data["modelos"].append(m)

    # Tendencias
    tendencias_block = extract_block(
        draft_text, "===TENDENCIAS_MERCADO===", "===VEREDICTO_ACCIONABLE==="
    )
    TENDENCIA_FIELDS = [("TÍTULO", "titulo"), ("ANÁLISIS", "analisis")]
    for chunk in re.split(r"---TENDENCIA_\d+---", tendencias_block):
        chunk = chunk.strip()
        if not chunk:
            continue
        t = extract_fields(chunk, TENDENCIA_FIELDS)
        if t.get("titulo"):
            data["tendencias"].append(t)

    # Veredicto
    veredicto_block = extract_block(
        draft_text, "===VEREDICTO_ACCIONABLE===", "===HASHTAGS_DINAMICOS==="
    )
    if not veredicto_block:
        veredicto_block = extract_block(draft_text, "===VEREDICTO_ACCIONABLE===", "===FIN===")
    for line in veredicto_block.strip().splitlines():
        m = re.match(r"^\d+\.\s+(.+)", line.strip())
        if m:
            data["veredicto"].append(m.group(1).strip())

    # Hashtags dinámicos
    hashtags_block = extract_block(draft_text, "===HASHTAGS_DINAMICOS===", "===FIN===")
    data["hashtags_dinamicos"] = re.findall(r"#\w+", hashtags_block)

    return data


def generate_draft_docx(data, edition_num, output_path):
    """Genera .docx borrador simple (será formateado por el publisher)."""
    doc = Document()
    today = datetime.now().strftime("%d de %B de %Y")

    # Título
    t = doc.add_heading(f"PULSO a la IA — Edición {edition_num}", 0)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Fecha: {today}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")

    # Resumen ejecutivo
    doc.add_heading("Resumen Ejecutivo", 1)
    doc.add_paragraph(data["resumen_ejecutivo"])
    doc.add_paragraph("")

    # Noticias
    doc.add_heading("1. Noticias Destacadas", 1)
    for i, n in enumerate(data["noticias"], 1):
        doc.add_heading(f"1.{i}  {n.get('titulo','')}", 2)
        if n.get("que_paso"):
            p = doc.add_paragraph()
            p.add_run("Qué pasó: ").bold = True
            p.add_run(n["que_paso"])
        if n.get("por_que_importa"):
            p = doc.add_paragraph()
            p.add_run("Por qué importa: ").bold = True
            p.add_run(n["por_que_importa"])
        if n.get("te_afecta"):
            p = doc.add_paragraph()
            p.add_run("Te afecta: ").bold = True
            p.add_run(n["te_afecta"])
        if n.get("recomendacion"):
            p = doc.add_paragraph()
            p.add_run("Recomendación: ").bold = True
            p.add_run(n["recomendacion"])
        doc.add_paragraph("")

    # Modelos
    if data["modelos"]:
        doc.add_heading("2. Modelos Destacados", 1)
        for i, m in enumerate(data["modelos"], 1):
            doc.add_heading(f"2.{i}  {m.get('titulo','')}", 2)
            if m.get("descripcion"):
                doc.add_paragraph(m["descripcion"])
            if m.get("recomendacion"):
                p = doc.add_paragraph()
                p.add_run("Recomendación: ").bold = True
                p.add_run(m["recomendacion"])
            doc.add_paragraph("")

    # Tendencias
    if data["tendencias"]:
        doc.add_heading("3. Tendencias del Mercado", 1)
        for i, t in enumerate(data["tendencias"], 1):
            doc.add_heading(f"3.{i}  {t.get('titulo','')}", 2)
            doc.add_paragraph(t.get("analisis", t.get("analsis", "")))
            doc.add_paragraph("")

    # Veredicto
    if data["veredicto"]:
        doc.add_heading("Veredicto Accionable", 1)
        for item in data["veredicto"]:
            doc.add_paragraph(item, style="List Number")
        doc.add_paragraph("")

    # Link suscripción
    doc.add_paragraph("")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("📩 Suscríbete a PULSO a la IA: ").bold = True
    p.add_run("https://emprendedores.ec/suscripcion")

    doc.save(output_path)
    # Guardar también como JSON para el publisher Node.js
    json_path = str(output_path).replace('.docx', '_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"Borrador guardado: {output_path}")


def run_publisher(draft_path, edition_num, cfg):
    """Ejecuta el formateador Python (pulso_publisher.py) con layout de producción."""
    publisher_script = BASE_DIR / "pulso_publisher.py"
    output_path = OUTPUT_DIR / f"PULSO_a_la_IA_Edicion_{edition_num}.docx"
    json_path = str(draft_path).replace('.docx', '_data.json')
    date_str = datetime.now().strftime("%d de %B de %Y")

    if not publisher_script.exists():
        log.warning("pulso_publisher.py no encontrado — se usará el borrador sin formatear")
        return draft_path

    # Inyectar hashtags fijos del config en el JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data['hashtags_fijos'] = cfg.get('hashtags', {}).get('fixed', [])
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.warning(f"No se pudo inyectar hashtags fijos: {e}")

    python_bin = sys.executable
    result = subprocess.run(
        [python_bin, str(publisher_script),
         json_path, str(output_path), str(edition_num), date_str],
        capture_output=True, text=True, cwd=str(BASE_DIR)
    )
    if result.returncode == 0:
        log.info(f"Publisher OK → {output_path}")
        return output_path
    else:
        log.error(f"Publisher error: {result.stderr}")
        return draft_path


def store_document(docx_path, edition_num, cfg):
    """Copia el .docx final al directorio de almacenamiento en el disco externo.

    Si el disco externo no está montado (p.ej. el cron corre sin el disco conectado),
    el documento se queda solo en la copia local de /output y se reporta el fallback
    en la notificación en lugar de fallar todo el pipeline.
    """
    storage_cfg = cfg.get("storage", {})
    external_dir = Path(storage_cfg.get("external_dir", "/Volumes/Externo/PULSO_a_la_IA/documentos"))

    try:
        external_dir.mkdir(parents=True, exist_ok=True)
        dest_path = external_dir / docx_path.name
        shutil.copy2(docx_path, dest_path)
        log.info(f"Documento almacenado en disco externo: {dest_path}")
        return dest_path, True
    except OSError as e:
        log.warning(f"No se pudo almacenar en disco externo ({external_dir}): {e}. "
                    f"Se mantiene solo la copia local en {docx_path}")
        return docx_path, False


def notify_generated(stored_path, edition_num, cfg, dry_run=False, external_ok=True):
    """Envía un email liviano (sin adjunto) informando que el documento fue generado,
    con la ubicación/URL donde quedó almacenado."""
    ec = cfg["email"]
    today = datetime.now().strftime("%d/%m/%Y")
    file_url = stored_path.resolve().as_uri()

    if external_ok:
        ubicacion = f"📁 Ubicación (disco externo): {stored_path}\n🔗 URL: {file_url}"
    else:
        ubicacion = (
            "⚠️ El disco externo no estaba disponible al momento de generar la edición — "
            f"el documento quedó únicamente en almacenamiento local:\n"
            f"📁 Ubicación: {stored_path}\n🔗 URL: {file_url}"
        )

    msg = MIMEMultipart()
    msg["From"]    = ec["from"]
    msg["To"]      = ec["to"]
    msg["Subject"] = f"✅ PULSO a la IA — Edición {edition_num} generada ({today})"

    body = f"""Hola Ricardo,

La Edición {edition_num} de PULSO a la IA fue generada y almacenada con éxito.

{ubicacion}

—
Sistema automatizado PULSO a la IA
"""
    msg.attach(MIMEText(body, "plain", "utf-8"))

    if dry_run:
        log.info(f"[DRY-RUN] Notificación preparada para {ec['to']} — no se envía")
        return

    port = int(ec.get("smtp_port", 587))
    if port == 465:
        log.info(f"Conectando a {ec['smtp_host']}:{port} usando SSL...")
        server = smtplib.SMTP_SSL(ec["smtp_host"], port)
    else:
        log.info(f"Conectando a {ec['smtp_host']}:{port} usando TLS...")
        server = smtplib.SMTP(ec["smtp_host"], port)
        server.starttls()

    with server:
        server.login(ec["smtp_user"], ec["smtp_password"].replace(" ", ""))
        server.sendmail(ec["from"], ec["to"], msg.as_string())
    log.info(f"Notificación enviada a {ec['to']}")

    sent_marker = BASE_DIR / "cache" / f"edition_{edition_num}.sent"
    sent_marker.parent.mkdir(parents=True, exist_ok=True)
    sent_marker.write_text(datetime.now().isoformat())


def get_next_edition(cfg, dry_run=False):
    """Determina la edición como la semana del año anterior a la ejecución."""
    import datetime
    # Se calcula como el número de semana ISO de hace 7 días (semana anterior a hoy)
    n = (datetime.date.today() - datetime.timedelta(days=7)).isocalendar()[1]
    
    edition_file = BASE_DIR / "cache" / "edition.txt"
    if not dry_run:
        edition_file.parent.mkdir(parents=True, exist_ok=True)
        edition_file.write_text(str(n))
    return n



def main():
    # ── Argumentos especiales para integraciones de API ──
    if "--send-only" in sys.argv:
        # Uso: pulso_curator.py --send-only <docx_path> <edition_num>
        try:
            idx = sys.argv.index("--send-only")
            docx_path = Path(sys.argv[idx+1])
            edition_num = int(sys.argv[idx+2])
            cfg = load_config()
            log.info(f"Almacenando y notificando edición {edition_num} con {docx_path}...")
            stored_path, external_ok = store_document(docx_path, edition_num, cfg)
            notify_generated(stored_path, edition_num, cfg, dry_run=False, external_ok=external_ok)
            sys.exit(0)
        except Exception as e:
            log.error(f"Error en --send-only: {e}")
            sys.exit(1)

    dry_run = "--dry-run" in sys.argv
    curate_only = "--curate-only" in sys.argv

    if dry_run:
        log.info("=== MODO DRY-RUN (sin email, sin actualizar contador) ===")
    elif curate_only:
        log.info("=== MODO CURATE-ONLY (curación y generación de borrador JSON, sin enviar) ===")

    cfg = load_config()
    cache = load_cache()

    # 1. Fetch feeds
    log.info("Descargando feeds RSS...")
    articles = fetch_feeds(cfg, cache)
    log.info(f"  {len(articles)} artículos nuevos encontrados")

    if not articles:
        log.info("Sin artículos nuevos. Abortando.")
        return

    # 2. Generar con Codex CLI (OpenAI)
    edition_num = get_next_edition(cfg, dry_run=dry_run)
    draft_text  = generate_with_codex(articles, cfg, edition_num)

    # 3. Parsear borrador
    data = parse_draft(draft_text)
    log.info(f"  {len(data['noticias'])} noticias | {len(data['modelos'])} modelos | {len(data['tendencias'])} tendencias")

    # 4. Guardar borrador .docx simple
    draft_path = OUTPUT_DIR / f"borrador_edicion_{edition_num}.docx"
    generate_draft_docx(data, edition_num, draft_path)

    # Si es curate-only, salimos aquí (guardando cache de artículos procesados)
    if curate_only:
        for a in articles:
            cache[a["id"]] = datetime.now().isoformat()
        save_cache(cache)
        log.info(f"=== Curación completada para Edición {edition_num} ===")
        return

    # 5. Ejecutar publisher formateador
    final_path = run_publisher(draft_path, edition_num, cfg)

    # 6. Almacenar en disco externo y notificar por email (sin adjunto)
    if dry_run:
        log.info("[DRY-RUN] Documento generado localmente — no se almacena en disco externo ni se notifica")
    else:
        stored_path, external_ok = store_document(final_path, edition_num, cfg)
        notify_generated(stored_path, edition_num, cfg, dry_run=dry_run, external_ok=external_ok)

    # 7. Actualizar cache (no en dry-run, para no "quemar" artículos nuevos en una prueba)
    if not dry_run:
        for a in articles:
            cache[a["id"]] = datetime.now().isoformat()
        save_cache(cache)

    log.info(f"=== PULSO Edición {edition_num} completado ===")


if __name__ == "__main__":
    main()
