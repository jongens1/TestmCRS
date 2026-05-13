import streamlit as st
import random
import time

# Nastavenie stránky pre mobilné zobrazenie
st.set_page_config(page_title="Pick Test - Scanner Only", page_icon="🎯")

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

# Funkcia, ktorá spracuje naskenovaný kód
def check_scan():
    # Získame hodnotu z inputu (používame kľúč 'scanner_input')
    scanned_ean = st.session_state.scanner_input.strip()
    
    if not scanned_ean:
        return

    current_item = st.session_state.picking_list[st.session_state.current_index]
    
    if scanned_ean == current_item['ean']:
        # Úspešný sken
        st.session_state.current_index += 1
        st.session_state.last_error = ""
        # Ak sme na konci, ukonči test
        if st.session_state.current_index >= len(st.session_state.picking_list):
            st.session_state.end_time = time.time()
            st.session_state.test_active = False
    else:
        # Chyba pri skenovaní
        st.session_state.last_error = f"❌ Zlý EAN: {scanned_ean} (Očakávaný: {current_item['ean']})"
    
    # Vymažeme input pre ďalšie skenovanie
    st.session_state.scanner_input = ""

st.title("🎯 Picking Scanner Test")

# --- 1. OBRAZOVKA: NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    st.write("Vložte dáta vo formáte: **Kód, EAN, Počet**")
    data_input = st.text_area("Zoznam produktov", 
                             placeholder="MONITOR1, 8591234, 3\nIPHONE15, 0194253, 1", 
                             height=200)
    
    if st.button("🚀 ŠTART", use_container_width=True):
        if data_input:
            lines = data_input.strip().split('\n')
            temp_list = []
            for line in lines:
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
                    'start_time': time.time(),
                    'last_error': ""
                })
                st.rerun()

# --- 2. OBRAZOVKA: TEST (SKENOVANIE) ---
elif st.session_state.test_active:
    idx = st.session_state.current_index
    total = len(st.session_state.picking_list)
    item = st.session_state.picking_list[idx]
    
    # Ukazovateľ progresu
    st.progress(idx / total)
    st.write(f"Položka {idx + 1} z {total}")

    # HLAVNÝ DISPLAY PRODUKTU
    st.markdown(f"""
    <div style="background-color:#f0f2f6; padding: 20px; border-radius: 10px; border-left: 10px solid #ff4b4b;">
        <h1 style="margin:0; color:#1f77b4;">Kód: {item['code']}</h1>
        <h3 style="margin:5px 0; color:#555;">EAN: {item['ean']}</h3>
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # SKENOVACIE POLE (Enter po skene spustí check_scan)
    st.text_input("Naskenuj EAN a stlač Enter", 
                  key="scanner_input", 
                  on_change=check_scan,
                  placeholder="Kurzor musí byť tu...")

    # Zobrazenie chyby, ak sa naskenoval zlý kód
    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.button("❌ Zrušiť test"):
        st.session_state.test_active = False
        st.rerun()

# --- 3. OBRAZOVKA: VÝSLEDKY ---
elif st.session_state.end_time is not None:
    duration = st.session_state.end_time - st.session_state.start_time
    total_items = len(st.session_state.picking_list)
    
    st.success("✅ HOTOVO!")
    
    c1, c2 = st.columns(2)
    c1.metric("Celkový čas", f"{duration:.1f} s")
    c2.metric("Priemer / kus", f"{duration/total_items:.2f} s")
    
    if st.button("🔄 Skúsiť znova", use_container_width=True):
        st.session_state.end_time = None
        st.rerun()
