"""
Gera as figuras estáticas (PDF) do relatório e um arquivo com as estatísticas
citadas no texto. Uso:  python figuras.py
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

import nucleo as nc

AQUI = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(AQUI, "relatorio", "figuras")
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.titlesize": 9,
    "axes.edgecolor": nc.EIXO, "axes.labelcolor": nc.TINTA_2, "xtick.color": nc.MUDO,
    "ytick.color": nc.MUDO, "axes.grid": True, "grid.color": nc.GRADE, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "figure.dpi": 150, "savefig.bbox": "tight", "lines.linewidth": 1.6,
})
DIV = LinearSegmentedColormap.from_list("div", [(p, c) for p, c in nc.DIVERGENTE])
SEQ = LinearSegmentedColormap.from_list("seq", nc.SEQUENCIAL)
COL1 = 3.5   # largura de 1 coluna IEEE (pol.)
COL2 = 7.16  # largura de 2 colunas


def turnos(ax):
    for d, r in [(nc.PRIMEIRO_TURNO, "1º turno"), (nc.SEGUNDO_TURNO, "2º turno")]:
        ax.axvline(d, color=nc.EIXO, lw=0.8, zorder=0)
        ax.text(d, 1.0, " " + r, transform=ax.get_xaxis_transform(), va="top", fontsize=7, color=nc.MUDO)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 4, 8, 12, 16, 20, 25, 30]))
    ax.set_xlim(pd.Timestamp("2026-09-30 12:00"), pd.Timestamp("2026-10-30 12:00"))


def salvar(fig, nome):
    fig.savefig(os.path.join(OUT, nome))
    plt.close(fig)
    print("  ", nome)


def main():
    B = nc.carregar()
    TOT = B.artigos
    A = nc.filtrar(TOT, excluir_auto=True)
    est: dict = {}

    # ---------- estatísticas gerais ----------
    est["total_bruto"] = int(len(TOT))
    est["automaticas"] = int(TOT["automatico"].sum())
    est["analisados"] = int(len(A))
    est["veiculos"] = int(A["veiculo"].nunique())
    est["idiomas"] = int(A["idioma"].nunique())
    est["pct_internacional"] = round(100 * (A["midia"] == "Internacional").mean(), 1)
    est["tom_medio"] = round(A["tom"].mean(), 2)
    est["tom_midia"] = A.groupby("midia")["tom"].mean().round(2).to_dict()
    est["globo_tom_com_auto"] = round(TOT[TOT.veiculo == "globo.com"]["tom"].mean(), 2)
    est["auto_tom"] = round(TOT[TOT.automatico]["tom"].mean(), 2)
    est["dia_pico"] = str(A.groupby("dia").size().idxmax().date())
    est["n_pico"] = int(A.groupby("dia").size().max())
    est["idiomas_top"] = A["idioma"].value_counts().head(6).to_dict()
    est["fases"] = nc.fases_resumo(A).assign(fase=lambda d: d.fase.astype(str)).to_dict("records")
    r = nc.atores_resumo(B, A)
    est["atores"] = r.assign(ator=r.ator.astype(str)).round(3).to_dict("records")
    rm = nc.atores_resumo(B, A, "midia")
    est["atores_midia"] = rm.assign(ator=rm.ator.astype(str)).round(3).to_dict("records")
    from scipy import stats
    n, i = A[A.midia == "Nacional"]["tom"], A[A.midia == "Internacional"]["tom"]
    u = stats.mannwhitneyu(n, i)
    est["mannwhitney_p"] = float(u.pvalue)
    est["cohen_d"] = round((n.mean() - i.mean()) / np.sqrt((n.var() + i.var()) / 2), 3)

    # ---------- Fig 1: volume diário (com páginas automáticas) ----------
    fig, ax = plt.subplots(figsize=(COL2, 2.2))
    v = TOT.assign(cat=np.where(TOT.automatico, "Páginas automáticas (g1)", TOT.midia))
    piv = v.pivot_table(index="dia", columns="cat", values="id", aggfunc="size", fill_value=0)
    ordem = ["Nacional", "Internacional", "Páginas automáticas (g1)"]
    cores = [nc.COR_MIDIA["Nacional"], nc.COR_MIDIA["Internacional"], "#c3c2b7"]
    base = np.zeros(len(piv))
    for c, cor in zip(ordem, cores):
        ax.bar(piv.index, piv[c], bottom=base, color=cor, width=0.8, label=c, edgecolor=nc.SUPERFICIE, lw=0.4)
        base += piv[c].values
    turnos(ax)
    ax.set_ylabel("Artigos por dia")
    ax.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, 1.18))
    salvar(fig, "fig_volume.pdf")

    # ---------- Fig 2: tom diário nacional × internacional ----------
    t = nc.tom_diario(A)
    fig, ax = plt.subplots(figsize=(COL1, 2.2))
    for m in ["Nacional", "Internacional"]:
        g = t[t.midia == m]
        ax.plot(g.dia, g.tom, color=nc.COR_MIDIA[m], label=m, marker="o", ms=2.5)
        ax.fill_between(g.dia, g.tom - 1.96 * g.ep, g.tom + 1.96 * g.ep, color=nc.COR_MIDIA[m], alpha=0.15, lw=0)
    ax.axhline(0, color=nc.EIXO, lw=0.8)
    turnos(ax)
    ax.xaxis.set_major_locator(mdates.DayLocator(bymonthday=[1, 8, 15, 22, 29]))
    ax.set_ylabel("Tom médio")
    ax.legend(loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.04))
    salvar(fig, "fig_tom_midia.pdf")

    # ---------- Fig 3: visibilidade diária dos atores ----------
    principais = list(nc.COR_ATOR)
    ad = nc.atores_diario(B, A, principais)
    fig, ax = plt.subplots(figsize=(COL2, 2.3))
    for at in principais:
        g = ad[ad.ator == at].sort_values("dia")
        ax.plot(g.dia, g.mencoes, color=nc.cor_ator(at), label=at)
    turnos(ax)
    ax.set_ylabel("Artigos que citam o ator")
    ax.legend(loc="lower center", ncol=4, bbox_to_anchor=(0.5, 1.04))
    salvar(fig, "fig_atores.pdf")

    # ---------- Fig 4: tom por ator × mídia + fonte da detecção ----------
    rm2 = rm[rm.ator.isin(principais)]
    r2 = r[r.ator.isin(principais)].set_index("ator").loc[principais[::-1]]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(COL2, 1.9), sharey=True)
    y = np.arange(len(principais))
    for k, m in enumerate(["Nacional", "Internacional"]):
        g = rm2[rm2.midia == m].set_index("ator").reindex(principais[::-1])
        a1.barh(y + (k - 0.5) * 0.38, g.tom, height=0.36, color=nc.COR_MIDIA[m], label=m)
    a1.axvline(0, color=nc.EIXO, lw=0.8)
    a1.set_yticks(y, principais[::-1])
    a1.set_xlabel("Tom médio")
    a1.legend(loc="upper center", fontsize=7, ncol=2, bbox_to_anchor=(0.5, -0.3))
    a1.set_title("(a) Tom por ator e mídia", loc="left")
    a2.barh(y + 0.19, 100 * r2.via_pessoa, height=0.36, color="#2a78d6", label="V2Persons")
    a2.barh(y - 0.19, 100 * r2.via_url, height=0.36, color="#eb6834", label="URL")
    a2.set_xlabel("% das menções detectadas")
    a2.legend(loc="upper center", fontsize=7, ncol=2, bbox_to_anchor=(0.5, -0.3))
    a2.set_title("(b) Fonte da detecção", loc="left")
    salvar(fig, "fig_atores_tom.pdf")

    # ---------- Fig 5: temas por fase (heatmap) ----------
    tf = nc.temas_por_fase(B, A)
    tf = tf[tf.tema != "ELECTION"]
    piv = tf.pivot_table(index="rotulo", columns="fase", values="pct", fill_value=0, observed=True)
    piv = piv.loc[piv.mean(axis=1).sort_values(ascending=False).index].head(22)
    fig, ax = plt.subplots(figsize=(COL1, 4.4))
    im = ax.imshow(piv.values, cmap=SEQ, aspect="auto")
    ax.set_xticks(range(piv.shape[1]), [str(c).replace(" (", "\n(") for c in piv.columns], fontsize=6)
    ax.set_yticks(range(piv.shape[0]), piv.index, fontsize=7)
    ax.grid(False)
    vmax = piv.values.max()
    for (i_, j_), val in np.ndenumerate(piv.values):
        ax.text(j_, i_, f"{val:.0f}", ha="center", va="center", fontsize=5.5,
                color="white" if val > 0.55 * vmax else nc.TINTA)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.set_label("% dos artigos da fase")
    cb.outline.set_visible(False)
    salvar(fig, "fig_temas_fase.pdf")
    est["temas_fase"] = piv.round(1).to_dict()

    # ---------- Fig 6: tom por tema ----------
    tr = nc.temas_resumo(B, A)
    tr = tr[tr.tema.isin(B.temas_rotulo.tema) & (tr.tema != "ELECTION")].sort_values("tom")
    fig, ax = plt.subplots(figsize=(COL1, 4.6))
    ax.barh(tr.rotulo, tr.tom, color=DIV((tr.tom.clip(-3, 3) + 3) / 6), height=0.7)
    ax.axvline(0, color=nc.EIXO, lw=0.8)
    ax.tick_params(axis="y", labelsize=6.5)
    ax.set_xlabel("Tom médio dos artigos com o tema")
    salvar(fig, "fig_temas_tom.pdf")
    est["temas_tom"] = tr.set_index("rotulo")[["artigos", "tom"]].round(2).to_dict("index")

    # ---------- Fig 7: idiomas ----------
    ir = nc.idiomas_resumo(A, 12).sort_values("tom")
    fig, ax = plt.subplots(figsize=(COL1, 2.6))
    ax.barh(ir.idioma, ir.tom, color=DIV((ir.tom.clip(-3, 3) + 3) / 6), height=0.7)
    for yy, (tom_, n_) in enumerate(zip(ir.tom, ir.artigos)):
        ax.text(min(tom_, 0) - 0.05, yy, f"{n_:,}".replace(",", "."), ha="right", va="center",
                fontsize=6, color=nc.TINTA_2)
    ax.axvline(0, color=nc.EIXO, lw=0.8)
    ax.set_xlim(ir.tom.min() - 1.1, max(0.6, ir.tom.max() + 0.2))
    ax.set_xlabel("Tom médio (rótulo = nº de artigos)")
    salvar(fig, "fig_idiomas.pdf")
    est["idiomas_tom"] = ir.set_index("idioma")[["artigos", "tom"]].round(2).to_dict("index")

    # ---------- estatísticas extras ----------
    u_ = nc.uf_resumo(B, A).sort_values("artigos", ascending=False)
    est["ufs_top"] = u_[["uf", "artigos", "tom", "saldo"]].head(10).round(3).to_dict("records")
    vr = nc.veiculos_resumo(A, 500)
    est["veiculos_tom"] = vr[["veiculo", "artigos", "tom"]].round(2).to_dict("records")
    lp = B.locais_pais[B.locais_pais.id.isin(A.id)]
    est["paises_top"] = lp.pais.value_counts().head(10).astype(int).to_dict()
    ids = lambda n: set(B.atores[B.atores.ator == n].id) & set(A.id)
    T = ids("Donald Trump")
    est["trump_internacional_pct"] = round(100 * A[A.id.isin(T)].midia.eq("Internacional").mean(), 1)
    est["trump_cooc"] = {k: len(T & ids(k)) for k in ["Lula", "Flávio Bolsonaro", "Jair Bolsonaro"]}
    ad["pct"] = ad.mencoes
    est["atores_fase"] = (ad.assign(fase=nc.fase_de(ad.dia).astype(str))
                          .groupby(["fase", "ator"], observed=True).mencoes.sum().unstack().to_dict())
    x = B.atores[B.atores.ator.isin(principais)].merge(A[["id", "tom", "dia"]], on="id")
    x["fase"] = nc.fase_de(x.dia).astype(str)
    est["atores_tom_fase"] = x.groupby(["fase", "ator"], observed=True).tom.mean().round(2).unstack().to_dict()
    G, _ = nc.rede_coocorrencia(B, A, 35, 40)
    import networkx as nx
    est["rede"] = {"nos": G.number_of_nodes(), "arestas": G.number_of_edges(),
                   "grau_top": sorted(dict(G.degree()).items(), key=lambda kv: -kv[1])[:8],
                   "intermediacao_top": sorted(nx.betweenness_centrality(G).items(), key=lambda kv: -kv[1])[:6]}

    with open(os.path.join(OUT, "..", "estatisticas.json"), "w", encoding="utf-8") as f:
        json.dump(est, f, ensure_ascii=False, indent=1, default=str)
    print("OK ->", OUT)


if __name__ == "__main__":
    main()
