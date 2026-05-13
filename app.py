import streamlit as st
import random
import time

# Nastavenie stránky
st.set_page_config(page_title="Pick Test + Images", page_icon="🖼️")

# Pomocná funkcia na získanie URL obrázka
def get_image_url(code_or_url):
    code_or_url = str(code_or_url).strip()
    # Ak to vyzerá ako link, vráť ho priamo
    if code_or_url.startswith("http"):
        return code_or_url
    # Inak predpokladaj, že je to Alza kód a skús CDN
    return f"https://cdn.alza.cz/ImgW.ashx?fd=f3&i={code_or_url}"

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
        st.session_state.last_error = f"❌ Nesprávny EAN: {scanned_ean}"
    
    st.session_state.scanner_input = ""

st.title("🖼️ Pick Test s obrázkami")

# --- 1. NASTAVENIE ---
if not st.session_state.test_active and st.session_state.end_time is None:
    st.markdown("""
    **Formát dát:** `Kód, EAN, Počet, [URL obrázku - voliteľné]`  
    *Ak nezadáte URL, použije sa obrázok z Alza CDN podľa kódu.*
    """)
    
    data_input = st.text_area("Vložiť dáta", 
                             placeholder="RI035b1, 8594177933134, 2\nhttps://img.url, 111222, 1", 
                             height=150)
    
    if st.button("🚀 PRIPRAVIŤ TEST", use_container_width=True):
        if data_input:
            temp_list = []
            for line in data_input.strip().split('\n'):
                parts = line.split(',')
                if len(parts) >= 3:
                    try:
                        code = parts[0].strip()
                        ean = parts[1].strip()
                        qty = int(parts[2].strip())
                        # Ak je 4. stĺpec, použi ho ako zdroj obrázku, inak použi kód
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
    
    col1, col2 = st.columns(2)
    col1.write(f"Položka: **{idx + 1} / {total}**")
    with col2:
        if st.session_state.start_time is not None:
            elapsed = time.time() - st.session_state.start_time
            st.success(f"⏱️ Čas: {elapsed:.0f} s")
        else:
            st.warning("⏳ Čakám na 1. sken")

    st.progress(idx / total)

    # HLAVNÁ KARTA S OBRÁZKOM
    with st.container():
        st.markdown('<div style="border: 2px solid #ddd; border-radius: 15px; padding: 20px; background: white; text-align: center;">', unsafe_allow_html=True)
        
        # Zobrazenie obrázka
        img_url = get_image_url(item['img'])
        st.image(img_url, width=200)
        
        st.markdown(f"""
            <div style="font-size: 1.2em; color: #666; margin-top:10px;">PRODUKT:</div>
            <div style="font-size: 2.5em; font-weight: bold; color: #1f77b4;">{item['code']}</div>
            <div style="font-size: 1.2em; color: #333;">Očakávaný EAN: <code>{item['ean']}</code></div>
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
    
    c1, c2 = st.columns(2)
    c1.metric("Celkový čas", f"{duration:.2f} s")
    c2.metric("Priemer na kus", f"{duration/total_items:.2f} s")
    
    if st.button("Nový test", use_container_width=True):
        st.session_state.end_time = None
        st.session_state.picking_list = []
        st.rerun()
