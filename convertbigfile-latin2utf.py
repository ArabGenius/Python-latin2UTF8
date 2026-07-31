import os


def fix_line_encoding(line):
    # 1. Standardize SQL dump charset statements to utf8mb4
    line = line.replace(
        "DEFAULT CHARSET=utf8mb4", "DEFAULT CHARSET=utf8mb4"
    )
    line = line.replace("CHARSET=latin1", "CHARSET=utf8mb4")
    line = line.replace(
        "COLLATE=latin1_swedish_ci", "COLLATE=utf8mb4_unicode_ci"
    )
    line = line.replace("SET NAMES latin1", "SET NAMES utf8mb4")

    # 2. Re-encode corrupt Mojibake text: latin1 -> cp1256
    try:
        return line.encode("latin1").decode("cp1256")
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback character-by-character conversion if a line has mixed characters
        cleaned_chars = []
        for char in line:
            try:
                cleaned_chars.append(char.encode("latin1").decode("cp1256"))
            except Exception:
                cleaned_chars.append(char)
        return "".join(cleaned_chars)


def convert_large_sql(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} does not exist.")
        return

    print(f"Processing large file: {input_file}")

    lines_processed = 0
    # Stream line by line to keep RAM usage negligible (under ~50MB)
    with (
        open(input_file, "r", encoding="utf-8", errors="ignore") as infile,
        open(
            output_file, "w", encoding="utf-8", buffering=1024 * 1024
        ) as outfile,
    ):
        for line in infile:
            fixed = fix_line_encoding(line)
            outfile.write(fixed)

            lines_processed += 1
            if lines_processed % 100000 == 0:
                print(f"Processed {lines_processed:,} lines...", end="\r")

    print(f"\nDone! Saved to: {output_file}")


if __name__ == "__main__":
    # Change file paths as needed
    convert_large_sql("iraqcent_montada.sql", "iraqcent_montada-bigfile.sql")