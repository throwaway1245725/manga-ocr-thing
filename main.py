import json
from pathlib import Path
from typing import List

import requests
from cutlet import Cutlet
from googletrans import Translator
from manga_ocr import MangaOcr

mocr = MangaOcr()
google_translator = Translator()
katsu = Cutlet()
manga_dir = Path(
    "J:/Misc/Nexus 5/.aux/Qualcomm/Roaming/Wireless/ffff/u/ohboy/manga/[Fuzui] Lethal Succubus (2D Comic Magazine Mesugaki Henshin Heroine Seisai Wakarase-bou ni wa Katemasen deshita! Vol 2) [Digital]"
)
raws_dir = manga_dir / "raw"
raw_pages = list(raws_dir.iterdir())


def deepl_translate(text: str) -> List[str]:
    req_json = {
        "jsonrpc": "2.0",
        "method": "LMT_handle_jobs",
        "params": {
            "jobs": [
                {
                    "kind": "default",
                    "sentences": [{"text": text, "id": 0, "prefix": ""}],
                    "raw_en_context_before": [],
                    "raw_en_context_after": [],
                    "preferred_num_beams": 4,
                    "quality": "fast",
                }
            ],
            "lang": {
                "source_lang_user_selected": "JA",
                "target_lang": "EN",
            },
            "priority": -1,
            "commonJobParams": {
                "regionalVariant": "en-US",
                "mode": "translate",
                "browserType": 1,
                "formality": None,
            },
            "timestamp": 1673734578790,
        },
        "id": 83150005,
    }
    data = requests.post(
        f"https://www2.deepl.com/jsonrpc?method=LMT_handle_jobs", json=req_json
    )
    translations = data.json()["result"]["translations"]
    beams = [beam for translation in translations for beam in translation["beams"]]
    sentences = [sentence for beam in beams for sentence in beam["sentences"]]
    texts = [sentence["text"] for sentence in sentences]
    return texts


def get_dir_or_create(path: Path) -> Path:
    if not path.exists():
        path.mkdir()
    return path


page_dirs = [get_dir_or_create(manga_dir / raw_page.stem) for raw_page in raw_pages]

for page_dir in page_dirs:
    for section in page_dir.iterdir():
        if section.suffix == ".png":
            out = section.parent / f"{section.stem}.json"
            with out.open("w", encoding="utf8") as f:
                raw_text = mocr(str(section))
                google_result = google_translator.translate(
                    raw_text, src="ja", dest="en"
                )
                deepl_result = deepl_translate(raw_text)
                cutlet_result = katsu.romaji(raw_text)
                data = {
                    "raw": raw_text,
                    "google romaji": google_result.extra_data["origin_pronunciation"],
                    "google trans": google_result.text,
                    "deepl trans": deepl_result,
                    "cutlet romaji": cutlet_result,
                }
                json.dump(data, f, ensure_ascii=False, indent=2)

print("done!")
