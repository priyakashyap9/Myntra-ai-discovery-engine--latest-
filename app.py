import streamlit as st
import pandas as pd
import re

st.set_page_config(
    page_title="Myntra AI Discovery Engine",
    layout="wide"
)

st.title("🔎 Myntra AI Discovery Engine")
st.caption(
    "Discover purchase barriers, wishlist behaviour and conversion opportunities "
    "from customer feedback."
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

    # -----------------------------------------------
    # EXCLUDE OBVIOUS POST-PURCHASE ISSUES
    # -----------------------------------------------

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


    # -----------------------------------------------
    # WAITING FOR SALE
    # -----------------------------------------------

    if re.search(
        r"didn't order.*sale|did not order.*sale|"
        r"didn't buy.*sale|did not buy.*sale|"
        r"wait.*sale.*buy|waiting.*sale.*buy|"
        r"wait.*discount.*buy|waiting.*discount.*buy|"
        r"shortlisted.*buy.*sale|shortlisted.*sale.*buy|"
        r"wanted to buy.*sale|wanted.*buy.*sale|"
        r"planned to buy.*sale|planned.*buy.*sale|"
        r"purchase.*later.*sale",
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


    # -----------------------------------------------
    # PRICE BLOCKED PURCHASE
    # -----------------------------------------------

    if re.search(
        r"couldn't buy.*expensive|could not buy.*expensive|"
        r"cannot buy.*expensive|can't buy.*expensive|"
        r"didn't buy.*expensive|did not buy.*expensive|"
        r"not buying.*expensive|won't buy.*expensive|"
        r"too expensive to buy|price.*stopped.*buy|"
        r"price.*prevented.*buy|expensive.*didn't buy",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "BROWSING",
            "purchase_intent": "MEDIUM",
            "primary_barrier": "PRICE_BLOCKED_PURCHASE",
            "purchase_trigger": "LOWER_PRICE_OR_DISCOUNT",
            "category": "PURCHASE_BARRIER"
        })

        return result


    # -----------------------------------------------
    # SIZE / FIT
    # -----------------------------------------------

    if re.search(
        r"not sure.*size|which size.*buy|what size.*buy|"
        r"size chart.*confus|size guide.*confus",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "BROWSING",
            "purchase_intent": "HIGH",
            "primary_barrier": "SIZE_UNCERTAINTY",
            "purchase_trigger": "SIZE_CONFIDENCE",
            "category": "PURCHASE_BARRIER"
        })

        return result


    # -----------------------------------------------
    # CHECKOUT
    # -----------------------------------------------

    if re.search(
        r"want to order.*not placed|"
        r"order.*not placed|"
        r"finally.*order.*not placed",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CHECKOUT",
            "purchase_intent": "VERY_HIGH",
            "primary_barrier": "CHECKOUT_FLOW_FAILURE",
            "purchase_trigger": "FIX_CHECKOUT_FLOW",
            "category": "CONVERSION_BLOCKER"
        })

        return result


    # -----------------------------------------------
    # DELIVERY
    # -----------------------------------------------

    if re.search(
        r"not deliverable.*pincode|"
        r"not deliverable.*selected pincode|"
        r"showing not deliverable",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CHECKOUT",
            "purchase_intent": "VERY_HIGH",
            "primary_barrier": "DELIVERY_UNAVAILABLE_AT_CHECKOUT",
            "purchase_trigger": "ENABLE_DELIVERY_TO_LOCATION",
            "category": "CONVERSION_BLOCKER"
        })

        return result


    # -----------------------------------------------
    # PAYMENT
    # -----------------------------------------------

    if re.search(
        r"no cash on delivery|no cod|"
        r"cod.*not available|"
        r"cash on delivery.*not available",
        text
    ):
        result.update({
            "relevant": True,
            "shopping_stage": "CHECKOUT",
            "purchase_intent": "VERY_HIGH",
            "primary_barrier": "PAYMENT_METHOD_UNAVAILABLE",
            "purchase_trigger": "ENABLE_PREFERRED_PAYMENT_METHOD",
            "category": "CONVERSION_BLOCKER"
        })

        return result


    # -----------------------------------------------
    # HIGH-INTENT WISHLIST
    # -----------------------------------------------

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


    # -----------------------------------------------
    # WISHLIST LOADING
    # -----------------------------------------------

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


    # -----------------------------------------------
    # CART → WISHLIST
    # -----------------------------------------------

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

    return result


# =====================================================
# UPLOAD
# =====================================================

st.divider()

uploaded_file = st.file_uploader(
    "Upload customer feedback CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.success(f"Loaded {len(df):,} reviews")

    st.subheader("Dataset Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------
    # FIND REVIEW COLUMN
    # -----------------------------------------------

    possible_columns = [
        "content",
        "review",
        "text",
        "raw_text"
    ]

    text_column = None

    for column in possible_columns:
        if column in df.columns:
            text_column = column
            break

    if text_column is None:
        st.error(
            "No review-text column found."
        )
        st.stop()

    st.success(
        f"Review text column detected: `{text_column}`"
    )

    # -----------------------------------------------
    # ANALYSE
    # -----------------------------------------------

    if st.button(
        "🔍 Analyse Feedback",
        type="primary"
    ):

        results = []

        progress = st.progress(0)

        for i, text in enumerate(df[text_column]):

            classification = classify_review(text)

            classification["raw_text"] = text

            results.append(classification)

            progress.progress(
                (i + 1) / len(df)
            )

        results_df = pd.DataFrame(results)

        relevant_df = results_df[
            results_df["relevant"] == True
        ].copy()

        st.divider()

        # -------------------------------------------
        # METRICS
        # -------------------------------------------

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Reviews analysed",
            f"{len(df):,}"
        )

        col2.metric(
            "Relevant signals",
            f"{len(relevant_df):,}"
        )

        col3.metric(
            "Signal rate",
            f"{len(relevant_df) / len(df) * 100:.1f}%"
        )

        # -------------------------------------------
        # OPPORTUNITIES
        # -------------------------------------------

        opportunity_df = relevant_df[
            relevant_df["primary_barrier"] != "NONE_IDENTIFIED"
        ]

        if len(opportunity_df) > 0:

            frequency = (
                opportunity_df["primary_barrier"]
                .value_counts()
                .reset_index()
            )

            frequency.columns = [
                "Opportunity",
                "Frequency"
            ]

            frequency["Share"] = (
                frequency["Frequency"]
                / len(opportunity_df)
                * 100
            ).round(1)

            st.subheader(
                "🏆 Opportunity Areas"
            )

            st.dataframe(
                frequency,
                use_container_width=True,
                hide_index=True
            )

        # -------------------------------------------
        # SIGNALS
        # -------------------------------------------

        st.subheader(
            "🔎 Relevant User Signals"
        )

        display_columns = [
            "shopping_stage",
            "wishlist_type",
            "purchase_intent",
            "primary_barrier",
            "purchase_trigger",
            "raw_text"
        ]

        st.dataframe(
            relevant_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # -------------------------------------------
        # DOWNLOAD
        # -------------------------------------------

        output_csv = results_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Analysis",
            output_csv,
            "discovery_engine_output.csv",
            "text/csv"
        )
