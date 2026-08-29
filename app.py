import streamlit as st
import pandas as pd
import re

# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Myntra AI Discovery Engine",
    page_icon="🔎",
    layout="wide"
)


# =====================================================
# CLASSIFIER
# =====================================================

def classify_review(text):

    text = str(text).lower()

    result = {
        "relevant": False,
        "shopping_stage": "UNKNOWN",
        "wishlist_type": "NOT_RELEVANT",
        "purchase_intent": "LOW",
        "primary_barrier": "OTHER",
        "purchase_trigger": "NOT_MENTIONED",
        "category": "EXCLUDE"
    }

    # -------------------------------------------------
    # POST-PURCHASE ISSUES
    # -------------------------------------------------

    post_purchase_patterns = [
        r"wanted to exchange",
        r"want to exchange",
        r"wanted to return",
        r"want to return",
        r"received damaged",
        r"wrong product",
        r"refund",
        r"return request",
        r"exchange process"
    ]

    if any(re.search(p, text) for p in post_purchase_patterns):
        return result


    # -------------------------------------------------
    # WAITING FOR SALE
    # -------------------------------------------------

    if re.search(
        r"didn't order.*sale|"
        r"did not order.*sale|"
        r"didn't buy.*sale|"
        r"did not buy.*sale|"
        r"wait.*sale.*buy|"
        r"waiting.*sale.*buy|"
        r"wait.*discount.*buy|"
        r"waiting.*discount.*buy|"
        r"shortlisted.*buy.*sale|"
        r"shortlisted.*sale.*buy|"
        r"wanted to buy.*sale|"
        r"wanted.*buy.*sale|"
        r"planned to buy.*sale|"
        r"planned.*buy.*sale",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "WISHLIST",
            "wishlist_type": "CONDITIONAL_PURCHASE",
            "purchase_intent": "HIGH",
            "primary_barrier": "WAITING_FOR_SALE",
            "purchase_trigger": "SALE_OR_DISCOUNT",
            "category": "PURCHASE_BARRIER"
        })

        return result


    # -------------------------------------------------
    # PRICE BARRIER
    # -------------------------------------------------

    if re.search(
        r"couldn't buy.*expensive|"
        r"could not buy.*expensive|"
        r"cannot buy.*expensive|"
        r"can't buy.*expensive|"
        r"didn't buy.*expensive|"
        r"did not buy.*expensive|"
        r"not buying.*expensive|"
        r"won't buy.*expensive|"
        r"too expensive to buy|"
        r"price.*stopped.*buy|"
        r"price.*prevented.*buy|"
        r"expensive.*didn't buy",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "BROWSING",
            "wishlist_type": "NOT_RELEVANT",
            "purchase_intent": "MEDIUM",
            "primary_barrier": "PRICE_BLOCKED_PURCHASE",
            "purchase_trigger": "LOWER_PRICE_OR_DISCOUNT",
            "category": "PURCHASE_BARRIER"
        })

        return result


    # -------------------------------------------------
    # SIZE / FIT UNCERTAINTY
    # -------------------------------------------------

    if re.search(
        r"not sure.*size|"
        r"which size.*buy|"
        r"what size.*buy|"
        r"size chart.*confus|"
        r"size guide.*confus",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "BROWSING",
            "wishlist_type": "NOT_RELEVANT",
            "purchase_intent": "HIGH",
            "primary_barrier": "SIZE_UNCERTAINTY",
            "purchase_trigger": "SIZE_CONFIDENCE",
            "category": "PURCHASE_BARRIER"
        })

        return result


    # -------------------------------------------------
    # CHECKOUT FAILURE
    # -------------------------------------------------

    if re.search(
        r"want to order.*not placed|"
        r"order.*not placed|"
        r"finally.*order.*not placed",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CHECKOUT",
            "wishlist_type": "NOT_RELEVANT",
            "purchase_intent": "VERY_HIGH",
            "primary_barrier": "CHECKOUT_FLOW_FAILURE",
            "purchase_trigger": "FIX_CHECKOUT_FLOW",
            "category": "CONVERSION_BLOCKER"
        })

        return result


    # -------------------------------------------------
    # DELIVERY UNAVAILABLE
    # -------------------------------------------------

    if re.search(
        r"not deliverable.*pincode|"
        r"not deliverable.*selected pincode|"
        r"showing not deliverable",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CHECKOUT",
            "wishlist_type": "NOT_RELEVANT",
            "purchase_intent": "VERY_HIGH",
            "primary_barrier": "DELIVERY_UNAVAILABLE_AT_CHECKOUT",
            "purchase_trigger": "ENABLE_DELIVERY_TO_LOCATION",
            "category": "CONVERSION_BLOCKER"
        })

        return result


    # -------------------------------------------------
    # PAYMENT METHOD
    # -------------------------------------------------

    if re.search(
        r"no cash on delivery|"
        r"no cod|"
        r"cod.*not available|"
        r"cash on delivery.*not available",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CHECKOUT",
            "wishlist_type": "NOT_RELEVANT",
            "purchase_intent": "VERY_HIGH",
            "primary_barrier": "PAYMENT_METHOD_UNAVAILABLE",
            "purchase_trigger": "ENABLE_PREFERRED_PAYMENT_METHOD",
            "category": "CONVERSION_BLOCKER"
        })

        return result


    # -------------------------------------------------
    # HIGH-INTENT WISHLIST
    # -------------------------------------------------

    if re.search(
        r"wishlist.*save.*time.*order|"
        r"open wishlist products.*order",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "WISHLIST",
            "wishlist_type": "PURCHASE_READY",
            "purchase_intent": "HIGH",
            "primary_barrier": "NONE_IDENTIFIED",
            "purchase_trigger": "FAST_RETURN_TO_SAVED_PRODUCTS",
            "category": "HIGH_INTENT_WISHLIST_BEHAVIOUR"
        })

        return result


    # -------------------------------------------------
    # WISHLIST LOADING
    # -------------------------------------------------

    if re.search(
        r"open.*wishlist.*slow|"
        r"wishlist.*functions slow|"
        r"wishlisted product.*takes.*time|"
        r"wishlist.*takes.*time.*open",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "WISHLIST",
            "wishlist_type": "UNKNOWN",
            "purchase_intent": "MEDIUM",
            "primary_barrier": "WISHLIST_LOADING_FRICTION",
            "purchase_trigger": "FASTER_WISHLIST_LOADING",
            "category": "WISHLIST_FRICTION"
        })

        return result


    # -------------------------------------------------
    # CART → WISHLIST
    # -------------------------------------------------

    if re.search(
        r"move to wishlist.*takes.*time|"
        r"wishlist pop up.*takes.*long|"
        r"cart.*move.*wishlist.*long",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CART",
            "wishlist_type": "BOOKMARK_ONLY",
            "purchase_intent": "MEDIUM",
            "primary_barrier": "CART_TO_WISHLIST_FRICTION",
            "purchase_trigger": "FASTER_SAVE_FOR_LATER",
            "category": "WISHLIST_FRICTION"
        })

        return result


    # -------------------------------------------------
    # GENERAL WISHLIST MENTION
    # -------------------------------------------------

    if re.search(
        r"wishlist|wishlisted|wish list|saved items|saved products",
        text
    ):

        result.update({
            "relevant": True,
            "shopping_stage": "WISHLIST",
            "wishlist_type": "UNKNOWN",
            "purchase_intent": "UNKNOWN",
            "primary_barrier": "NONE_IDENTIFIED",
            "purchase_trigger": "NOT_MENTIONED",
            "category": "WISHLIST_BEHAVIOUR"
        })

        return result


    return result


# =====================================================
# OPPORTUNITY INTERPRETATION
# =====================================================

opportunity_info = {

    "WAITING_FOR_SALE": {
        "title": "Price & Sale Uncertainty",
        "why": "Users may postpone purchases while waiting for a better price or sale.",
        "product": "Price-history and price-drop alerts for wishlisted products."
    },

    "PRICE_BLOCKED_PURCHASE": {
        "title": "Price Barrier",
        "why": "Price can prevent users from converting even when they are interested in a product.",
        "product": "Price-drop alerts and clearer price/value information."
    },

    "PAYMENT_METHOD_UNAVAILABLE": {
        "title": "Payment Flexibility",
        "why": "High-intent users can reach checkout but fail when their preferred payment method is unavailable.",
        "product": "Show available payment options earlier and provide alternatives."
    },

    "DELIVERY_UNAVAILABLE_AT_CHECKOUT": {
        "title": "Delivery Availability",
        "why": "Users can select a product but discover delivery restrictions at checkout.",
        "product": "Surface delivery availability earlier in the shopping journey."
    },

    "CHECKOUT_FLOW_FAILURE": {
        "title": "Checkout Friction",
        "why": "Users with strong purchase intent report difficulty completing their order.",
        "product": "Reduce checkout friction and clearly explain failed orders."
    },

    "CART_TO_WISHLIST_FRICTION": {
        "title": "Save-for-Later Friction",
        "why": "Users use wishlist as a way to defer purchases and return later.",
        "product": "Make saving products from cart instant and visible."
    },

    "WISHLIST_LOADING_FRICTION": {
        "title": "Wishlist Access Friction",
        "why": "Slow wishlist access can interrupt the return-to-purchase journey.",
        "product": "Improve wishlist loading speed and access to saved products."
    }
}


# =====================================================
# HEADER
# =====================================================

st.title("🔎 Myntra AI Discovery Engine")

st.caption(
    "Discover purchase barriers, wishlist behaviour and "
    "conversion opportunities from customer feedback."
)

st.divider()


# =====================================================
# UPLOAD MULTIPLE DATASETS
# =====================================================

st.subheader("📂 Upload Feedback Datasets")

st.write(
    "Upload your Play Store CSV and verified Reddit CSV together."
)

uploaded_files = st.file_uploader(
    "Select CSV files",
    type=["csv"],
    accept_multiple_files=True
)


# =====================================================
# PROCESS UPLOADS
# =====================================================

if uploaded_files:

    all_data = []

    for uploaded_file in uploaded_files:

        try:
            temp_df = pd.read_csv(uploaded_file)
        except Exception as e:

            st.error(
                f"Could not read {uploaded_file.name}: {e}"
            )

            continue


        # ---------------------------------------------
        # PLAY STORE
        # ---------------------------------------------

        if "content" in temp_df.columns:

            temp_df["source"] = "Play Store"

            temp_df["raw_text"] = (
                temp_df["content"]
                .fillna("")
                .astype(str)
            )

            temp_df["source_url"] = ""


        # ---------------------------------------------
        # REDDIT
        # ---------------------------------------------

        elif "raw_text" in temp_df.columns:

            temp_df["source"] = "Reddit"

            temp_df["raw_text"] = (
                temp_df["raw_text"]
                .fillna("")
                .astype(str)
            )

            if "source_url" not in temp_df.columns:

                temp_df["source_url"] = ""


        # ---------------------------------------------
        # UNKNOWN FILE
        # ---------------------------------------------

        else:

            st.warning(
                f"Skipped {uploaded_file.name}: "
                "no recognised review-text column."
            )

            continue


        # Remove empty records

        temp_df = temp_df[
            temp_df["raw_text"].str.strip() != ""
        ].copy()

        all_data.append(temp_df)


    # =================================================
    # MERGE
    # =================================================

    if all_data:

        master_df = pd.concat(
            all_data,
            ignore_index=True
        )


        # =============================================
        # DATASET SUMMARY
        # =============================================

        st.success(
            f"Loaded {len(master_df):,} total records "
            f"from {len(all_data)} dataset(s)."
        )


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


        # =============================================
        # PREVIEW
        # =============================================

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


        # =============================================
        # ANALYSE
        # =============================================

        if st.button(
            "🔍 Analyse All Feedback",
            type="primary"
        ):

            results = []

            progress = st.progress(0)

            total = len(master_df)

            for i, (_, row) in enumerate(
                master_df.iterrows()
            ):

                classification = classify_review(
                    row["raw_text"]
                )

                classification["source"] = (
                    row["source"]
                )

                classification["source_url"] = (
                    row["source_url"]
                )

                classification["raw_text"] = (
                    row["raw_text"]
                )

                results.append(
                    classification
                )

                progress.progress(
                    (i + 1) / total
                )


            results_df = pd.DataFrame(results)


            # =========================================
            # RELEVANT REVIEWS
            # =========================================

            relevant_df = results_df[
                results_df["relevant"] == True
            ].copy()


            opportunity_df = relevant_df[
                relevant_df["primary_barrier"]
                != "NONE_IDENTIFIED"
            ].copy()


            # =========================================
            # METRICS
            # =========================================

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

            signal_rate = (
                len(relevant_df)
                / len(master_df)
                * 100
            )

            col3.metric(
                "Signal rate",
                f"{signal_rate:.1f}%"
            )


            # =========================================
            # SOURCE RESULTS
            # =========================================

            st.subheader(
                "🔎 Relevant Signals by Source"
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


            # =========================================
            # OPPORTUNITY AREAS
            # =========================================

            if len(opportunity_df) > 0:

                frequency = (
                    opportunity_df[
                        "primary_barrier"
                    ]
                    .value_counts()
                    .reset_index()
                )

                frequency.columns = [
                    "Barrier",
                    "Frequency"
                ]

                frequency["Share"] = (
                    frequency["Frequency"]
                    / len(opportunity_df)
                    * 100
                ).round(1)

                frequency["Opportunity"] = (
                    frequency["Barrier"]
                    .map(
                        lambda x:
                        opportunity_info.get(
                            x,
                            {}
                        ).get(
                            "title",
                            x.replace(
                                "_",
                                " "
                            ).title()
                        )
                    )
                )

                st.subheader(
                    "🏆 Opportunity Areas"
                )

                st.dataframe(
                    frequency[
                        [
                            "Opportunity",
                            "Frequency",
                            "Share"
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True
                )


                # =====================================
                # TOP OPPORTUNITY
                # =====================================

                top_barrier = (
                    frequency.iloc[0]["Barrier"]
                )

                info = opportunity_info.get(
                    top_barrier,
                    {
                        "title":
                            top_barrier.replace(
                                "_",
                                " "
                            ).title(),

                        "why":
                            "Users are reporting "
                            "this recurring issue.",

                        "product":
                            "Investigate this issue "
                            "with targeted product research."
                    }
                )

                st.divider()

                st.subheader(
                    "🎯 Highest-Frequency Opportunity"
                )

                st.markdown(
                    f"### {info['title']}"
                )

                st.write(
                    f"**Why it matters:** "
                    f"{info['why']}"
                )

                st.write(
                    f"**Potential product opportunity:** "
                    f"{info['product']}"
                )


                # =====================================
                # USER EVIDENCE
                # =====================================

                st.subheader(
                    "💬 User Evidence"
                )

                evidence = opportunity_df[
                    opportunity_df[
                        "primary_barrier"
                    ] == top_barrier
                ][
                    [
                        "source",
                        "raw_text",
                        "source_url"
                    ]
                ].head(5)

                st.dataframe(
                    evidence,
                    use_container_width=True,
                    hide_index=True
                )


            # =========================================
            # ALL RELEVANT SIGNALS
            # =========================================

            st.subheader(
                "🔎 Relevant User Signals"
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
                relevant_df[
                    display_columns
                ],
                use_container_width=True,
                hide_index=True
            )


            # =========================================
            # DOWNLOAD
            # =========================================

            output_csv = (
                results_df
                .to_csv(index=False)
                .encode("utf-8")
            )

            st.download_button(
                "⬇️ Download Combined Analysis",
                output_csv,
                "myntra_discovery_engine_analysis.csv",
                "text/csv"
                # =====================================================
# EXTERNAL EVIDENCE
# =====================================================

st.divider()

st.subheader("🌐 External Evidence")

st.caption(
    "Contextual evidence from public sources. "
    "These sources validate themes but are not counted "
    "as customer-review signals."
)

context_path = "myntra_context_sources.csv"

try:
    context_df = pd.read_csv(context_path)

    st.dataframe(
        context_df[
            [
                "source",
                "source_type",
                "theme",
                "evidence_text",
                "source_url"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇️ Download External Evidence",
        context_df.to_csv(index=False).encode("utf-8"),
        "myntra_external_evidence.csv",
        "text/csv"
    )

except FileNotFoundError:

    st.info(
        "Upload myntra_context_sources.csv to view "
        "external evidence."
    )
            )
