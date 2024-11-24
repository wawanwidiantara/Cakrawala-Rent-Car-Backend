from doctr.models import ocr_predictor
from doctr.io import DocumentFile

# Initialize the OCR model (do this once)
model = ocr_predictor(
    det_arch="fast_small", reco_arch="crnn_mobilenet_v3_small", pretrained=True
)


class OCRTextProcessor:
    def __init__(self, tolerance=15):
        self.tolerance = tolerance

    def process_ocr_result(self, result):
        """Process OCR result and return corrected text alignments."""
        # Extract all words with their coordinates and text
        words = []
        for page in result["pages"]:
            for block in page["blocks"]:
                for line in block.get("lines", []):
                    for word in line.get("words", []):
                        # Get coordinates from geometry
                        coords = word["geometry"]
                        # Convert coordinates to more readable format
                        x1, y1 = coords[0]
                        x2, y2 = coords[1]

                        words.append(
                            {
                                "text": word["value"],
                                "coords": {
                                    "y1": float(y1),
                                    "y2": float(y2),
                                    "x1": float(x1),
                                    "x2": float(x2),
                                },
                            }
                        )

        # Sort words by y-coordinate first
        words.sort(key=lambda x: x["coords"]["y1"])

        # Group words that are on the same line
        lines = []
        current_line = [words[0]] if words else []

        for word in words[1:]:
            last_word = current_line[-1] if current_line else None

            if last_word and self._is_same_line(last_word["coords"], word["coords"]):
                current_line.append(word)
            else:
                if current_line:
                    # Sort words in the line by x-coordinate before adding to lines
                    current_line.sort(key=lambda x: x["coords"]["x1"])
                    lines.append(current_line)
                current_line = [word]

        if current_line:
            # Sort the last line by x-coordinate
            current_line.sort(key=lambda x: x["coords"]["x1"])
            lines.append(current_line)

        # Convert grouped words to text
        formatted_text = []
        for line in lines:
            line_text = " ".join(word["text"] for word in line)
            formatted_text.append(line_text)

        return formatted_text

    def _is_same_line(self, coords1, coords2, tolerance_factor=0.5):
        """
        Check if two words are on the same line based on vertical coordinates
        Using a tolerance factor relative to text height
        """
        height1 = coords1["y2"] - coords1["y1"]
        height2 = coords2["y2"] - coords2["y1"]
        avg_height = (height1 + height2) / 2

        mid1 = (coords1["y1"] + coords1["y2"]) / 2
        mid2 = (coords2["y1"] + coords2["y2"]) / 2

        return abs(mid1 - mid2) < (avg_height * tolerance_factor)


class TextEntityExtractor:
    def __init__(self):
        # Define fields with their keywords and tolerance levels
        self.fields = [
            {"name": "provinsi", "keywords": ["provinsi"], "tolerance": 2},
            {"name": "kabupaten", "keywords": ["kabupaten", "kota"], "tolerance": 2},
            {"name": "nik", "keywords": ["nik"], "tolerance": 1},
            {"name": "nama", "keywords": ["nama"], "tolerance": 1},
            {
                "name": "tempat_tgl_lahir",
                "keywords": [
                    "tempat/tgl",
                    "tempat/tgilahir",
                    "tempat",
                    "tompat/tgllah",
                ],
                "tolerance": 3,
            },
            # {'name': 'tanggal_lahir', 'keywords': ['tgl', 'tanggal'], 'tolerance': 2},
            {
                "name": "jenis_kelamin",
                "keywords": ["jenis kelamin", "kelamin"],
                "tolerance": 2,
            },
            {"name": "alamat", "keywords": ["alamat"], "tolerance": 2},
            {"name": "rt_rw", "keywords": ["rt/rw", "rtrw"], "tolerance": 2},
            {
                "name": "kel_desa",
                "keywords": ["kel/desa", "kelurahan", "desa"],
                "tolerance": 2,
            },
            {"name": "kecamatan", "keywords": ["kecamatan", "kec"], "tolerance": 3},
            {"name": "agama", "keywords": ["agama"], "tolerance": 2},
            {
                "name": "status_perkawinan",
                "keywords": ["status perkawinan", "perkawinan"],
                "tolerance": 3,
            },
            {"name": "pekerjaan", "keywords": ["pekerjaan", "kerja"], "tolerance": 3},
            {
                "name": "kewarganegaraan",
                "keywords": ["kewarganegaraan"],
                "tolerance": 4,
            },
            {
                "name": "berlaku_hingga",
                "keywords": ["berlaku hingga", "hingga"],
                "tolerance": 3,
            },
        ]

    def levenshtein_distance(self, s1, s2):
        """Calculate the Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    def find_field_match(self, line):
        """Find matching field for a line based on Levenshtein distance"""
        words = line.lower().split()
        if not words:
            return None

        best_match = None
        min_distance = float("inf")

        for field in self.fields:
            for keyword in field["keywords"]:
                keyword_parts = keyword.lower().split()

                # Try matching with first word(s) of line
                for i in range(min(len(words), len(keyword_parts) + 1)):
                    line_part = " ".join(words[: i + 1])
                    distance = self.levenshtein_distance(line_part, keyword)

                    if distance < min_distance and distance <= field["tolerance"]:
                        min_distance = distance
                        best_match = field

        return best_match

    def extract_value(self, line, field):
        """Extract value from a line based on field type"""
        # Split line into parts
        parts = line.split()

        # Find where the field name ends
        field_end = 0
        for i, part in enumerate(parts):
            for keyword in field["keywords"]:
                if (
                    self.levenshtein_distance(part.lower(), keyword.lower())
                    <= field["tolerance"]
                ):
                    field_end = i + 1
                    break

        # Extract value portion
        value = " ".join(parts[field_end:]).strip()

        # Clean up common artifacts
        value = value.replace(":", "").strip()

        return value if value else None

    def extract_entities(self, lines):
        """Extract entities from list of lines"""
        entities = {}

        for line in lines:
            # Skip empty lines
            if not line.strip():
                continue

            # Find matching field
            field = self.find_field_match(line)
            if field:
                value = self.extract_value(line, field)
                if value:
                    # Special handling for fields that might have multiple parts
                    if field["name"] in entities:
                        if isinstance(entities[field["name"]], list):
                            entities[field["name"]].append(value)
                        else:
                            entities[field["name"]] = [entities[field["name"]], value]
                    else:
                        entities[field["name"]] = value

        return entities


def preprocess_text(text):
    # Convert to uppercase
    text = text.upper()
    # Remove single characters
    text = " ".join(word for word in text.split() if len(word) > 1)
    # Remove leading and trailing spaces
    text = text.strip()
    return text


def post_processing(data):
    import re

    # 1. Update `jenis_kelamin`
    data["jenis_kelamin"] = (
        "Laki-laki" if data["jenis_kelamin"].startswith("L") else "Perempuan"
    )

    # 2. Update `agama`
    data["agama"] = data["agama"].split()[0]

    # 3. Update `status_perkawinan`
    data["status_perkawinan"] = re.sub(r"\d+", "", data["status_perkawinan"]).strip()

    return data


def extract_id_card(image_path):
    # Read image and pass it to the OCR model
    single_img_doc = DocumentFile.from_images(image_path)
    result = model(single_img_doc)
    ocr_export = result.export()

    # Process the OCR results
    processor = OCRTextProcessor()
    formatted_text = processor.process_ocr_result(ocr_export)
    processed_data = [preprocess_text(item) for item in formatted_text if item]

    # Extract entities
    extractor = TextEntityExtractor()
    entities = extractor.extract_entities(processed_data)

    # Post-process entities
    return post_processing(entities)
