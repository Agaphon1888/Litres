#ОТКРЫТИЕ СТРАНИЦ
 
from webbrowser import open
from time import sleep 
 
ref = 'https://www.litres.ru/pages/get_pdf_page/?file=59995600&page={0}&rt=w1900&ft={1}'
gif = (0,1,2,3,4,5,6,7,11,29,37,38,39,46,57,58,62,63,67,72,87,88,89,90,92,95,104,141,144,145,146,147,148,150,162,177,187,188,189,190,191,192,193,194,205,212,229,235,236,237,238,239,256,261,266,267,268,269,270,271,272)
 
for i in range(273):
    if i in gif:
        open(ref.format(i,'gif'), new=2)
    else:
        open(ref.format(i,'jpg'), new=2)
    if (i + 1) % 10 == 0:
        sleep(30)
