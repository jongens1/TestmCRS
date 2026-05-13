import streamlit as st
import random
import time

# Nastavenie stránky
st.set_page_config(page_title="Alza Pick Test Pro", page_icon="📦")

# --- OPRAVENÁ FUNKCIA PRE OBRÁZKY ---
def get_image_url(code_or_url):
    val = str(code_or_url).strip()
    if val.startswith("http"):
        return val
    # Použitie formátu, ktorý si našiel - je oveľa stabilnejší
    return f"https://image.alza.cz/products/{val}/{val.jpg}?width=500&height=500".replace("{val.jpg}", f"{val}.jpg")

# Inicializácia session state
if 'picking_list' not in st.session_state:
    st.session_state.update({
        'picking_list': [],
        'current_index': 0,
        'start_time': None,
        'end_time': None,
        'test_active': False,
        'last_error': ""
    })

def check_scan():
    scanned_ean = st.session_state.scanner_input.strip()
    if not scanned_ean:
        return

    current_item = st.session_state.picking_list[st.session_state.current_index]
    
    if scanned_ean == current_item['ean']:
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        
        st.session_state.current_index += 1
        st.session_state.last_error = ""
        
        if st.session_state.current_index >= len(st.session_state.picking_list):
            st.session_state.end_time = time.time()
            st.session_state.test_active = False
    else:
        st.session_state.last_error = f"❌ Zlý EAN: {scanned_ean}"
    
    st.session_state.scanner_input = ""

st.title("📦 Alza Pick Test")

# --- 1. NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    st.write("Vlož dáta: **Kód, EAN, Počet**")
    data_input = st.text_area("Vstup dát", placeholder="SGR_AD_C351CB, 8595691027976, 2", height=150)
    
    if st.button("🚀 ŠTART", use_container_width=True):
        if data_input:
            temp_list = []
            for line in data_input.strip().split('\n'):
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        code = parts[0].strip()
                        ean = parts[1].strip()
                        qty = int(parts[2].strip())
                        # Klúč 'img' tu explicitne definujeme, aby nevznikol KeyError
                        img_source = parts[3].strip() if len(parts) > 3 else code
                        
                        for _ in range(qty):
                            temp_list.append({"code": code, "ean": ean, "img": img_source})
                    except: continue
            
            if temp_list:
                random.shuffle(temp_list)
                st.session_state.update({
                    'picking_list': temp_list,
                    'current_index': 0,
                    'test_active': True,
                    'start_time': None,
                    'end_time': None,
                    'last_error': ""
                })
                st.rerun()

# --- 2. TEST ---
elif st.session_state.test_active:
    idx = st.session_state.current_index
    total = len(st.session_state.picking_list)
    item = st.session_state.picking_list[idx]
    
    col1, col2 = st.columns([2, 1])
    col1.write(f"Položka: **{idx + 1} / {total}**")
    with col2:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.write(f"⏱️ **{elapsed:.0f} s**")
        else:
            st.warning("Čakám na 1. sken")

    st.progress(idx / total)

    # KARTA PRODUKTU
    st.markdown('<div style="border: 2px solid #eee; border-radius: 10px; padding: 15px; text-align: center; background: white;">', unsafe_allow_html=True)
    
    # Tu používame tvoj nový URL formát
    url = get_image_url(item.get('img', item['code']))
    st.image(url, width=250)
    
    st.markdown(f"""
        <h1 style="color: #1f77b4; margin-bottom: 0;">{item['code']}</h1>
        <p style="color: #666; font-size: 1.1em;">EAN: {item['ean']}</p>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.text_input("Naskenuj EAN", key="scanner_input", on_change=check_scan)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

# --- 3. VÝSLEDKY ---
elif st.session_state.end_time is not None:
    duration = st.session_state.end_time - st.session_state.start_time
    total_items = len(st.session_state.picking_list)
    
    st.balloons()
    st.success("✅ Test úspešne dokončený!")
    st.metric("Priemer na kus", f"{duration/total_items:.2f} s")
    st.write(f"Celkový čas: {duration:.2f} s")
    
    if st.button("Nový test"):
        st.session_state.end_time = None
        st.session_state.picking_list = []
        st.rerun()
