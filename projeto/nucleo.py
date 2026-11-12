"""
Núcleo de dados e agregações — compartilhado pelo dashboard (app.py) e pelo
gerador de figuras do relatório (figuras.py). Só depende de pandas/networkx.
"""
from __future__ import annotations

import itertools
import os
from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd

DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados")

PRIMEIRO_TURNO = pd.Timestamp("2026-10-04")
SEGUNDO_TURNO = pd.Timestamp("2026-10-25")

FASES = {
    "Pré-1º turno": ("2026-10-01", "2026-10-03"),
    "1º turno (4–6/10)": ("2026-10-04", "2026-10-06"),
    "Entre turnos": ("2026-10-07", "2026-10-24"),
    "2º turno (25–26/10)": ("2026-10-25", "2026-10-26"),
    "Pós-eleição": ("2026-10-27", "2026-10-31"),
}

# ---- paleta (validada com o validador de paleta: CVD/contraste) ----
SUPERFICIE = "#fcfcfb"
TINTA = "#0b0b0b"
TINTA_2 = "#52514e"
MUDO = "#898781"
GRADE = "#e1e0d9"
EIXO = "#c3c2b7"

COR_ATOR = {  # cor segue a entidade, nunca o ranking
    "Lula": "#e34948",
    "Flávio Bolsonaro": "#2a78d6",
    "Jair Bolsonaro": "#1baf7a",
    "Donald Trump": "#eda100",
}
COR_MIDIA = {"Nacional": "#2a78d6", "Internacional": "#eb6834"}

# Divergente para tom: laranja (negativo) ↔ cinza neutro ↔ azul-petróleo (positivo)
DIVERGENTE = [
    [0.0, "#9a3a12"], [0.2, "#eb6834"], [0.4, "#f5c2aa"], [0.5, "#f0efec"],
    [0.6, "#a9d9e0"], [0.8, "#2b8ea0"], [1.0, "#135d6c"],
]
# Sequencial (azul, claro → escuro)
SEQUENCIAL = ["#f0f6fd", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]


def cor_ator(ator: str) -> str:
    return COR_ATOR.get(ator, MUDO)


@dataclass
class Base:
    artigos: pd.DataFrame
    atores: pd.DataFrame
    pessoas: pd.DataFrame
    orgs: pd.DataFrame
    temas: pd.DataFrame
    temas_rotulo: pd.DataFrame
    locais_uf: pd.DataFrame
    locais_pais: pd.DataFrame
    ufs: pd.DataFrame


def carregar(pasta: str = DADOS) -> Base:
    ler = lambda n: pd.read_parquet(os.path.join(pasta, f"{n}.parquet"))
    return Base(*(ler(n) for n in ["artigos", "atores", "pessoas", "orgs", "temas",
                                    "temas_rotulo", "locais_uf", "locais_pais", "ufs"]))


def fase_de(dia: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=dia.index, dtype="object")
    for nome, (ini, fim) in FASES.items():
        out[(dia >= ini) & (dia <= fim)] = nome
    return pd.Categorical(out, categories=list(FASES), ordered=True)


def filtrar(art: pd.DataFrame, ini=None, fim=None, midias=None, idiomas=None,
            veiculos=None, excluir_auto=True) -> pd.DataFrame:
    m = pd.Series(True, index=art.index)
    if ini is not None:
        m &= art["dia"] >= pd.Timestamp(ini)
    if fim is not None:
        m &= art["dia"] <= pd.Timestamp(fim)
    if midias:
        m &= art["midia"].isin(midias)
    if idiomas:
        m &= art["idioma"].isin(idiomas)
    if veiculos:
        m &= art["veiculo"].isin(veiculos)
    if excluir_auto:
        m &= ~art["automatico"]
    return art[m]


# ------------------------------------------------------------------ agregações

def volume_diario(art: pd.DataFrame, por: str = "midia") -> pd.DataFrame:
    return art.groupby(["dia", por]).size().rename("artigos").reset_index()


def tom_diario(art: pd.DataFrame, por: str = "midia") -> pd.DataFrame:
    g = art.groupby(["dia", por])["tom"]
    return pd.DataFrame({"tom": g.mean(), "n": g.size(),
                         "ep": g.std() / np.sqrt(g.size())}).reset_index()


def atores_diario(base: Base, art: pd.DataFrame, atores: list[str]) -> pd.DataFrame:
    x = base.atores[base.atores["ator"].isin(atores)].merge(art[["id", "dia", "tom"]], on="id")
    g = x.groupby(["dia", "ator"], observed=True)
    return g.agg(mencoes=("id", "size"), tom=("tom", "mean")).reset_index()


def atores_resumo(base: Base, art: pd.DataFrame, por: str | None = None) -> pd.DataFrame:
    x = base.atores.merge(art[["id", "tom", "midia", "dia"]], on="id")
    chaves = ["ator"] + ([por] if por else [])
    r = x.groupby(chaves, observed=True).agg(
        mencoes=("id", "size"), tom=("tom", "mean"),
        via_pessoa=("via_pessoa", "mean"), via_url=("via_url", "mean")).reset_index()
    return r.sort_values("mencoes", ascending=False)


def temas_por_dia(base: Base, art: pd.DataFrame, temas: list[str] | None = None,
                  rotular=True) -> pd.DataFrame:
    """% dos artigos de cada dia que contêm o tema."""
    t = base.temas
    if temas is None:
        t = t[t["tema"].isin(base.temas_rotulo["tema"])]
    else:
        t = t[t["tema"].isin(temas)]
    x = t.merge(art[["id", "dia"]], on="id")
    cont = x.groupby(["tema", "dia"], observed=True).size().rename("n").reset_index()
    tot = art.groupby("dia").size().rename("total")
    cont = cont.merge(tot, left_on="dia", right_index=True)
    cont["pct"] = 100 * cont["n"] / cont["total"]
    if rotular:
        rot = dict(zip(base.temas_rotulo["tema"], base.temas_rotulo["rotulo"]))
        cont["rotulo"] = cont["tema"].astype(str).map(lambda s: rot.get(s, s))
    return cont


def temas_resumo(base: Base, art: pd.DataFrame, top: int | None = None) -> pd.DataFrame:
    x = base.temas.merge(art[["id", "tom"]], on="id")
    r = x.groupby("tema", observed=True).agg(artigos=("id", "size"), tom=("tom", "mean")).reset_index()
    r["pct"] = 100 * r["artigos"] / max(len(art), 1)
    rot = dict(zip(base.temas_rotulo["tema"], base.temas_rotulo["rotulo"]))
    r["rotulo"] = r["tema"].astype(str).map(lambda s: rot.get(s, s))
    r = r.sort_values("artigos", ascending=False)
    return r.head(top) if top else r


def temas_por_fase(base: Base, art: pd.DataFrame) -> pd.DataFrame:
    a = art[["id", "dia"]].copy()
    a["fase"] = fase_de(a["dia"])
    t = base.temas[base.temas["tema"].isin(base.temas_rotulo["tema"])].merge(a, on="id")
    cont = t.groupby(["tema", "fase"], observed=True).size().rename("n").reset_index()
    tot = a.groupby("fase", observed=True).size().rename("total")
    cont = cont.merge(tot, left_on="fase", right_index=True)
    cont["pct"] = 100 * cont["n"] / cont["total"]
    rot = dict(zip(base.temas_rotulo["tema"], base.temas_rotulo["rotulo"]))
    cont["rotulo"] = cont["tema"].astype(str).map(rot)
    return cont


def uf_resumo(base: Base, art: pd.DataFrame) -> pd.DataFrame:
    x = base.locais_uf.merge(art[["id", "tom"]], on="id")
    r = x.groupby("uf", observed=True).agg(artigos=("id", "size"), tom=("tom", "mean")).reset_index()
    # saldo de menções Lula × Flávio entre os artigos que citam a UF
    at = base.atores[base.atores["ator"].isin(["Lula", "Flávio Bolsonaro"])]
    y = x.merge(at[["id", "ator"]], on="id")
    c = y.pivot_table(index="uf", columns="ator", values="id", aggfunc="size",
                      observed=True, fill_value=0)
    for col in ["Lula", "Flávio Bolsonaro"]:
        if col not in c:
            c[col] = 0
    c["saldo"] = (c["Lula"] - c["Flávio Bolsonaro"]) / (c["Lula"] + c["Flávio Bolsonaro"]).replace(0, np.nan)
    r = r.merge(c[["Lula", "Flávio Bolsonaro", "saldo"]].reset_index(), on="uf", how="left")
    r["uf"] = r["uf"].astype(str)
    return r.merge(base.ufs, on="uf", how="left")


def idiomas_resumo(art: pd.DataFrame, top: int = 12) -> pd.DataFrame:
    r = art.groupby("idioma").agg(artigos=("id", "size"), tom=("tom", "mean")).reset_index()
    return r.sort_values("artigos", ascending=False).head(top)


def veiculos_resumo(art: pd.DataFrame, minimo: int = 300) -> pd.DataFrame:
    r = art.groupby(["veiculo", "midia"]).agg(
        artigos=("id", "size"), tom=("tom", "mean"), negativo=("negativo", "mean"),
        positivo=("positivo", "mean")).reset_index()
    return r[r["artigos"] >= minimo].sort_values("tom")


def rede_coocorrencia(base: Base, art: pd.DataFrame, n_nos: int = 30, min_peso: int = 20,
                      tabela: str = "pessoas"):
    """Grafo de coocorrência (mesmo artigo) entre as n entidades mais citadas."""
    import networkx as nx

    tab = base.pessoas if tabela == "pessoas" else base.orgs
    col = "pessoa" if tabela == "pessoas" else "org"
    t = tab[tab["id"].isin(art["id"])]
    topo = t[col].value_counts().head(n_nos)
    t = t[t[col].isin(topo.index)]
    tom = t.merge(art[["id", "tom"]], on="id").groupby(col, observed=True)["tom"].mean()
    arestas = Counter()
    for _, grupo in t.groupby("id")[col]:
        nomes = sorted(set(map(str, grupo)))
        arestas.update(itertools.combinations(nomes, 2))
    G = nx.Graph()
    for nome, freq in topo.items():
        G.add_node(str(nome), freq=int(freq), tom=float(tom.get(nome, 0.0)))
    for (u, v), w in arestas.items():
        if w >= min_peso:
            G.add_edge(u, v, peso=w, w_layout=float(np.log1p(w)))
    if G.number_of_edges():
        # mantém só o maior componente conexo (remove pares isolados/ruído de NER)
        G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
    else:
        G = nx.Graph()
    if len(G):
        pos = nx.spring_layout(G, weight="w_layout", seed=7, k=2.5 / np.sqrt(len(G)), iterations=300)
        comunidades = nx.algorithms.community.greedy_modularity_communities(G, weight="peso")
        for i, com in enumerate(comunidades):
            for n in com:
                G.nodes[n]["comunidade"] = i
    else:
        pos = {}
    return G, pos


def fases_resumo(art: pd.DataFrame) -> pd.DataFrame:
    a = art.copy()
    a["fase"] = fase_de(a["dia"])
    return a.groupby(["fase", "midia"], observed=True)["tom"].agg(["size", "mean"]).reset_index()
