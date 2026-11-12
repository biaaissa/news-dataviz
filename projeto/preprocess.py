"""
Pré-processamento do recorte GDELT GKG 2.0 — Eleições Brasil 2026 (01–30/10/2026).

Lê o parquet bruto exportado do BigQuery e gera tabelas "longas" e leves em
projeto/dados/, usadas pelo dashboard (app.py) e pelo gerador de figuras.

Uso:
    python preprocess.py [caminho_do_parquet_bruto]
"""
from __future__ import annotations

import glob
import os
import re
import sys
import unicodedata

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "dados")

# --------------------------------------------------------------------------
# Dicionários de apoio
# --------------------------------------------------------------------------

# Códigos FIPS 10-4 (ADM1) usados pelo GDELT para as UFs brasileiras.
UF_FIPS = {
    "BR01": ("AC", "Acre"), "BR02": ("AL", "Alagoas"), "BR03": ("AP", "Amapá"),
    "BR04": ("AM", "Amazonas"), "BR05": ("BA", "Bahia"), "BR06": ("CE", "Ceará"),
    "BR07": ("DF", "Distrito Federal"), "BR08": ("ES", "Espírito Santo"),
    "BR11": ("MS", "Mato Grosso do Sul"), "BR13": ("MA", "Maranhão"),
    "BR14": ("MT", "Mato Grosso"), "BR15": ("MG", "Minas Gerais"),
    "BR16": ("PA", "Pará"), "BR17": ("PB", "Paraíba"), "BR18": ("PR", "Paraná"),
    "BR20": ("PI", "Piauí"), "BR21": ("RJ", "Rio de Janeiro"),
    "BR22": ("RN", "Rio Grande do Norte"), "BR23": ("RS", "Rio Grande do Sul"),
    "BR24": ("RO", "Rondônia"), "BR25": ("RR", "Roraima"),
    "BR26": ("SC", "Santa Catarina"), "BR27": ("SP", "São Paulo"),
    "BR28": ("SE", "Sergipe"), "BR29": ("GO", "Goiás"), "BR30": ("PE", "Pernambuco"),
    "BR31": ("TO", "Tocantins"),
}

# Região de cada UF (para agregações).
REGIAO = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte",
    "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste",
    "PB": "Nordeste", "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste",
    "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste",
    "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

# Centróides geográficos aproximados das UFs (lat, lon).
CENTROIDE = {
    "AC": (-9.0, -70.5), "AL": (-9.6, -36.6), "AP": (1.4, -51.8), "AM": (-4.2, -64.6),
    "BA": (-12.5, -41.7), "CE": (-5.2, -39.5), "DF": (-15.8, -47.9), "ES": (-19.6, -40.6),
    "MS": (-20.5, -54.8), "MA": (-5.1, -45.3), "MT": (-12.9, -55.9), "MG": (-18.5, -44.6),
    "PA": (-3.8, -52.5), "PB": (-7.1, -36.7), "PR": (-24.6, -51.6), "PI": (-7.7, -42.7),
    "RJ": (-22.3, -42.7), "RN": (-5.8, -36.6), "RS": (-29.7, -53.2), "RO": (-10.9, -62.8),
    "RR": (2.0, -61.4), "SC": (-27.3, -50.4), "SP": (-22.3, -48.6), "SE": (-10.6, -37.4),
    "GO": (-15.9, -49.6), "PE": (-8.4, -37.9), "TO": (-10.2, -48.3),
}

IDIOMA = {
    "por": "Português", "spa": "Espanhol", "eng": "Inglês", "deu": "Alemão",
    "ita": "Italiano", "fra": "Francês", "ell": "Grego", "zho": "Chinês",
    "rus": "Russo", "tur": "Turco", "ara": "Árabe", "srp": "Sérvio",
    "fin": "Finlandês", "ron": "Romeno", "kor": "Coreano", "nld": "Holandês",
    "pol": "Polonês", "jpn": "Japonês", "heb": "Hebraico", "ukr": "Ucraniano",
}

# Candidatos / atores centrais. Cada um é detectado por (a) regex sobre o nome
# normalizado em V2Persons e (b) regex sobre o "slug" da URL. A combinação
# corrige a sub-detecção de nomes mononímicos (ex.: "Lula") pelo NER do GDELT.
ATORES = {
    "Lula": (r"\blula\b", r"lula"),
    "Flávio Bolsonaro": (r"\bflavio b\w*", r"flavio"),
    "Jair Bolsonaro": (r"\bjair (?:messias )?bolsonaro\b", r"jair-(?:messias-)?bolsonaro"),
    "Michelle Bolsonaro": (r"\bmichelle bolsonaro\b", r"michelle-bolsonaro"),
    "Tarcísio de Freitas": (r"\btarcisio\b", r"tarcisio"),
    "Ronaldo Caiado": (r"\bcaiado\b", r"caiado"),
    "Romeu Zema": (r"\bzema\b", r"zema"),
    "Renan Santos": (r"\brenan santos\b", r"renan-santos"),
    "Simone Tebet": (r"\btebet\b", r"tebet"),
    "Geraldo Alckmin": (r"\balckmin\b", r"alckmin"),
    "Fernando Haddad": (r"\bhaddad\b", r"haddad"),
    "Donald Trump": (r"\bdonald trump\b", r"trump"),
}

# Normalização de nomes de pessoas (erros de tradução automática do GDELT).
ALIASES = [
    (r"\blula\b", "Lula"),
    (r"\bflavio b\w*", "Flávio Bolsonaro"),
    (r"^(jair renan|renan bolsonaro)", "Jair Renan Bolsonaro"),
    (r"^(andrew|andre) mendonca$", "André Mendonça"),
    (r"^davi(d)? alcolumbre$", "Davi Alcolumbre"),
    (r"^guillaume boulos$", "Guilherme Boulos"),
    (r"^kassio nunes", "Kassio Nunes Marques"),
    (r"^luis da silva$", "Lula"),
    (r"^(fernanda|luiza|fernanda antunes)? ?(antunes )?figueira bolsonaro$", "Fernanda Bolsonaro"),
]

# Entidades extraídas como pessoa que não são pessoas (ou são créditos de foto).
NAO_PESSOA = {
    "America Latin", "Wikimedia Commons", "Adenanthera Pavonina", "Our Lady",
    "El Nino", "El Pais", "Nova Zelandia", "Republica Dominicana", "Santa Barbara",
    "Los Angeles", "Belo Horizonte", "Bolsa Familia", "Nova Iguacu",
    "Calophyllum Longifolium", "Ser Soprado", "Bolsonaro Al", "Julio Caesar",
    # créditos fotográficos frequentes (agências)
    "Marcelo Camargo", "Ricardo Stuckert", "Eraldo Peres", "Andre Penner",
    "Natacha Pisarenko", "Campo Natacha Pisarenko", "Alexandre Schneider Getty",
    "Janeiro Silvia Izquierdo", "Julia Demaree Nikhinson", "Wilson Grassi",
}

# Temas GKG selecionados para análise, com rótulo em português.
TEMAS_ROTULO = {
    "ELECTION": "Eleição",
    "ELECTION_FRAUD": "Fraude eleitoral",
    "CORRUPTION": "Corrupção",
    "DEMOCRACY": "Democracia",
    "TRIAL": "Julgamento",
    "ARREST": "Prisão",
    "EXTREMISM": "Extremismo",
    "PROTEST": "Protesto",
    "ARMEDCONFLICT": "Conflito armado",
    "SOC_GENERALCRIME": "Crime",
    "KILL": "Mortes",
    "EPU_ECONOMY": "Economia",
    "TAX_ECON_PRICE": "Preços",
    "ECON_INFLATION": "Inflação",
    "WB_2670_JOBS": "Emprego",
    "POVERTY": "Pobreza",
    "EDUCATION": "Educação",
    "HEALTH_PANDEMIC": "Saúde/pandemia",
    "MEDIA_MSM": "Imprensa",
    "MEDIA_SOCIAL": "Redes sociais",
    "UNGP_POLITICAL_FREEDOMS": "Liberdades políticas",
    "SECURITY_SERVICES": "Segurança pública",
    "ENV_CLIMATECHANGE": "Mudança climática",
    "UNGP_FORESTS_RIVERS_OCEANS": "Florestas/Amazônia",
    "LEGISLATION": "Legislação",
    "USPEC_UNCERTAINTY1": "Incerteza",
    "TAX_FNCACT_CANDIDATE": "Candidato",
    "TAX_FNCACT_SUPPORTERS": "Apoiadores",
    "SURVEILLANCE": "Vigilância",
    "CYBER_ATTACK": "Ataque cibernético",
}


# --------------------------------------------------------------------------
# Funções auxiliares
# --------------------------------------------------------------------------

def sem_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def nomes_unicos(campo: str | None) -> list[str]:
    """'Nome,offset;Nome,offset' -> nomes únicos, na ordem."""
    if not campo:
        return []
    vistos = dict.fromkeys(x.rsplit(",", 1)[0] for x in campo.split(";") if x)
    return list(vistos)


def normaliza_pessoa(nome: str) -> str | None:
    if nome in NAO_PESSOA:
        return None
    n = sem_acento(nome).lower()
    for pad, canon in ALIASES:
        if re.search(pad, n):
            return canon
    return nome


def idioma_origem(trad: str | None) -> str:
    if not trad:
        return "eng"  # GKG: sem TranslationInfo = coletado em inglês
    m = re.search(r"srclc:(\w+)", trad)
    return m.group(1) if m else "eng"


def main(caminho: str | None = None) -> None:
    if caminho is None:
        cand = sorted(glob.glob(os.path.join(AQUI, "..", "data", "raw", "gkg_*.parquet")))
        if not cand:
            sys.exit("Parquet bruto não encontrado. Informe o caminho como argumento.")
        caminho = cand[-1]  # o mais recente (timestamp no nome)
    os.makedirs(SAIDA, exist_ok=True)
    print("Lendo", caminho)
    df = pd.read_parquet(caminho)
    df = df.drop_duplicates("GKGRECORDID").reset_index(drop=True)
    df["id"] = np.arange(len(df), dtype=np.int32)

    # ---------------- tabela de artigos ----------------
    tom = df["V2Tone"].fillna("").str.split(",", expand=True).iloc[:, :7]
    tom.columns = ["tom", "positivo", "negativo", "polaridade", "atividade", "autorref", "palavras"]
    tom = tom.apply(pd.to_numeric, errors="coerce")

    art = pd.DataFrame({
        "id": df["id"],
        "datahora": df["DataHora"].dt.tz_convert("UTC").dt.tz_localize(None),  # UTC: dias completos
        "veiculo": df["Veiculo"].fillna("(desconhecido)"),
        "url": df["URL"],
    })
    art = pd.concat([art, tom], axis=1)
    art["dia"] = art["datahora"].dt.normalize()
    art["idioma_cod"] = df["TranslationInfo"].map(idioma_origem)
    art["idioma"] = art["idioma_cod"].map(IDIOMA).fillna(art["idioma_cod"])
    art["midia"] = np.where(art["veiculo"].str.endswith(".br") | (art["idioma_cod"] == "por"),
                            "Nacional", "Internacional")
    # Páginas geradas automaticamente pelo g1 com o resultado por município/seção
    # ("resultado-das-eleicoes-2026-em-<cidade>..."): distorcem volume e tom.
    art["automatico"] = art["url"].fillna("").str.contains(
        r"resultado-das-eleicoes-2026|zona-eleitoral|resultado-da-votacao-em|como-foi-a-votacao",
        regex=True)
    # Portugal e outros lusófonos ficam como Nacional se em português; corrige pelos TLDs
    lus = art["veiculo"].str.contains(r"\.(?:pt|ao|mz|cv)$", regex=True)
    art.loc[lus, "midia"] = "Internacional"

    # ---------------- menções a atores (pessoas + URL) ----------------
    pessoas_norm = df["V2Persons"].map(lambda v: {sem_acento(p).lower() for p in nomes_unicos(v)})
    slug = df["URL"].fillna("").str.lower().map(sem_acento)
    linhas_at = []
    for ator, (re_p, re_u) in ATORES.items():
        rp, ru = re.compile(re_p), re.compile(re_u)
        em_p = pessoas_norm.map(lambda s: any(rp.search(x) for x in s))
        em_u = slug.str.contains(ru)
        m = em_p | em_u
        art[f"cita_{ator}"] = m
        sub = pd.DataFrame({"id": df.loc[m, "id"], "ator": ator,
                            "via_pessoa": em_p[m], "via_url": em_u[m]})
        linhas_at.append(sub)
    atores = pd.concat(linhas_at, ignore_index=True)
    atores["ator"] = atores["ator"].astype("category")

    # ---------------- pessoas (normalizadas) ----------------
    reg = []
    for i, v in zip(df["id"], df["V2Persons"]):
        for p in {normaliza_pessoa(n) for n in nomes_unicos(v)}:
            if p:
                reg.append((i, p))
    pessoas = pd.DataFrame(reg, columns=["id", "pessoa"])
    pessoas["pessoa"] = pessoas["pessoa"].astype("category")

    # ---------------- organizações ----------------
    reg = [(i, o) for i, v in zip(df["id"], df["V2Organizations"]) for o in nomes_unicos(v)]
    orgs = pd.DataFrame(reg, columns=["id", "org"])
    orgs["org"] = orgs["org"].astype("category")

    # ---------------- temas ----------------
    reg = [(i, t) for i, v in zip(df["id"], df["V2Themes"]) for t in nomes_unicos(v)]
    temas = pd.DataFrame(reg, columns=["id", "tema"])
    temas["tema"] = temas["tema"].astype("category")

    # ---------------- locais ----------------
    reg_uf, reg_pais = [], []
    for i, v in zip(df["id"], df["V2Locations"]):
        if not v:
            continue
        ufs, paises = set(), set()
        for loc in v.split(";"):
            f = loc.split("#")
            if len(f) < 8:
                continue
            pais, adm1 = f[2], f[3]
            if pais:
                paises.add(pais)
            if pais == "BR" and adm1 in UF_FIPS:
                ufs.add(adm1)
        reg_uf += [(i, u) for u in ufs]
        reg_pais += [(i, p) for p in paises]
    locais_uf = pd.DataFrame(reg_uf, columns=["id", "fips"])
    locais_uf["uf"] = locais_uf["fips"].map(lambda c: UF_FIPS[c][0])
    locais_uf = locais_uf.drop(columns="fips")
    locais_uf["uf"] = locais_uf["uf"].astype("category")
    locais_pais = pd.DataFrame(reg_pais, columns=["id", "pais"])
    locais_pais["pais"] = locais_pais["pais"].astype("category")

    ufs = pd.DataFrame([
        {"uf": sig, "nome": nome, "regiao": REGIAO[sig],
         "lat": CENTROIDE[sig][0], "lon": CENTROIDE[sig][1]}
        for f, (sig, nome) in UF_FIPS.items()
    ])

    temas_rot = pd.DataFrame(list(TEMAS_ROTULO.items()), columns=["tema", "rotulo"])

    # ---------------- gravação ----------------
    for nome, t in [("artigos", art), ("atores", atores), ("pessoas", pessoas),
                    ("orgs", orgs), ("temas", temas), ("locais_uf", locais_uf),
                    ("locais_pais", locais_pais), ("ufs", ufs), ("temas_rotulo", temas_rot)]:
        t.to_parquet(os.path.join(SAIDA, f"{nome}.parquet"), index=False)
        print(f"  {nome:12s} {len(t):>9,d} linhas")
    print("OK ->", SAIDA)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
