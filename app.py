import streamlit as st
import random
import time

# Nastavenie stránky
st.set_page_config(page_title="Alza Pick Test Pro", page_icon="📦", layout="centered")

def get_image_url(code_or_url):
    val = str(code_or_url).strip()
    if val.startswith("http"):
        return val
    return f"https://image.alza.cz/products/{val}/{val}.jpg?width=500&height=500"

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

st.title("📦 Random pick GEN")

# --- 1. NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    data_input = st.text_area("Vlož dáta (Kód, EAN, Počet)", placeholder="SGR_AD_C351CB, 8595691027976, 2", height=150)
    if st.button("🚀 ŠTART", use_container_width=True):
        if data_input:
            temp_list = []
            for line in data_input.strip().split('\n'):
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        code, ean, qty = parts[0].strip(), parts[1].strip(), int(parts[2].strip())
                        for _ in range(qty):
                            temp_list.append({"code": code, "ean": ean})
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

# --- 2. TEST (AKTÍVNE PICKOVANIE) ---
elif st.session_state.test_active:
    idx = st.session_state.current_index
    total = len(st.session_state.picking_list)
    item = st.session_state.picking_list[idx]
    
    # Horná lišta
    c1, c2 = st.columns([2, 1])
    c1.write(f"Položka: **{idx + 1} / {total}**")
    with c2:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.write(f"⏱️ **{elapsed:.0f} s**")
        else:
            st.warning("Čakám na 1. sken")

    st.progress(idx / total)

    # Vycentrovaný obrázok
    st.write("") 
    col_left, col_mid, col_right = st.columns([1, 2, 1])
    with col_mid:
        url = get_image_url(item['code'])
        st.image(url, use_container_width=True)

    # Vycentrovaný text
    st.markdown(f"""
        <div style="text-align: center;">
            <h1 style="color: #3498db; margin-top: 0px; font-size: 2.5em;">{item['code']}</h1>
            <p style="font-size: 1.2em; opacity: 0.8; margin-bottom: 20px;">EAN: {item['ean']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Skenovacie pole
    st.text_input("Naskenuj EAN", key="scanner_input", on_change=check_scan, placeholder="Sem skenuj...")

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    # TLAČIDLO NA ZRUŠENIE (Vráti na začiatok)
    st.write("---")
    if st.button("❌ Zrušiť test", use_container_width=True):
        st.session_state.update({
            'test_active': False,
            'picking_list': [],
            'start_time': None,
            'end_time': None
        })
        st.rerun()

# --- 3. VÝSLEDKY ---
elif st.session_state.end_time is not None:
    duration = st.session_state.end_time - st.session_state.start_time
    total_items = len(st.session_state.picking_list)
    st.balloons()
    st.success("✅ Test dokončený!")
    
    col_res1, col_res2 = st.columns(2)
    col_res1.metric("Celkový čas", f"{duration:.1f} s")
    col_res2.metric("Priemer na kus", f"{duration/total_items:.2f} s")
    
    if st.button("Nový test", use_container_width=True):
        st.session_state.end_time = None
        st.rerun()
