from openpyxl import Workbook



rows = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

workbook = Workbook()
sheet = workbook.active
sheet['C1'] = 'World'

workbook.save('output_file.xlsx')
workbook.close()