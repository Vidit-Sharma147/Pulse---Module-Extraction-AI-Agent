import streamlit as st
import json
import csv
import io
import yaml
import itertools

from module_extractor import run

st.set_page_config(page_title="Pulse - Module Extraction", layout="wide")

st.title("Pulse - Module Extraction")

st.write("Enter one or more documentation URLs (space or newline separated):")
urls_input = st.text_area("Documentation URLs", height=120, placeholder="https://help.instagram.com\nhttps://support.neo.space/hc/en-us")
max_pages = st.number_input("Max pages (total)", min_value=0, max_value=100000, value=0, step=50)
per_domain_limit = st.number_input("Max pages per domain", min_value=0, max_value=100000, value=0, step=50)
no_limits = st.checkbox("No limits (crawl as much as allowed)", value=True)

if st.button("Extract Modules"):
    urls = [u.strip() for u in urls_input.split() if u.strip()]
    if not urls:
        st.warning("Please enter at least one URL.")
    else:
        with st.spinner("Crawling and analyzing documentation..."):
            try:
                # Run extraction per URL to provide separate boxes and downloads
                results_by_url = {}
                used_max = 0 if no_limits else int(max_pages)
                used_domain = 0 if no_limits else int(per_domain_limit)
                for u in urls:
                    results_by_url[u] = run([u], max_pages=used_max, per_domain_limit=used_domain)

                combined_result = list(itertools.chain.from_iterable(results_by_url.values()))
                st.session_state["results_by_url"] = results_by_url
                st.session_state["combined_result"] = combined_result

                total_modules = sum(len(v) for v in results_by_url.values())
                st.success(f"Extraction complete. Found {total_modules} modules across {len(results_by_url)} URL(s).")
            except Exception as e:
                st.error(f"Extraction failed: {e}")

# Persisted per-URL results display and downloads
if st.session_state.get("results_by_url"):
    results_by_url = st.session_state["results_by_url"]

    # Per-URL boxes
    for idx, (u, res) in enumerate(results_by_url.items()):
        st.subheader(f"Results for {u}")
        st.json(res)

        # Per-URL JSON
        st.download_button(
            label="Download JSON",
            data=json.dumps(res, indent=2, ensure_ascii=False),
            file_name=f"pulse_modules_{idx+1}.json",
            mime="application/json",
            key=f"dl_json_{idx}"
        )

        # Per-URL CSV (flatten submodules)
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["module", "description", "submodule", "sub_description", "confidence"])
        for m in res:
            mod = m.get("module", "")
            desc = m.get("Description", "")
            conf = m.get("confidence", "")
            subs = m.get("Submodules", {}) or {}
            if subs:
                for sm_name, sm_desc in subs.items():
                    writer.writerow([mod, desc, sm_name, sm_desc, conf])
            else:
                writer.writerow([mod, desc, "", "", conf])
        st.download_button(
            label="Download CSV",
            data=csv_buf.getvalue(),
            file_name=f"pulse_modules_{idx+1}.csv",
            mime="text/csv",
            key=f"dl_csv_{idx}"
        )

        # Per-URL YAML
        yaml_str = yaml.safe_dump(res, allow_unicode=True, sort_keys=False)
        st.download_button(
            label="Download YAML",
            data=yaml_str,
            file_name=f"pulse_modules_{idx+1}.yaml",
            mime="text/yaml",
            key=f"dl_yaml_{idx}"
        )

    # Download all together section
    st.subheader("Download All Results")
    combined_result = st.session_state.get("combined_result", [])

    # All JSON
    st.download_button(
        label="Download All JSON",
        data=json.dumps(combined_result, indent=2, ensure_ascii=False),
        file_name="pulse_modules_all.json",
        mime="application/json",
        key="dl_all_json"
    )

    # All CSV
    all_csv_buf = io.StringIO()
    all_writer = csv.writer(all_csv_buf)
    all_writer.writerow(["module", "description", "submodule", "sub_description", "confidence"])
    for m in combined_result:
        mod = m.get("module", "")
        desc = m.get("Description", "")
        conf = m.get("confidence", "")
        subs = m.get("Submodules", {}) or {}
        if subs:
            for sm_name, sm_desc in subs.items():
                all_writer.writerow([mod, desc, sm_name, sm_desc, conf])
        else:
            all_writer.writerow([mod, desc, "", "", conf])
    st.download_button(
        label="Download All CSV",
        data=all_csv_buf.getvalue(),
        file_name="pulse_modules_all.csv",
        mime="text/csv",
        key="dl_all_csv"
    )

    # All YAML
    all_yaml_str = yaml.safe_dump(combined_result, allow_unicode=True, sort_keys=False)
    st.download_button(
        label="Download All YAML",
        data=all_yaml_str,
        file_name="pulse_modules_all.yaml",
        mime="text/yaml",
        key="dl_all_yaml"
    )

    # Clear persisted results
    if st.button("Clear Result"):
        st.session_state.pop("results_by_url", None)
        st.session_state.pop("combined_result", None)
        st.success("Result cleared.")
