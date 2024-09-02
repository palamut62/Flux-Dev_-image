import streamlit as st
import replicate
import os
from dotenv import load_dotenv
from replicate.exceptions import ModelError, ReplicateError

# .env dosyasından çevre değişkenlerini yükle
load_dotenv()

# Replicate API Token'ını .env dosyasından al
api_token = os.getenv("REPLICATE_API_TOKEN")
if not api_token:
    st.error("REPLICATE_API_TOKEN bulunamadı. Lütfen .env dosyanızı kontrol edin.")
    st.stop()

os.environ["REPLICATE_API_TOKEN"] = api_token

st.set_page_config(layout="wide")

# CSS ile sidebar'ı sabitleme
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 350px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 350px;
        margin-left: -350px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar içeriği
with st.sidebar:
    st.image("flux-dev.png", use_column_width=True)
    st.title("Ayarlar")

    # Temel ayarlar
    num_outputs = st.slider("Kaç resim oluşturulsun?", 1, 4, 1)
    aspect_ratio = st.selectbox("En boy oranı:", ["1:1", "16:9", "9:16", "4:3", "3:4"])
    output_format = st.selectbox("Çıktı Formatı:", ["webp", "jpg", "png"])

    # Gelişmiş ayarlar (expander içinde)
    with st.expander("Gelişmiş Ayarlar"):
        guidance = st.slider("Guidance", 1.0, 20.0, 3.5)
        output_quality = st.slider("Çıktı Kalitesi", 1, 100, 80)
        prompt_strength = st.slider("Prompt Gücü", 0.1, 1.0, 0.8)
        num_inference_steps = st.slider("Inference Steps", 20, 50, 28)

# Ana sayfa içeriği
st.title("Flux-dev Modeli ile Resim Oluşturma")

# Sohbet benzeri arayüz
st.markdown("### Resim Açıklaması")
prompt = st.text_area("Resim için bir açıklama yazın:",
                      "black forest gateau cake spelling out the words \"FLUX DEV\", tasty, food photography, dynamic shot",
                      key="prompt")

if st.button("Resim Oluştur", key="generate"):
    try:
        with st.spinner("Resimler oluşturuluyor..."):
            output = replicate.run(
                "black-forest-labs/flux-dev",
                input={
                    "prompt": prompt,
                    "guidance": guidance,
                    "num_outputs": num_outputs,
                    "aspect_ratio": aspect_ratio,
                    "output_format": output_format,
                    "output_quality": output_quality,
                    "prompt_strength": prompt_strength,
                    "num_inference_steps": num_inference_steps
                }
            )

        # Oluşturulan resimleri göster
        st.markdown("### Oluşturulan Resimler")
        cols = st.columns(num_outputs)
        for i, img_url in enumerate(output):
            with cols[i]:
                st.image(img_url, caption=f"Resim {i + 1} ({output_format})", use_column_width=True)

        # Kullanılan prompt'u göster
        st.markdown(f"**Kullanılan açıklama:** {prompt}")

    except ModelError as e:
        if "NSFW content detected" in str(e):
            st.error("Uygunsuz içerik algılandı. Lütfen farklı bir açıklama deneyin veya mevcut açıklamayı değiştirin.")
        else:
            st.error(f"Model hatası: {str(e)}")
    except ReplicateError as e:
        if "Invalid version or not permitted" in str(e):
            st.error(
                "Model versiyonu geçersiz veya erişim izniniz yok. Lütfen model adını ve API anahtarınızı kontrol edin.")
        else:
            st.error(f"Replicate API hatası: {str(e)}")
    except Exception as e:
        st.error(f"Beklenmeyen bir hata oluştu: {str(e)}")

st.markdown("---")
st.markdown(
    "Not: Bu uygulama, Replicate'in black-forest-labs/flux-dev modelini kullanmaktadır. Gelişmiş ayarlar için yan çubuktaki 'Gelişmiş Ayarlar' bölümünü genişletin.")