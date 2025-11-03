from pathlib import Path
from zipfile import ZipFile
from bs4 import BeautifulSoup

# Paths
out_dir = Path("/mnt/data/dhakaak_site")
tips_path = out_dir / "tips.html"
zip_path_v2 = Path("/mnt/data/dhakaak_site_v2.zip")

new_iframe_section = """
<h3>ملف توضيحي</h3>
<p class="small">يمكنك تصفح ملف "أنواع الذكاء" داخل الموقع دون الحاجة لتنزيله.</p>
<iframe src="types.pdf" style="width:100%;height:480px;border:1px solid #ccc;border-radius:8px;"></iframe>
<div style="text-align:center; margin-top:15px;">
  <a href="types.pdf" target="_blank"
     style="background-color:#3aa0d8; color:white; padding:10px 20px; border-radius:6px; text-decoration:none;">
     فتح الملف في صفحة مستقلة
  </a>
</div>
"""

def replace_demo_section(html_text: str) -> str:
    soup = BeautifulSoup(html_text, "html.parser")

    # Find an <h3> that contains the Arabic title (loose match)
    h3 = soup.find(lambda tag: tag.name == "h3" and "ملف توضيحي" in tag.get_text())

    if not h3:
        # nothing to replace
        return html_text

    # Collect nodes from the <h3> up to and including a following <iframe src="types.pdf"> (if present).
    nodes = [h3]
    ptr = h3.next_sibling
    found_iframe = False
    while ptr is not None:
        # Skip pure-string siblings that are just whitespace/newlines if desired
        nodes.append(ptr)
        # If this sibling is an iframe element and its src contains types.pdf, include it and stop
        if getattr(ptr, "name", None) == "iframe" and "types.pdf" in (ptr.get("src") or ""):
            found_iframe = True
            break
        ptr = ptr.next_sibling

    # Determine insertion reference (the sibling after the last removed node)
    insertion_ref = nodes[-1].next_sibling if nodes else None
    parent = h3.parent

    # Remove collected nodes
    for n in nodes:
        try:
            n.extract()
        except Exception:
            pass

    # Parse the replacement fragment and insert it at the previous location
    fragment = BeautifulSoup(new_iframe_section, "html.parser")
    if insertion_ref:
        for element in fragment.contents:
            insertion_ref.insert_before(element)
    else:
        # append at end of parent if there is no reference
        for element in fragment.contents:
            parent.append(element)

    return str(soup)

def main():
    if not tips_path.exists():
        print(f"tips.html not found at {tips_path}")
        return

    content = tips_path.read_text(encoding="utf-8")
    updated = replace_demo_section(content)
    tips_path.write_text(updated, encoding="utf-8")
    print(f"Updated {tips_path}")

    # Recreate updated zip (only files, skip directories)
    with ZipFile(zip_path_v2, "w") as z:
        for p in out_dir.rglob("*"):
            if p.is_file():
                z.write(p, arcname=p.relative_to(out_dir))
    print(f"Created zip: {zip_path_v2}")

if __name__ == "__main__":
    main()