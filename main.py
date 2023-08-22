import sqlite3
import xml.etree.ElementTree as ET
from xml.dom import minidom

db_connection = sqlite3.connect('data.sqlite')
cursor = db_connection.cursor()

query = """
SELECT p.product_id, pd.name AS title, pd.description, 'https://butopea.com/p/' + m.manufacturer_id AS link,
       pi.image AS image_link, GROUP_CONCAT(pi.image) AS additional_image_link,
       CASE WHEN p.quantity > 0 THEN 'in_stock' ELSE 'out_of_stock' END AS availability,
       p.price, m.name AS brand
FROM product p
JOIN product_description pd ON p.product_id = pd.product_id
LEFT JOIN product_image pi ON p.product_id = pi.product_id
JOIN manufacturer m ON p.manufacturer_id = m.manufacturer_id
WHERE p.status = '1'
GROUP BY p.product_id
"""
cursor.execute(query)
data = cursor.fetchall()

root = ET.Element("rss")
root.set("version", "2.0")
root.set("xmlns:g", "http://base.google.com/ns/1.0")

# Create the channel element
channel = ET.SubElement(root, "channel")

# Loop through the retrieved data and create XML elements for each product
for row in data:
    item = ET.SubElement(channel, "item")

    ET.SubElement(item, "id").text = str(row[0])
    ET.SubElement(item, "title").text = row[1]
    ET.SubElement(item, "description").text = row[2]
    ET.SubElement(item, "link").text = f"https://butopea.com/p/{row[3]}"
    ET.SubElement(item, "image_link").text = f"https://butopea.com/image/catalog/{row[4]}"

    additional_images = row[5].split(',') if row[5] else []
    for i, img in enumerate(additional_images, start=1):
        ET.SubElement(item, f"additional_image_link_{i}").text = f"https://butopea.com/image/catalog/{img.strip()}"

    ET.SubElement(item, "availability").text = row[6]
    ET.SubElement(item, "price").text = str(row[7]) + " HUF"
    ET.SubElement(item, "brand").text = row[8]
    ET.SubElement(item, "condition").text = "new"

# Create a nicely formatted XML string
xml_string = ET.tostring(root, encoding="unicode")
xml_pretty_string = minidom.parseString(xml_string).toprettyxml(indent="  ")

# Save the XML data to a file
with open('feed.xml', 'w',  encoding='utf-8') as xml_file:
    xml_file.write(xml_pretty_string)

db_connection.close()
