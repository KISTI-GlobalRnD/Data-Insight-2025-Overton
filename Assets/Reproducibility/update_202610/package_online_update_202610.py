#!/usr/bin/env python3
"""Bind current October public aggregates and their source files, then package them."""
from pathlib import Path
import hashlib
import json
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
PUBLIC=ROOT/'Data_Insight/Assets/Reproducibility/update_202610'
SCRIPTS=['analyze_online_update_202610.py','refine_online_update_202610.py',
         'plot_online_update_202610.py','write_online_update_202610.py',
         'update_online_landing_202610.py','package_online_update_202610.py']

def main():
    manifest=json.loads((PUBLIC/'provenance.json').read_text())
    # Do not silently legitimize changed aggregates: calculation owns CSV checksums.
    csvs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(PUBLIC.glob('*.csv'))}
    assert csvs==manifest['public_aggregate_sha256'], 'Rerun analysis after aggregate changes'
    for name in SCRIPTS:
        source=ROOT/'scripts'/name
        shutil.copyfile(source,PUBLIC/name)
        manifest['scripts'][name]=hashlib.sha256(source.read_bytes()).hexdigest()
    manifest['web_source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [ROOT/'Data_Insight/SI/update_202603.qmd',ROOT/'Data_Insight/SI/update_202603_en.qmd',
                  ROOT/'Data_Insight/index.html',ROOT/'Data_Insight/Assets/Site/promo.js']}
    manifest['public_support_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [PUBLIC/'README_KO.md',PUBLIC/'headline_metrics.json']}
    (PUBLIC/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    paths=sorted(p for p in PUBLIC.iterdir() if p.is_file() and p.suffix in ('.csv','.json','.md','.py'))
    with ZipFile(PUBLIC/'online_update_aggregates.zip','w',compression=ZIP_DEFLATED,compresslevel=9) as archive:
        for p in paths: archive.write(p,p.name)
    with ZipFile(PUBLIC/'online_update_aggregates.zip') as archive:
        assert archive.testzip() is None
        assert set(archive.namelist())=={p.name for p in paths}
        for p in paths: assert archive.read(p.name)==p.read_bytes()
    print(f'Packaged {len(csvs)} CSVs; {len(paths)} public files, ZIP verified')

if __name__=='__main__':
    main()
