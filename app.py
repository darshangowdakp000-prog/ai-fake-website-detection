
import streamlit as st
import re
import numpy as np
import pandas as pd
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(
    page_title="PhishGuard",
    page_icon="🛡️",
    layout="wide"
)

# Website design
st.markdown("""
<style>
.stApp {
    background: #f4f7fb;
}
.main-title {
    background: linear-gradient(120deg,#101c3a,#087e8b);
    padding: 30px;
    border-radius: 16px;
    color: white;
    text-align: center;
}
.main-title h1 {color:white;}
.main-title p {color:#e0f2fe;}
</style>
""", unsafe_allow_html=True)

# Extract URL features
def extract_features(url):
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    p = urlparse(url)
    host = p.hostname or ""
    full = url.lower()

    suspicious = [
        "login", "verify", "update", "secure",
        "account", "banking", "password",
        "free", "gift", "prize", "confirm"
    ]

    return [
        len(full),
        len(host),
        full.count("."),
        full.count("-"),
        full.count("@"),
        int(p.scheme == "https"),
        int(bool(re.search(r"\d+\.\d+\.\d+\.\d+", host))),
        sum(word in full for word in suspicious)
    ]

# Generate demonstration training data
@st.cache_resource
def train_model():
    rng = np.random.default_rng(42)
    X, y = [], []

    safe = [
        "https://www.wikipedia.org",
        "https://www.microsoft.com",
        "https://www.apple.com",
        "https://www.github.com",
        "https://www.bbc.com",
        "https://www.mozilla.org"
    ]

    risky = [
        "http://secure-login-account.example/verify",
        "http://free-prize-claim.example/login",
        "http://banking-update.example/password",
        "http://urgent-account-confirm.example",
        "http://verify-wallet.example/update"
    ]

    for _ in range(1000):
        if rng.random() < 0.5:
            url = rng.choice(safe)
            label = 0
        else:
            url = rng.choice(risky)
            label = 1

        X.append(extract_features(url))
        y.append(label)

    model = RandomForestClassifier(
        n_estimators=150,
        random_state=42
    )
    model.fit(X, y)
    return model

model = train_model()

# Header
st.markdown("""
<div class="main-title">
<h1>🛡️ PhishGuard</h1>
<h3>AI-Based Fake Website Detection</h3>
<p>Smart URL analysis using Machine Learning</p>
</div>
""", unsafe_allow_html=True)

st.write("")
st.subheader("🔍 Analyse a Website")

url = st.text_input(
    "Enter website URL",
    placeholder="https://example.com"
)

if st.button("Analyse Website", type="primary"):
    if not url.strip():
        st.warning("Please enter a website URL.")
    else:
        host = urlparse(
            url if "://" in url else "http://" + url
        ).hostname

        if not host or "." not in host:
            st.error("Please enter a valid-looking domain.")
        else:
            features = extract_features(url)
            probability = model.predict_proba([features])[0][1]
            score = int(probability * 100)

            st.divider()
            st.subheader("Analysis Result")

            col1, col2 = st.columns(2)

            col1.metric("Risk Score", f"{score}/100")

            if score >= 70:
                verdict = "🔴 High Risk"
                st.error(verdict)
            elif score >= 40:
                verdict = "🟠 Suspicious"
                st.warning(verdict)
            else:
                verdict = "🟢 Lower Risk"
                st.success(verdict)

            col2.metric("Classification", verdict)

            st.progress(score)

            st.write("### URL Characteristics")

            names = [
                "URL Length",
                "Hostname Length",
                "Number of Dots",
                "Hyphens",
                "@ Symbols",
                "HTTPS Enabled",
                "IP Address Host",
                "Suspicious Keywords"
            ]

            st.dataframe(
                pd.DataFrame({
                    "Feature": names,
                    "Value": features
                }),
                use_container_width=True,
                hide_index=True
            )

            st.info(
                "This result is an educational estimate. "
                "It does not guarantee that a website is safe "
                "or malicious."
            )

st.divider()

st.subheader("⚙️ How PhishGuard Works")

st.write("""
1. User enters a website URL.
2. The system extracts important URL characteristics.
3. A Random Forest machine learning model analyses those features.
4. The system displays an estimated risk score.
5. The website is classified as lower risk, suspicious or high risk.
""")

st.warning("""
Academic prototype: The model is trained on synthetic demonstration
examples, not a verified real-world phishing dataset. It analyses
URL characteristics only and does not inspect website content.
""")

st.caption("ETC CCA Project | AI-Based Fake Website Detection")
      
