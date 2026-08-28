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

    # POST-PURCHASE EXCLUSION
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

    # WAITING FOR SALE
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

    # PRICE BLOCKED PURCHASE
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

    # SIZE / FIT
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

    # CHECKOUT
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

    # DELIVERY
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

    # PAYMENT
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

    # HIGH INTENT WISHLIST
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

    # WISHLIST LOADING
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

    # CART → WISHLIST
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
# OPPORTUNITY INTERPRETATION
# =====================================================

opportunity_info = {

    "WAITING_FOR_SALE": {
        "title": "Price & Sale Uncertainty",
        "why": "Users may postpone purchasing when they expect a better price or when sale pricing changes.",
        "product": "Add price-history and price-drop alerts for wishlisted products."
    },

    "PAYMENT_METHOD_UNAVAILABLE": {
        "title": "Payment Flexibility",
        "why": "High-intent users can reach the purchase stage but fail when their preferred payment method is unavailable.",
        "product": "Show available payment options earlier and provide alternative payment methods."
    },

    "DELIVERY_UNAVAILABLE_AT_CHECKOUT": {
        "title": "Delivery Availability",
        "why": "Users can discover and select products but lose the ability to purchase when delivery becomes unavailable at checkout.",
        "product": "Surface delivery availability earlier in the shopping journey."
    },

    "CHECKOUT_FLOW_FAILURE": {
        "title": "Checkout Friction",
        "why": "Users with strong purchase intent report difficulty completing the order.",
        "product": "Reduce checkout steps and clearly explain why an order cannot be completed."
    },

    "CART_TO_WISHLIST_FRICTION": {
        "title": "Save-for-Later Friction",
        "why": "Users may use wishlist as a way to defer and return to products later.",
        "product": "Make saving products from cart instant and visible."
    },

    "WISHLIST_LOADING_FRICTION": {
        "title": "Wishlist Access Friction",
        "why": "Slow wishlist access can interrupt the user's return-to-purchase journey.",
        "product": "Improve wishlist loading speed and provide instant access to saved products."
    },

    "PRICE_BLOCKED_PURCHASE": {
        "title": "Price Barrier",
        "why": "Some users explicitly identify price as preventing purchase.",
        "product": "Offer price-drop alerts or clearer value/price comparison information."
    }
}


# =====================================================
# APP
# =====================================================

st.divider()

uploaded_file = st.file_uploader(
    "Upload customer feedback CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.success(f"Loaded {len(df):,} reviews")

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
        st.error("No review-text column found.")
        st.stop()

    st.info(f"Review text detected: `{text_column}`")

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

        opportunity_df = relevant_df[
            relevant_df["primary_barrier"] != "NONE_IDENTIFIED"
        ].copy()

        # =================================================
        # METRICS
        # =================================================

        st.divider()

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

        # =================================================
        # OPPORTUNITY RANKING
        # =================================================

        if len(opportunity_df) > 0:

            frequency = (
                opportunity_df["primary_barrier"]
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

            frequency["Opportunity"] = frequency[
                "Barrier"
            ].map(
                lambda x: opportunity_info.get(
                    x, {}
                ).get(
                    "title",
                    x.replace("_", " ").title()
                )
            )

            st.subheader("🏆 Opportunity Areas")

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

            # =================================================
            # TOP OPPORTUNITY
            # =================================================

            top_barrier = frequency.iloc[0]["Barrier"]

            info = opportunity_info.get(
                top_barrier,
                {
                    "title": top_barrier.replace("_", " ").title(),
                    "why": "Users are reporting this recurring issue.",
                    "product": "Investigate this issue with targeted product research."
                }
            )

            st.divider()

            st.subheader(
                "🎯 Highest-Frequency Opportunity"
            )

            st.markdown(
                f"## {info['title']}"
            )

            st.write(
                f"**Why it matters:** {info['why']}"
            )

            st.write(
                f"**Potential product opportunity:** {info['product']}"
            )

            # =================================================
            # EVIDENCE
            # =================================================

            st.subheader("💬 User Evidence")

            evidence = opportunity_df[
                opportunity_df["primary_barrier"] == top_barrier
            ][["raw_text"]].head(5)

            st.dataframe(
                evidence,
                use_container_width=True,
                hide_index=True
            )

        # =================================================
        # ALL SIGNALS
        # =================================================

        st.subheader("🔎 Relevant User Signals")

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

        # =================================================
        # DOWNLOAD
        # =================================================

        output_csv = results_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "⬇️ Download Analysis",
            output_csv,
            "discovery_engine_output.csv",
            "text/csv"
        )
