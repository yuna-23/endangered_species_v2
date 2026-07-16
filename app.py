from pathlib import Path

import pandas as pd
import pydeck as pdk
import streamlit as st


# =========================================================
# 파일 경로 설정
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

EXCEL_FILE = (
    BASE_DIR
    / "data"
    / "멸종위기 야생생물 등급별 종 목록.xlsx"
)

CSV_FILE = (
    BASE_DIR
    / "data"
    / "서울시종합생태정보.csv"
)

ICON_FILE = (
    BASE_DIR
    / "images"
    / "redlist.jpg"
)


# =========================================================
# Streamlit 페이지 설정
# =========================================================

st.set_page_config(
    page_title="멸종위기 야생생물 도감",
    page_icon=str(ICON_FILE) if ICON_FILE.exists() else "🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 화면 디자인
# =========================================================

st.markdown(
    """
    <style>
    img {
        max-height: 320px;
        object-fit: contain;
    }

    [data-testid="StyledFullScreenButton"] {
        visibility: hidden;
    }

    [data-testid="stImage"] img {
        border-radius: 10px;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 데이터 불러오기
# =========================================================

@st.cache_data
def load_species_data(file_path: Path) -> pd.DataFrame:
    """
    멸종위기 야생생물 등급별 목록을 불러옵니다.
    """
    return pd.read_excel(
        file_path,
        engine="openpyxl",
    )


@st.cache_data
def load_habitat_data(file_path: Path) -> pd.DataFrame:
    """
    서울시 종합생태정보 CSV 파일을 불러옵니다.

    파일 인코딩이 다를 수 있으므로
    CP949, UTF-8-SIG, UTF-8 순서로 확인합니다.
    """
    encodings = [
        "cp949",
        "utf-8-sig",
        "utf-8",
    ]

    last_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(
                file_path,
                encoding=encoding,
            )
        except UnicodeDecodeError as error:
            last_error = error

    raise ValueError(
        "CSV 파일의 문자 인코딩을 확인할 수 없습니다."
    ) from last_error


def confirm_file_exists(
    file_path: Path,
    file_name: str,
) -> bool:
    """
    필요한 데이터 파일이 있는지 확인합니다.
    """
    if file_path.exists():
        return True

    st.error(
        f"데이터 파일을 찾을 수 없습니다: `{file_name}`"
    )

    st.info(
        "GitHub 저장소의 data 폴더와 "
        "파일 이름을 확인해 주세요."
    )

    return False


# =========================================================
# 사이드바
# =========================================================

st.sidebar.title(
    "멸종위기 야생생물 도감"
)

st.sidebar.caption(
    "순서대로 활동해 보세요."
)

activity = st.sidebar.selectbox(
    "활동 선택",
    [
        "1. 멸종위기 야생생물 알아보기",
        "2. 멸종위기 야생생물 서식지",
        "3. 멸종위기 야생생물 도감 만들기",
    ],
    label_visibility="collapsed",
)


# =========================================================
# 활동 1
# 멸종위기 야생생물 알아보기
# =========================================================

if activity == "1. 멸종위기 야생생물 알아보기":

    st.title(
        "🐾 멸종위기 야생생물 알아보기 🌱"
    )

    st.markdown(
        """
        멸종위기 야생생물이 무엇인지 알아보고,  
        등급별로 어떤 생물들이 지정되어 있는지
        살펴보세요.
        """
    )

    st.video(
        "https://youtu.be/EEvBV8mBG9o"
    )

    if confirm_file_exists(
        EXCEL_FILE,
        "멸종위기 야생생물 등급별 종 목록.xlsx",
    ):
        try:
            species_data = load_species_data(
                EXCEL_FILE
            )

            # 열 이름 앞뒤의 공백 제거
            species_data.columns = (
                species_data.columns
                .astype(str)
                .str.strip()
            )

            required_columns = {
                "분류군",
                "등급",
                "국명",
                "학명",
            }

            missing_columns = (
                required_columns
                - set(species_data.columns)
            )

            if missing_columns:
                st.error(
                    "엑셀 파일에 필요한 열이 없습니다."
                )

                st.write(
                    "누락된 열:",
                    ", ".join(
                        sorted(missing_columns)
                    ),
                )

                st.write(
                    "현재 열 이름:",
                    list(species_data.columns),
                )

            else:
                grade = st.selectbox(
                    "등급을 선택하세요.",
                    [
                        "Ⅰ",
                        "Ⅱ",
                    ],
                )

                show_button = st.button(
                    "알아보기",
                    type="primary",
                    width="stretch",
                )

                if show_button:
                    grade_values = (
                        species_data["등급"]
                        .astype(str)
                        .str.strip()
                    )

                    filtered_data = species_data[
                        grade_values == grade
                    ].copy()

                    if filtered_data.empty:
                        st.warning(
                            f"등급 {grade}에 해당하는 "
                            "데이터가 없습니다."
                        )

                        st.info(
                            "엑셀의 등급이 로마 숫자 "
                            "Ⅰ, Ⅱ로 입력되어 있는지 "
                            "확인해 주세요."
                        )

                    else:
                        st.dataframe(
                            filtered_data[
                                [
                                    "분류군",
                                    "등급",
                                    "국명",
                                    "학명",
                                ]
                            ],
                            hide_index=True,
                            width="stretch",
                        )

                        st.success(
                            f"등급 {grade}에 해당하는 "
                            f"생물 {len(filtered_data)}종을 "
                            "찾았습니다."
                        )

        except Exception as error:
            st.error(
                "엑셀 파일을 불러오는 중 "
                "오류가 발생했습니다."
            )

            st.exception(error)


# =========================================================
# 활동 2
# 멸종위기 야생생물 서식지
# =========================================================

elif activity == "2. 멸종위기 야생생물 서식지":

    st.title(
        "📍 멸종위기 야생생물 서식지"
    )

    st.markdown(
        """
        **멸종위기 야생생물의 서식지**를 살펴보고,  
        서식 환경과 동식물의 생활이
        어떤 관련이 있는지 탐구해 보세요.
        """
    )

    if confirm_file_exists(
        CSV_FILE,
        "서울시종합생태정보.csv",
    ):
        try:
            habitat_data = load_habitat_data(
                CSV_FILE
            )

            # CSV 열 이름의 앞뒤 공백 제거
            habitat_data.columns = (
                habitat_data.columns
                .astype(str)
                .str.strip()
            )

            required_columns = {
                "위도",
                "경도",
                "보호구역 대상지",
                "보호구역 대분류",
                "보호구역 소분류",
            }

            missing_columns = (
                required_columns
                - set(habitat_data.columns)
            )

            if missing_columns:
                st.error(
                    "CSV 파일에 필요한 열이 없습니다."
                )

                st.write(
                    "누락된 열:",
                    ", ".join(
                        sorted(missing_columns)
                    ),
                )

                st.write(
                    "현재 열 이름:",
                    list(habitat_data.columns),
                )

            else:
                habitat_data["위도"] = pd.to_numeric(
                    habitat_data["위도"],
                    errors="coerce",
                )

                habitat_data["경도"] = pd.to_numeric(
                    habitat_data["경도"],
                    errors="coerce",
                )

                habitat_data = habitat_data.dropna(
                    subset=[
                        "위도",
                        "경도",
                    ]
                ).copy()

                map_data = pd.DataFrame(
                    {
                        "lat": habitat_data["위도"],
                        "lon": habitat_data["경도"],
                        "대상지": habitat_data[
                            "보호구역 대상지"
                        ].fillna("정보 없음"),
                        "대분류": habitat_data[
                            "보호구역 대분류"
                        ].fillna("정보 없음"),
                        "소분류": habitat_data[
                            "보호구역 소분류"
                        ].fillna("정보 없음"),
                    }
                )

                if map_data.empty:
                    st.warning(
                        "지도에 표시할 수 있는 "
                        "위도와 경도 데이터가 없습니다."
                    )

                else:
                    scatter_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=map_data,
                        get_position="[lon, lat]",
                        get_radius=100,
                        get_fill_color=[
                            180,
                            0,
                            200,
                            150,
                        ],
                        pickable=True,
                        auto_highlight=True,
                    )

                    view_state = pdk.ViewState(
                        latitude=float(
                            map_data["lat"].mean()
                        ),
                        longitude=float(
                            map_data["lon"].mean()
                        ),
                        zoom=10,
                        min_zoom=5,
                        max_zoom=16,
                        pitch=35,
                        bearing=0,
                    )

                    deck = pdk.Deck(
                        layers=[
                            scatter_layer
                        ],
                        initial_view_state=view_state,
                        tooltip={
                            "html": (
                                "<b>대상지</b>: {대상지}"
                                "<br/>"
                                "<b>대분류</b>: {대분류}"
                                "<br/>"
                                "<b>소분류</b>: {소분류}"
                            ),
                            "style": {
                                "backgroundColor":
                                    "steelblue",
                                "color":
                                    "white",
                            },
                        },
                    )

                    st.pydeck_chart(
                        deck,
                        width="stretch",
                    )

                    st.caption(
                        f"지도에 표시된 서식지 정보: "
                        f"{len(map_data)}개"
                    )

                with st.form(
                    "habitat_form"
                ):
                    answer = st.text_area(
                        (
                            "데이터를 통해 알게 된 "
                            "서식지와 동식물의 생활에 "
                            "관한 특징을 적어 보세요."
                        ),
                        placeholder=(
                            "예: 물이 풍부한 지역에는 "
                            "습지 식물과 수생 생물이 "
                            "많이 살아갑니다."
                        ),
                        height=150,
                    )

                    submitted = (
                        st.form_submit_button(
                            "제출",
                            type="primary",
                            width="stretch",
                        )
                    )

                    if submitted:
                        if answer.strip():
                            st.success(
                                "제출되었습니다."
                            )
                        else:
                            st.warning(
                                "내용을 먼저 작성해 주세요."
                            )

        except Exception as error:
            st.error(
                "서식지 데이터를 불러오는 중 "
                "오류가 발생했습니다."
            )

            st.exception(error)


# =========================================================
# 활동 3
# 멸종위기 야생생물 도감 만들기
# =========================================================

else:

    st.title(
        "📝 멸종위기 야생생물 도감 만들기"
    )

    st.markdown(
        """
        **멸종위기 야생생물**을 하나씩 추가하여  
        우리 반의 멸종위기 야생생물 도감을
        완성해 보세요.
        """
    )

    type_emoji = {
        "동물": "🐾",
        "식물": "🌱",
    }

    initial_species = [
        {
            "name": "자이언트 판다",
            "types": [
                "동물"
            ],
            "image_url": (
                "https://i.namu.wiki/i/"
                "ZcoHpRfcLvVyW2Dhs58vHkd-"
                "CfPTdZe4bbi9bm3E30Mvnwe71h_"
                "fPkD5T3JUlmToxtlL3udpL8ijyyl"
                "KIY8KIefEnB_vTN4KXKhwY4t-"
                "HcO6I4psnFkK5S9HadBu3ZRl2Ki"
                "92SlAv55YKkS3s6KXmQ.webp"
            ),
        },
        {
            "name": "북극여우",
            "types": [
                "동물"
            ],
            "image_url": (
                "https://i.namu.wiki/i/"
                "mua5eqLLT8P0ueiN8juGyEqq7XJ-"
                "pj7NFqWzXCKW-qxQYgqE5F2Ohq3"
                "IgmW1PLP2x1Xl4g4jHiU26P7vPJ"
                "p8ykxQhLtL9-DEdAXRVzMAWOwp7E"
                "l1stsB5U3vS9J9rozCzajxEC9FnR"
                "NzPVmIgYvZbw.webp"
            ),
        },
        {
            "name": "검은별고사리",
            "types": [
                "식물"
            ],
            "image_url": (
                "https://t1.daumcdn.net/"
                "thumb/R760x0/"
                "?fname=http%3A%2F%2F"
                "t1.daumcdn.net%2Fencyclop"
                "%2Fm174%2FFFX4Or7uPdIxaqGE"
                "jtUodhG4h7fEVo3hLyQ9Wfha"
                "%3Ft%3D1471587036000"
            ),
        },
    ]

    example_species = {
        "name": "날개하늘나리",
        "types": [
            "식물"
        ],
        "image_url": (
            "https://t1.daumcdn.net/"
            "thumb/R0x640/"
            "?fname=http%3A%2F%2F"
            "t1.daumcdn.net%2Fencyclop"
            "%2Fm174%2F7JWYv3bEPYnUeqV"
            "WWM8ewnbGoxKeiimioDkd1fQ4"
            "%3Ft%3D1471586354000"
        ),
    }

    if "species_cards" not in st.session_state:
        st.session_state.species_cards = [
            item.copy()
            for item in initial_species
        ]

    auto_complete = st.toggle(
        "예시 데이터로 채우기"
    )

    with st.form(
        "species_form",
        clear_on_submit=False,
    ):
        col1, col2 = st.columns(2)

        with col1:
            species_name = st.text_input(
                "멸종위기 야생생물 이름",
                value=(
                    example_species["name"]
                    if auto_complete
                    else ""
                ),
            )

        with col2:
            species_types = st.multiselect(
                "멸종위기 야생생물 종류",
                options=list(
                    type_emoji.keys()
                ),
                max_selections=1,
                default=(
                    example_species["types"]
                    if auto_complete
                    else []
                ),
            )

        image_url = st.text_input(
            "멸종위기 야생생물 이미지 URL",
            value=(
                example_species["image_url"]
                if auto_complete
                else ""
            ),
        )

        add_species = (
            st.form_submit_button(
                "도감에 추가",
                type="primary",
                width="stretch",
            )
        )

        if add_species:
            if not species_name.strip():
                st.error(
                    "멸종위기 야생생물의 "
                    "이름을 입력해 주세요."
                )

            elif not species_types:
                st.error(
                    "멸종위기 야생생물의 "
                    "종류를 선택해 주세요."
                )

            else:
                st.session_state.species_cards.append(
                    {
                        "name":
                            species_name.strip(),
                        "types":
                            species_types,
                        "image_url":
                            image_url.strip(),
                    }
                )

                st.success(
                    f"'{species_name.strip()}'을 "
                    "도감에 추가했습니다."
                )

    st.divider()

    species_cards = (
        st.session_state.species_cards
    )

    for row_start in range(
        0,
        len(species_cards),
        3,
    ):
        row_species = species_cards[
            row_start : row_start + 3
        ]

        columns = st.columns(3)

        for column_number, species in enumerate(
            row_species
        ):
            actual_index = (
                row_start + column_number
            )

            with columns[column_number]:
                with st.container(
                    border=True
                ):
                    st.subheader(
                        f"{actual_index + 1}. "
                        f"{species['name']}"
                    )

                    image_source = (
                        species
                        .get(
                            "image_url",
                            "",
                        )
                        .strip()
                    )

                    if image_source:
                        try:
                            st.image(
                                image_source,
                                width="stretch",
                            )
                        except Exception:
                            st.warning(
                                "이미지를 불러오지 "
                                "못했습니다."
                            )
                    else:
                        st.info(
                            "등록된 이미지가 없습니다."
                        )

                    species_type_text = [
                        (
                            f"{type_emoji[item]} "
                            f"{item}"
                        )
                        for item
                        in species["types"]
                    ]

                    st.write(
                        " / ".join(
                            species_type_text
                        )
                    )

                    delete_button = st.button(
                        "삭제",
                        key=(
                            f"delete_"
                            f"{actual_index}"
                        ),
                        width="stretch",
                    )

                    if delete_button:
                        del (
                            st.session_state
                            .species_cards[
                                actual_index
                            ]
                        )

                        st.rerun()

    reset_button = st.button(
        "처음 상태로 되돌리기",
        width="stretch",
    )

    if reset_button:
        st.session_state.species_cards = [
            item.copy()
            for item in initial_species
        ]

        st.rerun()
