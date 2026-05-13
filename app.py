import streamlit as st
import random
import time

# Nastavenie stránky
st.set_page_config(page_title="Pick Test - Timer Pro", page_icon="⏱️")

# Inicializácia pamäte (session state)
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
        # LOGIKA ČASOVAČA: Spustí sa pri prvom správnom skene
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        
        st.session_state.current_index += 1
        st.session_state.last_error = ""
        
        # Kontrola konca testu
        if st.session_state.current_index >= len(st.session_state.picking_list):
            st.session_state.end_time = time.time()
            st.session_state.test_active = False
    else:
        st.session_state.last_error = f"❌ Nesprávny EAN! (Očakávaný: {current_item['ean']})"
    
    # Automatické vymazanie poľa pre ďalší sken
    st.session_state.scanner_input = ""

st.title("⏱️ Pick Test (Štart prvým skenom)")

# --- 1. OBRAZOVKA: NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    st.info("Stopky začnú bežať až po naskenovaní prvého správneho kusu.")
    data_input = st.text_area("Vložiť dáta (Formát: Kód, EAN, Počet)", 
                             placeholder="PRODUKT_A, 123456, 5", height=150)
    
    if st.button("Pripraviť test", use_container_width=True):
        if data_input:
            temp_list = []
            for line in data_input.strip().split('\n'):
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        code = parts[0].strip()
                        ean = parts[1].strip()
                        qty = int(parts[2].strip())
                        for _ in range(qty):
                            temp_list.append({"code": code, "ean": ean})
                    except:
                        continue
            
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

# --- 2. OBRAZOVKA: SAMOTNÝ TEST ---
elif st.session_state.test_active:
    idx = st.session_state.current_index
    total = len(st.session_state.picking_list)
    item = st.session_state.picking_list[idx]
    
    # Horná lišta s informáciami
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Položka: **{idx + 1} / {total}**")
    with col2:
        if st.session_state.start_time is None:
            st.warning("⏳ Čakám na 1. sken")
        else:
            elapsed = time.time() - st.session_state.start_time
            st.success(f"⏱️ Čas: {elapsed:.0f} s")

    st.progress(idx / total)

    # Hlavná karta produktu
    st.markdown(f"""
    <div style="background-color:#F0F2F6; padding:30px; border-radius:15px; text-align:center; border: 2px solid #007BFF;">
        <div style="font-size: 1.2em; color: #555;">NASKENUJE PRODUKT:</div>
        <div style="font-size: 3.5em; font-weight: bold; color: #007BFF;">{item['code']}</div>
        <div style="font-size: 1.5em; margin-top:10px; color: #333;">Očakávaný EAN: <code>{item['ean']}</code></div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    
    # Skenovacie pole
    st.text_input("Sem skenuj EAN", key="scanner_input", on_change=check_scan)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.button("Zrušiť test"):
        st.session_state.test_active = False
        st.rerun()

# --- 3. OBRAZOVKA: VÝSLEDKY ---
elif st.session_state.end_time is not None:
    duration = st.session_state.end_time - st.session_state.start_time
    total_items = len(st.session_state.picking_list)
    
    st.balloons()
    st.success("✅ Test dokončený!")
    
    c1, c2 = st.columns(2)
    c1.metric("Čistý čas (medzi skenmi)", f"{duration:.2f} s")
    c2.metric("Priemer na jeden kus", f"{duration/total_items:.2f} s")
    
    if st.button("Začať nový test", use_container_width=True):
        st.session_state.end_time = None
        st.session_state.picking_list = []
        st.rerun()
