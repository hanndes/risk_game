import re
from PyQt6.QtGui import QPainterPath

def svg_d_to_qpath(d_string):
    path = QPainterPath() # bos bir cizim sayfasi actik

    # burasi metnin icindeki harfleri ve sayilari ayikliyor
    tokens = re.findall(r'([MmLlCcSsZz])|(-?\d*\.?\d+)', d_string)

    current_cmd = None # su an hangi harfteyiz onu aklimizda tutuyoruz
    points = [] # sayilari buraya doldurup doldurup kullanicaz

    for cmd, val in tokens:
        if cmd: # eger gelen sey harfse buraya giriyor
            current_cmd = cmd # yeni komutu hafizaya aldik
            points = [] # yeni harfe gectigimiz icin sayilari sifirladik
            if cmd in ('Z', 'z'): # eger z harfiyse cizimi kapat basladigin yere don demek
                path.closeSubpath()
            continue # harf isini hallettik simdi siradaki sayiya geciyoruz

        points.append(float(val)) # gelen sayiyi listeye ekle

        # eger komut m ise ve elimizde 2 tane sayi biriktiyse kalemi o koordinata gotur
        if current_cmd in ('M', 'm') and len(points) == 2:
            path.moveTo(points[0], points[1])

        # eger l harfindeysek ve 2 sayi varsa oraya duz bir cizgi cek
        elif current_cmd in ('L', 'l') and len(points) == 2:
            path.lineTo(points[0], points[1])

        # c harfi kavisli egri demek bunun icin 6 tane sayi lazim 6 sayi dolunca egriyi ciziyoruz
        elif current_cmd in ('C', 'c') and len(points) == 6:
            path.cubicTo(points[0], points[1], points[2], points[3], points[4], points[5])
            points = [] # isi biten sayilari temizle ki yenileri gelsin

    return path