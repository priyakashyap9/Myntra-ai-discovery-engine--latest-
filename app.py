# =====================================================
# MULTI-SOURCE DATA UPLOAD
# =====================================================

st.divider()

st.subheader("📂 Upload Feedback Datasets")

uploaded_files = st.file_uploader(
    "Upload Play Store and/or Reddit CSV files",
    type=["csv"],
    accept_multiple_files=True
)

if uploaded_files:

    all_data = []

    for uploaded_file in uploaded_files:

        temp_df = pd.read_csv(uploaded_file)

        filename = uploaded_file.name.lower()

        # -------------------------------
        # PLAY STORE
        # -------------------------------

        if "content" in temp_df.columns:

            temp_df["source"] = "Play Store"
            temp_df["raw_text"] = temp_df["content"]
            temp_df["source_url"] = ""

        # -------------------------------
        # REDDIT
        # -------------------------------

        elif "raw_text" in temp_df.columns:

            temp_df["source"] = "Reddit"

            if "source_url" in temp_df.columns:
                temp_df["source_url"] = temp_df["source_url"]
            else:
                temp_df["source_url"] = ""

        else:

            st.warning(
                f"Skipped {uploaded_file.name}: "
                "no recognised review-text column."
            )

            continue

        # Keep only records containing text

        temp_df = temp_df[
            temp_df["raw_text"].notna()
        ].copy()

        all_data.append(temp_df)

    # -------------------------------
    # MERGE
    # -------------------------------

    if all_data:

        master_df = pd.concat(
            all_data,
            ignore_index=True
        )

        st.success(
            f"Loaded {len(master_df):,} total records "
            f"from {len(all_data)} dataset(s)."
        )

        # -------------------------------
        # SOURCE BREAKDOWN
        # -------------------------------

        st.subheader("📊 Sources")

        source_counts = (
            master_df["source"]
            .value_counts()
            .reset_index()
        )

        source_counts.columns = [
            "Source",
            "Records"
        ]

        st.dataframe(
            source_counts,
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------
        # PREVIEW
        # -------------------------------

        st.subheader("Dataset Preview")

        st.dataframe(
            master_df[
                [
                    "source",
                    "raw_text",
                    "source_url"
                ]
            ].head(10),
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------
        # ANALYSE
        # -------------------------------

        if st.button(
            "🔍 Analyse All Feedback",
            type="primary"
        ):

            results = []

            progress = st.progress(0)

            total = len(master_df)

            for i, row in master_df.iterrows():

                classification = classify_review(
                    row["raw_text"]
                )

                classification["source"] = row["source"]
                classification["source_url"] = row["source_url"]
                classification["raw_text"] = row["raw_text"]

                results.append(
                    classification
                )

                progress.progress(
                    (i + 1) / total
                )

            results_df = pd.DataFrame(results)

            relevant_df = results_df[
                results_df["relevant"] == True
            ].copy()

            # -------------------------------
            # METRICS
            # -------------------------------

            st.divider()

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Reviews analysed",
                f"{len(master_df):,}"
            )

            col2.metric(
                "Relevant signals",
                f"{len(relevant_df):,}"
            )

            col3.metric(
                "Signal rate",
                f"{len(relevant_df) / len(master_df) * 100:.1f}%"
            )

            # -------------------------------
            # SOURCE RESULTS
            # -------------------------------

            st.subheader(
                "🔎 Signals by Source"
            )

            if len(relevant_df) > 0:

                source_results = (
                    relevant_df["source"]
                    .value_counts()
                    .reset_index()
                )

                source_results.columns = [
                    "Source",
                    "Relevant Signals"
                ]

                st.dataframe(
                    source_results,
                    use_container_width=True,
                    hide_index=True
                )

            # -------------------------------
            # RELEVANT SIGNALS
            # -------------------------------

            st.subheader(
                "Relevant User Signals"
            )

            display_columns = [
                "source",
                "shopping_stage",
                "wishlist_type",
                "purchase_intent",
                "primary_barrier",
                "purchase_trigger",
                "raw_text",
                "source_url"
            ]

            st.dataframe(
                relevant_df[display_columns],
                use_container_width=True,
                hide_index=True
            )

            # -------------------------------
            # DOWNLOAD
            # -------------------------------

            output_csv = results_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Combined Analysis",
                output_csv,
                "myntra_discovery_engine_analysis.csv",
                "text/csv"
            )
