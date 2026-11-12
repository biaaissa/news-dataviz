"""
Observatório Visual — Eleições Brasil 2026 na mídia (GDELT GKG 2.0)

Dashboard de exploração visual interativa. Execute com:
    streamlit run app.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import nucleo as nc

st.set_page_config(page_title="Eleições 2026 na mídia — GDELT", page_icon="🗳️", layout="wide")

# ----------------------------------------------------------------- estilo
FONTE = 'system-ui, -apple-system, "Segoe UI", sans-serif'
LAYOUT = dict(
    font=dict(family=FONTE, size=13, color=nc.TINTA_2),
    paper_bgcolor=nc.SUPERFICIE, plot_bgcolor=nc.SUPERFICIE,
    margin=dict(l=10, r=10, t=78, b=10),
    hoverlabel=dict(bgcolor="white", font=dict(family=FONTE, color=nc.TINTA)),
    legend=dict(orientation="h", yanchor="bottom", y=1.03, x=0, title=None),
    xaxis=dict(gridcolor=nc.GRADE, linecolor=nc.EIXO, zeroline=False, tickfont=dict(color=nc.MUDO)),
    yaxis=dict(gridcolor=nc.GRADE, linecolor=nc.EIXO, zeroline=False, tickfont=dict(color=nc.MUDO)),
)
CFG = {"displaylogo": False, "locale": "pt-BR"}


def estilizar(fig: go.Figure, titulo: str | None = None, altura: int = 380) -> go.Figure:
    fig.update_layout(**LAYOUT, height=altura)
    if titulo:
        fig.update_layout(title=dict(text=titulo, font=dict(size=15, color=nc.TINTA), x=0, xanchor="left",
                                     y=1, yref="container", yanchor="top", pad=dict(t=12, l=4)))
    return fig


def marcar_turnos(fig: go.Figure, ini, fim) -> None:
    fig.update_xaxes(tickformat="%d/%m", hoverformat="%d/%m/%Y")
    for d, rot in [(nc.PRIMEIRO_TURNO, "1º turno"), (nc.SEGUNDO_TURNO, "2º turno")]:
        if pd.Timestamp(ini) <= d <= pd.Timestamp(fim):
            fig.add_vline(x=d, line_width=1, line_color=nc.EIXO)
            fig.add_annotation(x=d, y=1, yref="paper", text=rot, showarrow=False,
                               xanchor="left", yanchor="top", xshift=4,
                               font=dict(size=11, color=nc.MUDO))


def rotulo_final(fig: go.Figure, df: pd.DataFrame, x: str, y: str, serie: str) -> None:
    """Rótulo direto no último ponto de cada série (codificação secundária)."""
    for nome, g in df.groupby(serie, observed=True):
        g = g.dropna(subset=[y]).sort_values(x)
        if g.empty:
            continue
        ult = g.iloc[-1]
        fig.add_annotation(x=ult[x], y=ult[y], text=str(nome), showarrow=False, xanchor="left",
                           xshift=6, font=dict(size=11, color=nc.TINTA_2))


# ----------------------------------------------------------------- dados
@st.cache_resource(show_spinner="Carregando dados…")
def base() -> nc.Base:
    return nc.carregar()


B = base()
ART = B.artigos

st.markdown(
    "## Eleições Brasil 2026 na mídia\n"
    "<span style='color:#52514e'>Exploração visual de notícias indexadas pelo GDELT Global "
    "Knowledge Graph (GKG 2.0) — 01 a 30/10/2026 (datas em UTC).</span>",
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------- filtros (uma linha, escopo global)
d_min, d_max = ART["dia"].min().date(), ART["dia"].max().date()
c1, c2, c3, c4, c5 = st.columns([2.2, 1.4, 2, 2.4, 1.2])
with c1:
    periodo = st.slider("Período", min_value=d_min, max_value=d_max, value=(d_min, d_max),
                        format="DD/MM")
with c2:
    midias = st.multiselect("Mídia", ["Nacional", "Internacional"], default=["Nacional", "Internacional"])
with c3:
    idiomas_todos = ART["idioma"].value_counts().index.tolist()
    idiomas = st.multiselect("Idioma de origem", idiomas_todos, placeholder="Todos")
with c4:
    veic_todos = ART["veiculo"].value_counts().index.tolist()
    veiculos = st.multiselect("Veículo", veic_todos, placeholder="Todos")
with c5:
    excluir_auto = st.toggle("Excluir páginas automáticas", value=True,
                             help="Remove ~13 mil páginas geradas automaticamente pelo g1 "
                                  "com resultados por município/seção eleitoral.")

A = nc.filtrar(ART, periodo[0], periodo[1], midias, idiomas, veiculos, excluir_auto)
if A.empty:
    st.warning("Nenhum artigo para os filtros escolhidos.")
    st.stop()

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Artigos", f"{len(A):,}".replace(",", "."))
k2.metric("Veículos", f"{A['veiculo'].nunique():,}".replace(",", "."))
k3.metric("Idiomas de origem", A["idioma"].nunique())
k4.metric("Tom médio", f"{A['tom'].mean():+.2f}".replace(".", ","))
k5.metric("Mídia internacional", f"{100 * (A['midia'] == 'Internacional').mean():.0f}%")

abas = st.tabs(["📈 Linha do tempo", "👥 Candidatos", "🏷️ Temas", "🗺️ Geografia",
                "🕸️ Rede de atores", "📰 Veículos e idiomas", "🔎 Artigos"])

# ================================================================= 1. Linha do tempo
with abas[0]:
    gran = st.radio("Granularidade", ["Diária", "Horária"], horizontal=True)
    if gran == "Horária":
        Ah = A.assign(dia=A["datahora"].dt.floor("h"))
    else:
        Ah = A
    v = nc.volume_diario(Ah)
    fig = go.Figure()
    for m in ["Nacional", "Internacional"]:
        g = v[v["midia"] == m]
        if g.empty:
            continue
        fig.add_bar(x=g["dia"], y=g["artigos"], name=m, marker_color=nc.COR_MIDIA[m],
                    marker_line_width=0,
                    hovertemplate="%{x|%d/%m %Hh}<br>" + m + ": %{y:,} artigos<extra></extra>")
    fig.update_layout(barmode="stack", bargap=0.15)
    marcar_turnos(fig, periodo[0], periodo[1])
    st.plotly_chart(estilizar(fig, "Volume de artigos por " + ("dia" if gran == "Diária" else "hora")),
                    use_container_width=True, config=CFG)

    t = nc.tom_diario(A)
    fig = go.Figure()
    for m in ["Nacional", "Internacional"]:
        g = t[t["midia"] == m]
        if g.empty:
            continue
        fig.add_scatter(x=g["dia"], y=g["tom"], name=m, mode="lines+markers",
                        line=dict(color=nc.COR_MIDIA[m], width=2), marker=dict(size=6),
                        customdata=np.c_[g["n"], g["ep"]],
                        hovertemplate="%{x|%d/%m}<br>" + m + ": tom %{y:.2f} "
                                      "(±%{customdata[1]:.2f})<br>%{customdata[0]:,} artigos<extra></extra>")
    fig.add_hline(y=0, line_width=1, line_color=nc.EIXO)
    marcar_turnos(fig, periodo[0], periodo[1])
    rotulo_final(fig, t, "dia", "tom", "midia")
    fig.update_layout(hovermode="x unified", yaxis_title="Tom médio (GDELT)")
    st.plotly_chart(estilizar(fig, "Tom médio diário — nacional × internacional"),
                    use_container_width=True, config=CFG)
    st.caption("Tom GDELT = % palavras positivas − % palavras negativas (escala aprox. −10 a +10). "
               "Barras de erro omitidas; o erro-padrão aparece no tooltip.")

    f = nc.fases_resumo(A)
    st.dataframe(f.rename(columns={"fase": "Fase", "midia": "Mídia", "size": "Artigos", "mean": "Tom médio"})
                 .style.format({"Tom médio": "{:+.2f}"}), hide_index=True, use_container_width=True)

# ================================================================= 2. Candidatos
with abas[1]:
    todos_atores = list(nc.COR_ATOR) + [a for a in B.atores["ator"].cat.categories if a not in nc.COR_ATOR]
    sel = st.multiselect("Atores", todos_atores, default=list(nc.COR_ATOR),
                         help="Menção = nome em V2Persons (variantes normalizadas) OU no endereço (URL) do artigo. "
                              "Os 4 atores principais têm cor fixa; os demais aparecem em cinza.")
    metrica = st.radio("Métrica", ["Menções absolutas", "Participação (% dos artigos do dia)"], horizontal=True)
    if sel:
        ad = nc.atores_diario(B, A, sel)
        tot = A.groupby("dia").size().rename("total")
        ad = ad.merge(tot, left_on="dia", right_index=True)
        ad["pct"] = 100 * ad["mencoes"] / ad["total"]
        ycol = "mencoes" if metrica.startswith("Menções") else "pct"
        fig = go.Figure()
        for ator in sel:
            g = ad[ad["ator"] == ator]
            fig.add_scatter(x=g["dia"], y=g[ycol], name=ator, mode="lines",
                            line=dict(color=nc.cor_ator(ator), width=2),
                            hovertemplate=ator + ": %{y:,.1f}<extra></extra>")
        marcar_turnos(fig, periodo[0], periodo[1])
        rotulo_final(fig, ad, "dia", ycol, "ator")
        fig.update_layout(hovermode="x unified", yaxis_title="Menções" if ycol == "mencoes" else "% dos artigos")
        st.plotly_chart(estilizar(fig, "Visibilidade diária dos atores"), use_container_width=True, config=CFG)

        janela = st.slider("Média móvel do tom (dias)", 1, 7, 3)
        fig = go.Figure()
        for ator in sel:
            g = ad[ad["ator"] == ator].sort_values("dia")
            fig.add_scatter(x=g["dia"], y=g["tom"].rolling(janela, min_periods=1).mean(), name=ator,
                            mode="lines", line=dict(color=nc.cor_ator(ator), width=2),
                            hovertemplate=ator + ": %{y:.2f}<extra></extra>")
        fig.add_hline(y=0, line_width=1, line_color=nc.EIXO)
        marcar_turnos(fig, periodo[0], periodo[1])
        fig.update_layout(hovermode="x unified", yaxis_title="Tom médio")
        st.plotly_chart(estilizar(fig, f"Tom médio dos artigos que citam cada ator (média móvel de {janela} d)"),
                        use_container_width=True, config=CFG)

        col_a, col_b = st.columns(2)
        r = nc.atores_resumo(B, A, por="midia")
        r = r[r["ator"].isin(sel)]
        with col_a:
            fig = go.Figure()
            for m in ["Nacional", "Internacional"]:
                g = r[r["midia"] == m]
                fig.add_bar(y=g["ator"].astype(str), x=g["tom"], name=m, orientation="h",
                            marker_color=nc.COR_MIDIA[m], customdata=g["mencoes"],
                            hovertemplate="%{y} — " + m + "<br>tom %{x:.2f} · %{customdata:,} artigos<extra></extra>")
            fig.update_layout(barmode="group", bargap=0.3, bargroupgap=0.1,
                              yaxis=dict(categoryorder="array", categoryarray=sel[::-1]),
                              xaxis_title="Tom médio")
            st.plotly_chart(estilizar(fig, "Tom por ator e tipo de mídia", 420), use_container_width=True, config=CFG)
        with col_b:
            rr = nc.atores_resumo(B, A)
            rr = rr[rr["ator"].isin(sel)]
            fig = go.Figure()
            fig.add_bar(y=rr["ator"].astype(str), x=100 * rr["via_pessoa"], name="Detectado em V2Persons",
                        orientation="h", marker_color="#2a78d6")
            fig.add_bar(y=rr["ator"].astype(str), x=100 * rr["via_url"], name="Detectado na URL",
                        orientation="h", marker_color="#eb6834")
            fig.update_layout(barmode="group", bargap=0.3, xaxis_title="% das menções",
                              yaxis=dict(categoryorder="array", categoryarray=sel[::-1]))
            st.plotly_chart(estilizar(fig, "Fonte da detecção (qualidade do NER)", 420),
                            use_container_width=True, config=CFG)
        st.caption("Ex.: o NER do GDELT reconhece pouco o mononímico “Lula” — a maioria das menções a ele "
                   "só é recuperada pela URL. Comparações de volume entre atores devem considerar esse viés.")

# ================================================================= 3. Temas
with abas[2]:
    st.markdown("**Agenda temática** — % dos artigos do dia classificados em cada tema do GKG.")
    modo = st.radio("Conjunto de temas", ["Selecionados (rótulos PT)", "Escolher códigos GKG"], horizontal=True)
    if modo.startswith("Escolher"):
        top = nc.temas_resumo(B, A, 400)
        temas = st.multiselect("Temas GKG", top["tema"].astype(str).tolist(),
                               default=top["tema"].astype(str).tolist()[1:13])
        td = nc.temas_por_dia(B, A, temas)
    else:
        td = nc.temas_por_dia(B, A)
    td = td[td["tema"] != "ELECTION"]
    if not td.empty:
        piv = td.pivot_table(index="rotulo", columns="dia", values="pct", fill_value=0)
        piv = piv.loc[piv.mean(axis=1).sort_values().index]
        fig = go.Figure(go.Heatmap(
            z=piv.values, x=piv.columns, y=piv.index, colorscale=[[i / 7, c] for i, c in enumerate(nc.SEQUENCIAL)],
            xgap=2, ygap=2, colorbar=dict(title="% artigos", thickness=12),
            hovertemplate="%{y}<br>%{x|%d/%m}: %{z:.1f}% dos artigos<extra></extra>"))
        marcar_turnos(fig, periodo[0], periodo[1])
        st.plotly_chart(estilizar(fig, "Intensidade diária dos temas", max(420, 22 * len(piv) + 120)),
                        use_container_width=True, config=CFG)

    col_a, col_b = st.columns(2)
    tr = nc.temas_resumo(B, A)
    tr = tr[tr["tema"].isin(B.temas_rotulo["tema"]) & (tr["tema"] != "ELECTION")]
    with col_a:
        g = tr.sort_values("tom")
        fig = go.Figure(go.Bar(
            y=g["rotulo"], x=g["tom"], orientation="h", customdata=g["artigos"],
            marker=dict(color=g["tom"], colorscale=nc.DIVERGENTE, cmid=0, cmin=-3, cmax=3),
            hovertemplate="%{y}<br>tom %{x:.2f} · %{customdata:,} artigos<extra></extra>"))
        fig.update_layout(xaxis_title="Tom médio dos artigos com o tema")
        st.plotly_chart(estilizar(fig, "Tom associado a cada tema", 640), use_container_width=True, config=CFG)
    with col_b:
        tf = nc.temas_por_fase(B, A)
        tf = tf[tf["tema"] != "ELECTION"]
        piv = tf.pivot_table(index="rotulo", columns="fase", values="pct", fill_value=0, observed=True)
        piv = piv.loc[piv.mean(axis=1).sort_values().index]
        fig = go.Figure(go.Heatmap(
            z=piv.values, x=[str(c) for c in piv.columns], y=piv.index, xgap=2, ygap=2,
            colorscale=[[i / 7, c] for i, c in enumerate(nc.SEQUENCIAL)], text=np.round(piv.values, 1),
            texttemplate="%{text}", textfont=dict(size=10),
            colorbar=dict(title="%", thickness=12),
            hovertemplate="%{y} — %{x}: %{z:.1f}%<extra></extra>"))
        st.plotly_chart(estilizar(fig, "Temas por fase da eleição (% dos artigos)", 640),
                        use_container_width=True, config=CFG)

# ================================================================= 4. Geografia
with abas[3]:
    u = nc.uf_resumo(B, A)
    met = st.radio("Cor do mapa", ["Tom médio", "Saldo de menções Lula × Flávio"], horizontal=True)
    if met == "Tom médio":
        cor, escala, cmid, rng, titulo_cb = u["tom"], nc.DIVERGENTE, 0, (-2.5, 2.5), "Tom"
    else:
        cor = u["saldo"]
        escala = [[0, "#2a78d6"], [0.5, "#f0efec"], [1, "#e34948"]]
        cmid, rng, titulo_cb = 0, (-0.5, 0.5), "← Flávio · Lula →"
    tam = 8 + 52 * np.sqrt(u["artigos"] / u["artigos"].max())
    fig = go.Figure(go.Scattergeo(
        lat=u["lat"], lon=u["lon"], text=u["uf"], mode="markers+text", textposition="middle center",
        textfont=dict(size=10, color=nc.TINTA),
        marker=dict(size=tam, color=cor, colorscale=escala, cmid=cmid, cmin=rng[0], cmax=rng[1],
                    line=dict(width=2, color=nc.SUPERFICIE), colorbar=dict(title=titulo_cb, thickness=12)),
        customdata=np.c_[u["nome"], u["artigos"], u["tom"], u["Lula"].fillna(0), u["Flávio Bolsonaro"].fillna(0)],
        hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]:,} artigos · tom %{customdata[2]:.2f}"
                      "<br>Lula: %{customdata[3]:,} · Flávio: %{customdata[4]:,}<extra></extra>"))
    fig.update_geos(projection_type="mercator", lonaxis_range=[-76, -32], lataxis_range=[-35, 7],
                    showcountries=True, countrycolor=nc.EIXO, showland=True, landcolor="#f4f3ef",
                    showocean=False, bgcolor=nc.SUPERFICIE, showframe=False)
    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.plotly_chart(estilizar(fig, "UFs mencionadas nos artigos (tamanho = volume)", 620),
                        use_container_width=True, config=CFG)
    with col_b:
        g = u.sort_values("artigos")
        fig = go.Figure(go.Bar(y=g["uf"], x=g["artigos"], orientation="h", marker_color="#2a78d6",
                               customdata=g["nome"], hovertemplate="%{customdata}: %{x:,}<extra></extra>"))
        st.plotly_chart(estilizar(fig, "Artigos por UF mencionada", 620), use_container_width=True, config=CFG)
    st.caption("Uma notícia pode mencionar várias UFs. DF concentra menções por sediar TSE, STF e o governo federal.")

    lp = B.locais_pais[B.locais_pais["id"].isin(A["id"])]
    paises = lp["pais"].value_counts().drop("BR", errors="ignore").head(20).sort_values()
    fig = go.Figure(go.Bar(y=paises.index.astype(str), x=paises.values, orientation="h", marker_color="#2a78d6",
                           hovertemplate="%{y}: %{x:,} artigos<extra></extra>"))
    st.plotly_chart(estilizar(fig, "Outros países mencionados junto à eleição (código FIPS)", 520),
                    use_container_width=True, config=CFG)

# ================================================================= 5. Rede
with abas[4]:
    c1_, c2_, c3_ = st.columns(3)
    tipo = c1_.radio("Entidades", ["Pessoas", "Organizações"], horizontal=True)
    n_nos = c2_.slider("Nº de entidades", 10, 80, 35)
    min_peso = c3_.slider("Coocorrência mínima", 5, 500, 40)
    G, pos = nc.rede_coocorrencia(B, A, n_nos, min_peso, "pessoas" if tipo == "Pessoas" else "orgs")
    if len(G) == 0:
        st.info("Nenhuma aresta com esses parâmetros — reduza a coocorrência mínima.")
    else:
        pmax = max(d["peso"] for *_, d in G.edges(data=True))
        fig = go.Figure()
        for u_, v_, d in G.edges(data=True):
            fig.add_scatter(x=[pos[u_][0], pos[v_][0]], y=[pos[u_][1], pos[v_][1]], mode="lines",
                            line=dict(width=0.5 + 5 * d["peso"] / pmax, color="rgba(137,135,129,0.35)"),
                            hoverinfo="skip", showlegend=False)
        nos = list(G.nodes)
        freq = np.array([G.nodes[n]["freq"] for n in nos])
        fig.add_scatter(
            x=[pos[n][0] for n in nos], y=[pos[n][1] for n in nos], mode="markers+text",
            text=nos, textposition="top center", textfont=dict(size=11, color=nc.TINTA),
            marker=dict(size=10 + 40 * np.sqrt(freq / freq.max()), color=[G.nodes[n]["tom"] for n in nos],
                        colorscale=nc.DIVERGENTE, cmid=0, cmin=-3, cmax=3,
                        line=dict(width=2, color=nc.SUPERFICIE), colorbar=dict(title="Tom", thickness=12)),
            customdata=np.c_[freq, [G.nodes[n]["tom"] for n in nos], [G.degree(n) for n in nos]],
            hovertemplate="<b>%{text}</b><br>%{customdata[0]:,} artigos · tom %{customdata[1]:.2f}"
                          "<br>%{customdata[2]} conexões<extra></extra>", showlegend=False)
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        st.plotly_chart(estilizar(fig, f"Rede de coocorrência de {tipo.lower()} (mesmo artigo)", 720),
                        use_container_width=True, config=CFG)
        st.caption("Tamanho = nº de artigos; cor = tom médio; espessura da aresta = nº de artigos em comum. "
                   "Layout por forças (Fruchterman–Reingold). Nomes vêm da tradução automática do GDELT.")
        com = pd.DataFrame([(n, G.nodes[n].get("comunidade", -1), G.nodes[n]["freq"]) for n in nos],
                           columns=["Entidade", "Comunidade", "Artigos"]).sort_values(["Comunidade", "Artigos"],
                                                                                    ascending=[True, False])
        with st.expander("Comunidades detectadas (modularidade gulosa)"):
            st.dataframe(com, hide_index=True, use_container_width=True)

# ================================================================= 6. Veículos e idiomas
with abas[5]:
    col_a, col_b = st.columns(2)
    with col_a:
        minimo = st.slider("Mínimo de artigos por veículo", 50, 2000, 400, step=50)
        vr = nc.veiculos_resumo(A, minimo)
        fig = go.Figure()
        for m in ["Nacional", "Internacional"]:
            g = vr[vr["midia"] == m]
            fig.add_scatter(x=g["tom"], y=g["veiculo"], mode="markers", name=m,
                            marker=dict(size=6 + 18 * np.sqrt(g["artigos"] / max(vr["artigos"].max(), 1)),
                                        color=nc.COR_MIDIA[m], line=dict(width=2, color=nc.SUPERFICIE)),
                            customdata=g["artigos"],
                            hovertemplate="%{y}<br>tom %{x:.2f} · %{customdata:,} artigos<extra></extra>")
        fig.add_vline(x=0, line_width=1, line_color=nc.EIXO)
        fig.update_layout(yaxis=dict(categoryorder="array", categoryarray=vr["veiculo"].tolist()),
                          xaxis_title="Tom médio")
        st.plotly_chart(estilizar(fig, "Tom médio por veículo", max(420, 18 * len(vr) + 120)),
                        use_container_width=True, config=CFG)
    with col_b:
        ir = idiomas_r = nc.idiomas_resumo(A, 15)
        g = ir.sort_values("artigos")
        fig = go.Figure(go.Bar(y=g["idioma"], x=g["artigos"], orientation="h",
                               marker=dict(color=g["tom"], colorscale=nc.DIVERGENTE, cmid=0, cmin=-3, cmax=3,
                                           colorbar=dict(title="Tom", thickness=12)),
                               customdata=g["tom"],
                               hovertemplate="%{y}: %{x:,} artigos · tom %{customdata:.2f}<extra></extra>"))
        fig.update_layout(xaxis_title="Artigos")
        st.plotly_chart(estilizar(fig, "Idioma de origem (cor = tom médio)", 520),
                        use_container_width=True, config=CFG)

    st.markdown("**Distribuição do tom** — nacional × internacional")
    fig = go.Figure()
    for m in ["Nacional", "Internacional"]:
        g = A[A["midia"] == m]
        fig.add_histogram(x=g["tom"].clip(-10, 10), name=m, histnorm="percent", nbinsx=80, opacity=0.6,
                          marker_color=nc.COR_MIDIA[m])
    fig.update_layout(barmode="overlay", xaxis_title="Tom", yaxis_title="% dos artigos")
    st.plotly_chart(estilizar(fig, None, 340), use_container_width=True, config=CFG)

# ================================================================= 7. Artigos
with abas[6]:
    busca = st.text_input("Buscar no endereço (URL) — ex.: debate, pesquisa, fraude, urna")
    T = A
    if busca:
        T = T[T["url"].str.contains(busca, case=False, na=False, regex=False)]
    ordem = st.selectbox("Ordenar por", ["Mais recentes", "Mais negativos", "Mais positivos"])
    T = T.sort_values({"Mais recentes": "datahora", "Mais negativos": "tom", "Mais positivos": "tom"}[ordem],
                      ascending=ordem == "Mais negativos")
    st.caption(f"{len(T):,} artigos".replace(",", "."))
    st.dataframe(
        T[["datahora", "veiculo", "idioma", "midia", "tom", "url"]].head(1000),
        column_config={"url": st.column_config.LinkColumn("URL"),
                       "datahora": st.column_config.DatetimeColumn("Data/hora", format="DD/MM HH:mm"),
                       "tom": st.column_config.NumberColumn("Tom", format="%.2f")},
        hide_index=True, use_container_width=True, height=520)
    st.download_button("Baixar seleção (CSV)", T.drop(columns=[c for c in T if c.startswith("cita_")])
                       .to_csv(index=False).encode("utf-8"), "artigos_filtrados.csv", "text/csv")
