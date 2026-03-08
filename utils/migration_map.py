import folium
import streamlit as st

PLACE_COORDS = {
    "湖北": (30.6, 114.3),
    "湖南": (28.2, 112.9),
    "江西": (28.7, 115.9),
    "福建": (26.1, 119.3),
    "广东": (23.1, 113.3),
    "广西": (22.8, 108.3),
    "贵州": (26.6, 106.7),
    "四川": (30.7, 104.1),
    "重庆": (29.6, 106.5),
    "湖广": (29.4, 112.5),
    "成都": (30.7, 104.1)
}


def draw_migration_map(text: str):
    places = []

    for place in PLACE_COORDS.keys():
        if place in text and place not in places:
            places.append(place)

    if not places:
        st.warning("未识别到可绘制的迁徙地点。")
        return

    coords = [PLACE_COORDS[p] for p in places]

    m = folium.Map(location=coords[0], zoom_start=5)

    for place in places:
        lat, lng = PLACE_COORDS[place]
        folium.Marker([lat, lng], popup=place).add_to(m)

    if len(coords) >= 2:
        folium.PolyLine(coords, weight=4, opacity=0.8).add_to(m)

    st.components.v1.html(m._repr_html_(), height=620, scrolling=True)
