#!/usr/bin/env python3
"""Render the web-update figures exclusively from October public aggregates."""
from pathlib import Path
import argparse

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Data_Insight/Assets/Reproducibility/update_202610"
OUT = ROOT / "Data_Insight/Assets/Figures/update_202610"
HTML = ROOT / "Data_Insight/Assets/Interactive/update_202610"
DOMAINS = ["Social Sciences", "Health Sciences", "Physical Sciences", "Life Sciences"]
COLORS = ["#285f8f", "#b55d39", "#49867a", "#8d6b9d"]
COUNTRY_NAMES = {
    "USA": "United States", "US": "United States",
    "UK": "United Kingdom", "GB": "United Kingdom",
    "KR": "South Korea", "CA": "Canada", "DE": "Germany",
    "AU": "Australia", "NL": "Netherlands", "FR": "France",
    "CN": "China", "IT": "Italy",
    "IGO": "International organizations", "EU": "European Union",
}
plt.rcParams.update({"font.size":11,"axes.spines.top":False,"axes.spines.right":False,
                     "axes.titleweight":"bold","figure.facecolor":"white","savefig.facecolor":"white"})


def load(name):
    return pd.read_csv(DATA / f"{name}.csv", keep_default_na=False)


def save(fig, name):
    fig.savefig(OUT/f"{name}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def interactive(fig, name):
    fig.update_layout(template="plotly_white",font=dict(size=14),margin=dict(l=30,r=35,t=65,b=60))
    fig.write_html(HTML/f"{name}.html", include_plotlyjs="directory", config={"displaylogo":False,"responsive":True})


def main():
    global DATA, OUT, HTML
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',type=Path,default=DATA)
    ap.add_argument('--out-dir',type=Path,default=OUT)
    ap.add_argument('--html-dir',type=Path,default=HTML)
    args=ap.parse_args()
    DATA,OUT,HTML=args.data_dir,args.out_dir,args.html_dir
    OUT.mkdir(parents=True, exist_ok=True)
    HTML.mkdir(parents=True, exist_ok=True)
    inbound = load("korea_inbound_sources")
    inbound["share_pct"] = inbound.citation_rows / inbound.citation_rows.sum() * 100
    outbound = load("korea_outbound_countries")
    outbound = outbound[outbound.research_country != "Unassigned"].copy()
    outbound["share_pct"] = outbound.citation_rows / outbound.citation_rows.sum() * 100
    fig, axes = plt.subplots(1,2,figsize=(12,5.5),layout="constrained")
    flow = make_subplots(rows=1,cols=2,subplot_titles=("Policy sources → Korean research", "Korean policy → research countries"),horizontal_spacing=.18)
    for ax,df,col,title,i in zip(axes,[inbound,outbound],["policy_country","research_country"],
                                ["Policy sources → Korean research", "Korean policy → research countries"],[1,2]):
        top=df.head(10).iloc[::-1]
        labels=top[col].replace(COUNTRY_NAMES)
        ax.barh(labels,top.share_pct,color=COLORS[i-1])
        ax.set(xlabel="Share of citations (%)",title=title,xlim=(0,max(top.share_pct)*1.23))
        ax.bar_label(ax.containers[0],labels=[f"{x:.1f}%" for x in top.share_pct],padding=4,fontsize=10)
        flow.add_trace(go.Bar(x=top.share_pct,y=labels,orientation="h",showlegend=False,
                             marker_color=COLORS[i-1],customdata=top.citation_rows,
                             hovertemplate="%{y}<br>%{x:.2f}%<br>%{customdata:,} citations<extra></extra>"),row=1,col=i)
        flow.update_xaxes(title_text="Share of citations (%)",row=1,col=i)
        flow.update_yaxes(automargin=True,row=1,col=i)
    flow.update_layout(height=560)
    save(fig,"korea_flows")
    interactive(flow,"korea_flows")

    domains=load("direction_domains")
    dirs=["Korean policy → research","Policy → Korean research"]
    mat=domains.pivot(index="domain",columns="direction",values="share_pct").reindex(DOMAINS)[dirs]
    fig,ax=plt.subplots(figsize=(10,4.8),layout="constrained")
    y=np.arange(len(DOMAINS))
    for i,d in enumerate(dirs):
        bars=ax.barh(y+(i-.5)*.35,mat[d],height=.33,label=d,color=COLORS[1-i])
        ax.bar_label(bars,labels=[f"{x:.1f}%" for x in mat[d]],padding=4,fontsize=10)
    ax.set(yticks=y,yticklabels=DOMAINS,xlabel="Share of domain assignments (%)",xlim=(0,70))
    ax.invert_yaxis()
    ax.legend(loc="lower right",frameon=False)
    save(fig,"korea_domains")
    dplot=px.bar(domains,x="share_pct",y="domain",color="direction",barmode="group",orientation="h",
                 color_discrete_map={dirs[0]:COLORS[1],dirs[1]:COLORS[0]},labels={"share_pct":"Share of domain assignments (%)"},
                 hover_data=["citation_rows"],category_orders={"domain":DOMAINS},title="Korea's two citation directions: domain composition")
    dplot.update_xaxes(range=[0,70])
    interactive(dplot,"korea_domains")

    sources=load("policy_sources").head(10).iloc[::-1]
    source_labels=sources.policy_country.replace(COUNTRY_NAMES)
    fig,axes=plt.subplots(1,2,figsize=(12,5.5),sharey=True,layout="constrained")
    axes[0].barh(source_labels,sources.citation_rows,color=COLORS[0])
    axes[0].set(xlabel="DOI-linked citations",title="Citation totals")
    axes[0].xaxis.set_major_formatter(FuncFormatter(lambda v,pos:f"{v/1e6:g}M"))
    axes[1].barh(source_labels,sources.citations_per_document,color=COLORS[2])
    axes[1].set(xlabel="Citations per citing policy document",title="Average within the same top 10 sources")
    save(fig,"policy_sources")
    source_plot=make_subplots(rows=1,cols=2,shared_yaxes=True,
                             subplot_titles=("Citation totals", "Average within the same top 10 sources"))
    for i,metric,color,axis_title in [
        (1,"citation_rows",COLORS[0],"DOI-linked citations"),
        (2,"citations_per_document",COLORS[2],"Citations per citing policy document"),
    ]:
        source_plot.add_trace(go.Bar(x=sources[metric],y=source_labels,orientation="h",marker_color=color,
                                    showlegend=False,customdata=sources.policy_documents,
                                    hovertemplate="%{y}<br>%{x:,.2f}<br>%{customdata:,} citing policy documents<extra></extra>"),row=1,col=i)
        source_plot.update_xaxes(title_text=axis_title,rangemode="tozero",row=1,col=i)
        source_plot.update_yaxes(automargin=True,row=1,col=i)
    source_plot.update_layout(height=560)
    interactive(source_plot,"policy_sources")

    types=load("source_type_domains")
    tmat=types.pivot(index="source_type",columns="domain",values="citation_rows").fillna(0).reindex(columns=DOMAINS,fill_value=0)
    order=tmat.sum(axis=1).sort_values(ascending=False).head(7).index
    tmat=tmat.loc[order]; shares=tmat.div(tmat.sum(axis=1),axis=0)*100
    fig,ax=plt.subplots(figsize=(11,5),layout="constrained")
    left=np.zeros(len(shares))
    for d,color in zip(DOMAINS,COLORS):
        ax.barh(shares.index,shares[d],left=left,label=d,color=color)
        left+=shares[d].to_numpy()
    ax.set(xlim=(0,100),xlabel="Share of domain assignments (%)")
    ax.invert_yaxis()
    ax.legend(loc="upper center",bbox_to_anchor=(.5,-.16),ncol=2,frameon=False)
    save(fig,"source_type_domains")
    type_plot=go.Figure()
    for d,color in zip(DOMAINS,COLORS):
        type_plot.add_trace(go.Bar(x=shares[d],y=shares.index,orientation="h",name=d,marker_color=color,
                                  customdata=tmat[d],hovertemplate="%{y}<br>"+d+"<br>%{x:.2f}%<br>%{customdata:,} domain assignments<extra></extra>"))
    type_plot.update_layout(barmode="stack",height=560,legend=dict(orientation="h",y=-.2),
                            title="Domain composition by policy-source type")
    type_plot.update_xaxes(range=[0,100],title_text="Share of domain assignments (%)")
    type_plot.update_yaxes(autorange="reversed",automargin=True)
    interactive(type_plot,"source_type_domains")

    topics=load("topic_metrics").head(300).copy()
    topics["recent_share_pct"]=pd.to_numeric(topics.recent_share_pct,errors="coerce")
    fig,ax=plt.subplots(figsize=(10,5.7),layout="constrained")
    for domain,color in zip(DOMAINS,COLORS):
        d=topics[topics.domain==domain]
        ax.scatter(d.citations_per_work,d.recent_share_pct,s=28,alpha=.65,color=color,label=domain)
    ymax=max(5,5*np.ceil(topics.recent_share_pct.max()*1.1/5))
    ax.set(xlabel="DOI-linked citations per cited work",ylabel="Cited works published in 2023–2025 (%)",ylim=(0,ymax))
    ax.legend(loc="upper right",frameon=False)
    save(fig,"topic_intensity_recency")
    topic_plot=px.scatter(topics,x="citations_per_work",y="recent_share_pct",color="domain",hover_name="topic",
                           hover_data=["citation_rows","cited_works","recent_works","eligible_year_works"],
                           color_discrete_map=dict(zip(DOMAINS,COLORS)),
                           labels={"citations_per_work":"DOI-linked citations per cited work","recent_share_pct":"Cited works published in 2023–2025 (%)"},
                           title="Top 300 topics by DOI-linked citations")
    topic_plot.update_yaxes(range=[0,ymax])
    interactive(topic_plot,"topic_intensity_recency")

    years=load("publication_year")
    years["pubyear"]=pd.to_numeric(years.pubyear,errors="coerce")
    years=years[years.pubyear.between(1990,2026)]
    fig,ax=plt.subplots(figsize=(10,4),layout="constrained")
    ax.bar(years.pubyear,years.citation_rows,color=COLORS[0])
    ax.set(xlabel="Publication year of cited research",ylabel="DOI-linked citations",xlim=(1989,2027))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f"{v/1e6:g}M"))
    ax.axvspan(2025.5,2026.5,color="#e6e6e6",zorder=0)
    save(fig,"research_publication_year")
    year_plot=px.bar(years,x="pubyear",y="citation_rows",color_discrete_sequence=[COLORS[0]],
                     labels={"pubyear":"Publication year of cited research","citation_rows":"DOI-linked citations"},
                     title="Publication years of cited research")
    year_plot.update_traces(hovertemplate="%{x:.0f}<br>%{y:,} citations<extra></extra>")
    year_plot.update_xaxes(range=[1989,2027],dtick=5)
    year_plot.update_yaxes(rangemode="tozero")
    year_plot.add_vrect(x0=2025.5,x1=2026.5,fillcolor="#e6e6e6",opacity=1,line_width=0,layer="below")
    interactive(year_plot,"research_publication_year")
    print(f"Rendered six PNGs and six interactive figures in {OUT}")


if __name__ == '__main__':
    main()
