import streamlit as st
import random
import time[4][5]

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
        # --- LOGIKA ČASOVAČA ---
        # Ak je toto úplne prvý naskenovaný kus, odteraz začíname merať čas
        if st.session_state.start_time is None:
            st.session_state.start_time = time.time()
        
        st.session_state.current_index += 1
        st.session_state.last_error = ""
        
        # Ak sme naskenovali všetko
        if st.session_state.current_index >= len(st.session_state.picking_list):
            st.session_state.end_time = time.time()
            st.session_state.test_active = False
    else:
        st.session_state.last_error = f"❌ Nesprávny EAN! (Očakávaný: {current_item['ean']})"
    
    # Vymazanie inputu pre ďalší sken
    st.session_state.scanner_input = ""

st.title("⏱️ Pick Test s odloženým štartom")

# --- 1. NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    st.info("Stopky sa spustia až po naskenovaní prvého kusu.")
    data_input = st.text_area("Vložiť dáta (Kód, EAN, Počet)", 
                             placeholder="PRODUKT_A, 123456, 5", height=150)
    
    if st.button("Pripraviť test", use_container_width=True):
        if data_input:
            temp_list = []
            for line in data_input.strip().split('\n'):
                parts = line.split(',')
                if len(parts) >= 3:
                    code, ean, qty = parts[0].strip(), parts[1].strip(), int(parts[2].strip())
                    for _ in range(qty):
                        temp_list.append({"code": code, "ean": ean})
            
            if temp_list:
                random.shuffle(temp_list)
                st.session_state.update({
                    'picking_list': temp_list,
                    'current_index': 0,
                    'test_active': True,
                    'start_time': None, # Čas sa nastaví až pri skene
                    'end_time': None,
                    'last_error': ""
                })
                st.rerun()

# --- 2. SAMOTNÝ TEST ---
elif st.session_state.test_active:
    idx = st.session_state.current_index
    total = len(st.session_state.picking_list)
    item = st.session_state.picking_list[idx]
    
    # Stavový riadok
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Položka: **{idx + 1} / {total}**")
    with col2:
        if st.session_state.start_time is None:
            st.warning("⏳ Čakám na 1. sken")
        else:
            elapsed = time.time() - st.session_state.start_time
            st.success(f"⏱️ Čas beží: {elapsed:.0f} s")[6][5][7]

    st.progress(idx / total)

    # Vizitka produktu
    st.markdown(f"""
    <div style="background-color:#F0F2F6; padding:30px; border-radius:15px; text-align:center; border: 2px solid #007BFF;">
        <div style="font-size: 1.2em; color: #555;">OBERTE PRODUKT:</div>
        <div style="font-size: 3em; font-weight: bold; color: #007BFF;">{item['code']}</div>
        <div style="font-size: 1.5em; margin-top:10px;">EAN: <code>{item['ean']}</code></div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    
    # Skenovacie pole
    st.text_input("Naskenuj EAN", key="scanner_input", on_change=check_scan)

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.button("Zrušiť"):
        st.session_state.test_active = False
        st.rerun()

# --- 3. VÝSLEDKY ---
elif st.session_state.end_time is not None:
    # Ak bol naskenovaný len 1 kus celkovo, čas bude 0 (lebo štart a koniec bol ten istý sken)
    # Preto pri výpočte počítame s časom od 1.[4] do posledného skenu
    duration = st.session_state.end_time - st.session_state.start_time
    total_items = len(st.session_state.picking_list)
    
    st.balloons()
    st.success("✅ Test úspešne dokončený!")
    
    c1, c2 = st.columns(2)
    c1.metric("Čas (od 1. skenu)", f"{duration:.2f} s")
    # Priemer počítame na (n-1) medzier medzi skenmi, alebo na celok, podľa logiky
    c2.metric("Priemer na kus", f"{duration/total_items:.2f} s")
    
    st.info(f"Namerané od prvého po posledný (celkovo {total_items} ks).")
    
    if st.button("Nový test", use_container_width=True):
        st.session_state.end_time = None
        st.rerun()
