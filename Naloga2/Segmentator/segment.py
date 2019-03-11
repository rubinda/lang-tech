import xml.etree.ElementTree as ET


def main():
    """
    Glavna funkcija, ki prozi zacetek segmentacije
    :return: NULL
    """
    document = ET.parse("kas-4000.text.xml")
    root = document.getroot()

    pages = [page for page in root.findall('./page')]

    for page in pages:
        print('\nNova stran')
        for elem in page.iter('p'):

            print(elem)


if __name__ == '__main__':
    main()
